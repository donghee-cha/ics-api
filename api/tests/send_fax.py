import ftplib
import os
import boto3


class SendFax:

    def __init__(self):
        self.ftp_url = '192.168.50.34'
        self.user = 'dongheecha'
        self.password = 'ubuntu'
        self.port = 21
        self.is_uploaded = False

    # ftp 연결 후 문서 업로드
    def upload_ftp(self, file):
        try:
            ftp = ftplib.FTP_TLS()
            ftp.set_debuglevel(2)
            ftp.connect(host=self.ftp_url, port=self.port, timeout=10)
            ftp.sendcmd('USER {}'.format(self.user))
            res = ftp.sendcmd('PASS {}'.format(self.password))
            
            # ftp 접속 성공
            if '230' in res:
                ftp.set_pasv(False)
                res = ftp.retrlines('LIST', listLineCallback)

                # 폴더 리스트 불러오기
                if '226' in res:
                    # 파일 전송!!
                    res_uploaded = ftp.storbinary('STOR {}'.format('sample.jpg'), open(file, 'rb'))

            ftp.quit()
        except Exception as e:
            print(e)

    # ftp로 문서 업로드 후 비즈모아샷 팩스 전송
    def upload_fax(self, file_name_list):
        return

"""
 디렉토리 목록 출력하기 콜백
"""
def listLineCallback(line):
    msg = "** print %s*" % line
    print(msg)
