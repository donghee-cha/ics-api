
from logging.config import fileConfig

import socket
import os, json
import configparser

if not os.path.exists('logs'):
    os.makedirs('logs')

log_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logging.ini')
config = configparser.ConfigParser()
config.read(log_file_path)
config.set('handler_logfile', 'args', f"('logs/{socket.gethostbyname(socket.gethostname())}_logging.log', 'midnight', 1 , 0 ,'utf8')")

with open(log_file_path, 'w') as configfile:
    config.write(configfile)
fileConfig(log_file_path)

basedir = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["ENV"] = "DEVELOPMENT"

"""
 설정 정보 읽어들이기
"""

with open(basedir + "/config.json", 'r', encoding='utf-8') as f:
    _config = json.load(f)

"""
파트너사 정보 읽어들이기
"""
master_key = _config["DEFAULT"]["MASTER_KEY"]  # auth token에 쓰이는 마스터키
secret_key = _config["DEFAULT"]["SECRET_KEY"]  # body 에 쓰이는 마스터키

default_partner_code = _config['DEFAULT']['PARTNER_CODE']
default_hospital_seq = _config['DEFAULT']['HOSPITAL_SEQ']
default_hospital_code = _config['DEFAULT']['HOSPITAL_CODE']
default_hospital_sido_code = _config['DEFAULT']['SIDO_CODE']
default_hospital_sigungu_code = _config['DEFAULT']['SIGUNGU_CODE']

api_url = _config[os.environ["ENV"]]['API_URL']
default_host = _config[os.environ["ENV"]]['WEB_URL']

"""
 bizm 정보 읽어들이기
"""
notification_config = _config[os.environ["ENV"]]['NOTIFICATION']
notification_message_template = _config["DEFAULT"]['NOTIFICATION_MESSAGE_TEMPLATE']

"""
 s3 정보 읽어들이기
"""
s3_config = _config[os.environ["ENV"]]['S3']

"""
contents 경로
"""
contents_path = _config[os.environ["ENV"]]['CONTENTS_PATH']
file_upload_path = _config[os.environ["ENV"]]['WS']
config_app = _config[os.environ["ENV"]]
