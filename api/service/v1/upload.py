import gc
import glob
import json
import os
import shutil
import tempfile
import zipfile

from botocore.exceptions import ClientError

from api import SessionLocal
from api.config import file_upload_path, s3_config, notification_config, default_host

from api.model.claim_history import ClaimClass
from api.model.insurance import InsuranceClass
from api.model.message_template import MessageTemplateClass
from api.model.notification_send_log import NotificationSendLog
from api.model.partner import PartnerClass
from api.util.helper.decorator import parameter_validation
from api.util.helper.time import currentUTCTimestamp, convertTimeToYYYYMMDDWithComma
from api.util.plugin.cipher import AESCipher
from api.util.plugin.send_notification import SendNotification
from api.util.reponse_message import response_message_handler

import logging
import boto3
import pyminizip

logger = logging.getLogger(__name__)


@parameter_validation(requires={'upload_target': str, 'claim_id': str, 'upload_flag': bool})
def upload_document(data, header):
    db = SessionLocal()

    try:

        logger.info("header : {}".format(header))
        logger.info("data : {}".format(data))

        cipher = AESCipher()
        send_notification = SendNotification(api_url=notification_config['API_URL'],
                                             user_id=notification_config['USER_ID'],
                                             profile=notification_config['PROFILE'])
        auth_token = header['Auth-Token']

        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token)

        if partner_info.count() > 0:

            partner_info_to_dict = partner_info.first().__dict__
            get_claim_info = db.query(ClaimClass).filter_by(claim_id=data['claim_id'])

            """ 1. upload target path 확인해서 s3이면 업로드, 아니면, 등록완료로만 확인"""
            if get_claim_info.count() > 0:

                claim_info = get_claim_info.first().__dict__
                current_utc_timestamp = currentUTCTimestamp()
                if data['upload_target'] == 'S3':
                    get_claim_info.first().is_uploaded_documentary = eval(data['upload_flag'])
                    get_claim_info.first().insurance_request_date = 0
                    get_claim_info.first().documentary_submit_status = 1
                    get_claim_info.first().update_date = current_utc_timestamp

                    try:
                        db.commit()
                    except Exception as error:
                        logger.critical(error, exc_info=True)
                        db.rollback()
                        return response_message_handler(500)

                    """ 2. s3 이면 디렉토리 안에 파일이 있는지 확인"""
                elif data['upload_target'] == 'WS':
                    insurant_identify_number = cipher.decrypt(partner_info_to_dict['partner_secret_key'],
                                                              get_claim_info.first().insurant_identify_number)
                    if insurant_identify_number != '':
                        document_file_path_list = []
                        insurant_birthday = insurant_identify_number.split('-')[0]
                        document_zip_file_name = f'{int(current_utc_timestamp)}.zip'
                        documentary_directory_path = f'{file_upload_path["URL"]}/{file_upload_path["BUCKET"]}' \
                                                     f'/document/{data["claim_id"]}'
                        documentary_zip_file_path = f'{documentary_directory_path}/{document_zip_file_name}'

                        if not os.path.exists(documentary_directory_path):
                            logger.info(f"{documentary_directory_path} 폴더가 존재하지 않습니다.")
                            return response_message_handler(204, result_message='청구파일이 존재하지 않습니다')

                        for folder_name, sub_folders, file_names in os.walk(documentary_directory_path):
                            for file_name in file_names:
                                document_file_path_list.append(f'{documentary_directory_path}/{file_name}')
                        logger.info(f'insurant birthday :: {insurant_birthday}')
                        pyminizip.compress_multiple(document_file_path_list, [], documentary_zip_file_path,
                                                    insurant_birthday, 4)

                        """zip 파일 만든 후 s3로 파일 업로드"""
                        s3_client = boto3.client('s3',
                                                 aws_access_key_id=s3_config['AWS_ACCESS_KEY'],
                                                 aws_secret_access_key=s3_config['AWS_SECRET_KEY'],
                                                 region_name=s3_config['REGION'])

                        key_path = f'document/{data["claim_id"]}/{document_zip_file_name}'
                        try:
                            s3_client.upload_file(documentary_zip_file_path,
                                                  file_upload_path["BUCKET"], key_path)

                            """ 올려놨던 파일 삭제 """
                            # delete_files = glob.glob(f'{documentary_directory_path}/*.png')
                            # for delete_file in delete_files:
                            #     try:
                            #         os.remove(delete_file)
                            #         logger.info(f'{delete_file} 삭제!!!')
                            #     except Exception as error:
                            #         logger.error(error, exc_info=True)

                        except ClientError as error:
                            logging.error(error, exc_info=True)
                            return response_message_handler(500, result_message='s3 업로드 중 오류가 발행하였습니다')

                        get_claim_info.first().is_uploaded_documentary = eval(data['upload_flag'])
                        get_claim_info.first().insurance_request_date = 0
                        get_claim_info.first().documentary_submit_status = 1
                        get_claim_info.first().update_date = currentUTCTimestamp()

                        try:
                            db.commit()
                        except Exception as error:
                            logger.critical(error, exc_info=True)
                            db.rollback()
                            return response_message_handler(500)

                    else:
                        return response_message_handler(204, result_message='피보험자의 생년월일 정보가 존재하지 않습니다.')
                else:
                    return response_message_handler(204, result_message='업로드 대상지점이 없습니다.')

                # 서류 등록시 알림톡 배치 제외
                try:
                    db.query(NotificationSendLog).filter(
                        NotificationSendLog.claim_id == claim_info['claim_id'],
                        NotificationSendLog.is_batch.__eq__(True),
                        NotificationSendLog.type == 5). \
                        update({NotificationSendLog.status: 0})
                    db.commit()
                except Exception as error:
                    logger.critical(error, exc_info=True)
                    db.rollback()
                    return response_message_handler(500)

                insurance_code_list = claim_info['ec_insurance_code_list'].split(',')

                # 개인팩스번호가 필요하지 않은 경우 서류첨부만 있는 알림톡 전송 뒤 보험사로 청구서 양식만들고 전송.
                if claim_info['claim_status'] == 1:

                    # 추가서류가 아닌 서류제출 후 보험사로 청구시 알림톡 전송
                    if claim_info['documentary_submit_status'] != 2 and eval(data['upload_flag']):

                        partner_info = db.query(PartnerClass).filter_by(partner_auth_token=auth_token, active=1)
                        if partner_info.first().hospital_seq > 0:
                            partner_name = partner_info.first().partner_name
                        else:
                            partner_name = ''

                        # 발송할 알림톡 host 가져오기
                        notification_url = partner_info.first().host

                        if notification_url == '':
                            notification_url = default_host

                        # 보험사의 이름 목록들
                        insurance_name_list = ''
                        insurance_need_fax_count = 0
                        for insurance_code in insurance_code_list:
                            get_insurance_info = db.query(InsuranceClass).filter_by(active=1,
                                                                                    ec_code=insurance_code)

                            if get_insurance_info.first():
                                insurance_name_list += f'{get_insurance_info.first().name},'
                                if get_insurance_info.first().claim_type == 2:
                                    insurance_need_fax_count += 1

                        if ',' in insurance_name_list:
                            insurance_name_list = insurance_name_list[:-1]

                        receive_cellphone_list = []
                        insurant_cellphone_decrypt = cipher.decrypt(
                            partner_info_to_dict['partner_secret_key'],
                            claim_info['insurant_cellphone']
                        )
                        # 피보험자가 본인이 아닐 경우 수익자와 피보험자 둘다 알림톡 발송
                        if claim_info['insurant_type'] == 1:
                            beneficiary_cellphone_decrypt = cipher.decrypt(
                                partner_info_to_dict['partner_secret_key'],
                                claim_info['beneficiary_cellphone']
                            )
                            receive_cellphone_list.append(beneficiary_cellphone_decrypt)
                            if beneficiary_cellphone_decrypt != insurant_cellphone_decrypt:
                                receive_cellphone_list.append(insurant_cellphone_decrypt)

                        # 피보험자가 본인일 경우 피보험자에게만 알림톡 발송
                        else:
                            receive_cellphone_list.append(insurant_cellphone_decrypt)

                        if len(receive_cellphone_list) > 0:

                            get_message_template = db.query(
                                MessageTemplateClass).filter_by(template_id='ics-006')

                            if get_message_template.count() > 0:
                                notification_message = get_message_template.first().message

                                claim_id_reformat = f"{claim_info['claim_id'][0:6]}-" \
                                                    f"{claim_info['claim_id'][6:]}"
                                notification_message = notification_message.replace(
                                    '#{NAME}', claim_info['insurant_name'])
                                notification_message = notification_message.replace(
                                    '#{CLAIMID}', claim_id_reformat)
                                notification_message = notification_message.replace(
                                    '#{COMPANY}', insurance_name_list)
                                notification_message = notification_message.replace(
                                    '#{PARTNER}', partner_name)
                                notification_message = notification_message.replace(
                                    '#{REGDATE}', convertTimeToYYYYMMDDWithComma(current_utc_timestamp + (9 * 3600)))

                                notification_message = notification_message.replace(
                                    "#{STATUS_URL}", notification_config['BUTTON_URL'].format(
                                        notification_url, claim_info['claim_id']))

                                for receive_cellphone in receive_cellphone_list:

                                    notification_message_json = json.loads(notification_message, strict=False)

                                    notification_response = send_notification.send_notification(
                                        data=notification_message_json[0],
                                        profile_key=notification_config['PROFILE'],
                                        receive_number=f"{notification_config['ITU']}{receive_cellphone[1:]}",
                                        reservation_date=''
                                    )
                                    # 알림톡 로그쌓기
                                    new_notification_send_log = NotificationSendLog(
                                        claim_id=claim_info['claim_id'],
                                        type=0,
                                        message_template_seq=get_message_template.first().seq,
                                        send_message=json.dumps(notification_message_json[0],
                                                                ensure_ascii=False),
                                        send_date=current_utc_timestamp,
                                        is_send_success=notification_response,
                                        create_date=current_utc_timestamp
                                    )
                                    try:
                                        db.add(new_notification_send_log)
                                        db.commit()
                                    except Exception as error:
                                        logger.critical(error, exc_info=True)
                                        db.rollback()
                            else:
                                logger.info("청구완료 알림톡 템플릿이 존재하지 않습니다.")
                        else:
                            logger.info("보낼 알림톡 번호가 존재하지 않습니다")
                return response_message_handler(200)
            else:
                return response_message_handler(204, result_message='청구정보가 존재하지 않습니다')
        else:
            return response_message_handler(401)

    except Exception as error:
        logger.critical(error, exc_info=True)
        return response_message_handler(500)
    finally:
        db.close()
        gc.collect()
