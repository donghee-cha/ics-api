from flask import Flask
from flask_cors import CORS

from api import config_app

from api.router import common_api
from api.router.v1.insurant import insurant_api as insurant_api_v1
from api.router.v1.claim import claim_api as claim_api_v1
from api.router.v1.claim_receive import claim_receive_api as claim_receive_api_v1
from api.router.v1.claim_status import claim_status_api as claim_status_api_v1
from api.router.v1.beneficiary import beneficiary_api as beneficiary_api_v1
from api.router.v1.accident import accident_api as accident_api_v1
from api.router.v1.terms import terms_api as terms_api_v1
from api.router.v1.thirdparty_terms import thirdparty_terms_api as thirdparty_terms_api_v1
from api.router.v1.insurance import insurance_api as insurance_api_v1
from api.router.v1.fax_number import fax_number_api as fax_number_api_v1
from api.router.v1.insurance_telephone import insurance_telephone_api as insurance_telephone_api_v1
from api.router.v1.information import information_api as information_api_v1
from api.router.v1.token import token_api as token_api_v1
from api.router.v1.benefit import benefit_api as benefit_api_v1
from api.router.v1.insurance_terms import insurance_terms_api as insurance_terms_api_v1
from api.router.v1.signage import signage_api as signage_api_v1
from api.router.v1.setting import setting_api as setting_api_v1
from api.router.v1.setting_signage import setting_signage_api as setting_signage_api_v1
from api.router.v1.upload_signature import upload_signature_api as upload_signature_api_v1
from api.router.v1.upload import upload_api as upload_api_v1
from api.router.v1.check import check_api as check_api_v1
from api.router.v1.config import config_api as config_api_v1
from api.router.v1.counting import counting_api as counting_api_v1
from api.router.v1.send import send_api as send_api_v1
from api.router.v1.sign_insurance import sign_insurance_api as sign_insurance_v1

from api.router.dev.insurant import insurant_api as insurant_api_dev
from api.router.dev.claim import claim_api as claim_api_dev
from api.router.dev.claim_receive import claim_receive_api as claim_receive_api_dev
from api.router.dev.claim_status import claim_status_api as claim_status_api_dev
from api.router.dev.beneficiary import beneficiary_api as beneficiary_api_dev
from api.router.dev.accident import accident_api as accident_api_dev
from api.router.dev.terms import terms_api as terms_api_dev
from api.router.dev.thirdparty_terms import thirdparty_terms_api as thirdparty_terms_api_dev
from api.router.dev.insurance import insurance_api as insurance_api_dev
from api.router.dev.fax_number import fax_number_api as fax_number_api_dev
from api.router.dev.insurance_telephone import insurance_telephone_api as insurance_telephone_api_dev
from api.router.dev.information import information_api as information_api_dev
from api.router.dev.token import token_api as token_api_dev
from api.router.dev.benefit import benefit_api as benefit_api_dev
from api.router.dev.insurance_terms import insurance_terms_api as insurance_terms_api_dev
from api.router.dev.signage import signage_api as signage_api_dev
from api.router.dev.setting import setting_api as setting_api_dev
from api.router.dev.upload_signature import upload_signature_api as upload_signature_api_dev
from api.router.dev.upload import upload_api as upload_api_dev
from api.router.dev.setting_signage import setting_signage_api as setting_signage_api_dev
from api.router.dev.check import check_api as check_api_dev
from api.router.dev.config import config_api as config_api_dev
from api.router.dev.counting import counting_api as counting_api_dev
from api.router.dev.send import send_api as send_api_dev
from api.router.dev.sign_insurance import sign_insurance_api as sign_insurance_dev


app = Flask(__name__)
app.config.update(config_app)
app.config['MAX_CONTENT_LENGTH'] = 250 * 1024 * 1024

app.register_blueprint(common_api, url_prefix='/')
app.register_blueprint(insurant_api_v1, url_prefix='/v1/insurant/')
app.register_blueprint(claim_api_v1, url_prefix='/v1/claim/')
app.register_blueprint(beneficiary_api_v1, url_prefix='/v1/beneficiary/')
app.register_blueprint(accident_api_v1, url_prefix='/v1/accident/')
app.register_blueprint(terms_api_v1, url_prefix='/v1/terms/')
app.register_blueprint(thirdparty_terms_api_v1, url_prefix='/v1/thirdparty-terms/')
app.register_blueprint(insurance_api_v1, url_prefix='/v1/insurance/')
app.register_blueprint(insurance_telephone_api_v1, url_prefix='/v1/insurance-telephone/')
app.register_blueprint(fax_number_api_v1, url_prefix='/v1/fax-number/')
app.register_blueprint(claim_receive_api_v1, url_prefix='/v1/claim-receive/')
app.register_blueprint(claim_status_api_v1, url_prefix='/v1/claim-status/')
app.register_blueprint(information_api_v1, url_prefix='/v1/information/')
app.register_blueprint(token_api_v1, url_prefix='/v1/token/')
app.register_blueprint(benefit_api_v1, url_prefix='/v1/benefit/')
app.register_blueprint(insurance_terms_api_v1, url_prefix='/v1/insurance-terms/')
app.register_blueprint(signage_api_v1, url_prefix='/v1/signage/')
app.register_blueprint(setting_api_v1, url_prefix='/v1/setting/')
app.register_blueprint(upload_signature_api_v1, url_prefix='/v1/upload-signature/')
app.register_blueprint(upload_api_v1, url_prefix='/v1/upload/')
app.register_blueprint(setting_signage_api_v1, url_prefix='/v1/setting-signage/')
app.register_blueprint(check_api_v1, url_prefix='/v1/check/')
app.register_blueprint(config_api_v1, url_prefix='/v1/config/')
app.register_blueprint(counting_api_v1, url_prefix='/v1/counting/')
app.register_blueprint(send_api_v1, url_prefix='/v1/send/')
app.register_blueprint(sign_insurance_v1, url_prefix='/v1/sign-insurance/')

app.register_blueprint(insurant_api_dev, url_prefix='/dev/insurant/')
app.register_blueprint(claim_api_dev, url_prefix='/dev/claim/')
app.register_blueprint(beneficiary_api_dev, url_prefix='/dev/beneficiary/')
app.register_blueprint(accident_api_dev, url_prefix='/dev/accident/')
app.register_blueprint(terms_api_dev, url_prefix='/dev/terms/')
app.register_blueprint(thirdparty_terms_api_dev, url_prefix='/dev/thirdparty-terms/')
app.register_blueprint(insurance_api_dev, url_prefix='/dev/insurance/')
app.register_blueprint(insurance_telephone_api_dev, url_prefix='/dev/insurance-telephone/')
app.register_blueprint(fax_number_api_dev, url_prefix='/dev/fax-number/')
app.register_blueprint(claim_receive_api_dev, url_prefix='/dev/claim-receive/')
app.register_blueprint(claim_status_api_dev, url_prefix='/dev/claim-status/')
app.register_blueprint(information_api_dev, url_prefix='/dev/information/')
app.register_blueprint(token_api_dev, url_prefix='/dev/token/')
app.register_blueprint(benefit_api_dev, url_prefix='/dev/benefit/')
app.register_blueprint(insurance_terms_api_dev, url_prefix='/dev/insurance-terms/')
app.register_blueprint(signage_api_dev, url_prefix='/dev/signage/')
app.register_blueprint(setting_api_dev, url_prefix='/dev/setting/')
app.register_blueprint(upload_signature_api_dev, url_prefix='/dev/upload-signature/')
app.register_blueprint(upload_api_dev, url_prefix='/dev/upload/')
app.register_blueprint(setting_signage_api_dev, url_prefix='/dev/setting-signage/')
app.register_blueprint(check_api_dev, url_prefix='/dev/check/')
app.register_blueprint(config_api_dev, url_prefix='/dev/config/')
app.register_blueprint(counting_api_dev, url_prefix='/dev/counting/')
app.register_blueprint(send_api_dev, url_prefix='/dev/send/')
app.register_blueprint(sign_insurance_dev, url_prefix='/dev/sign-insurance/')

app.app_context().push()

# SWAGGER_URL = '/apidoc'
# API_URL = '/swagger.json'
#
# swaggerui_blueprint = get_swaggerui_blueprint(
#     SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
#     API_URL,
#     config={  # Swagger UI config overrides
#         'app_name': "ICS API Documentation"
#     }
# )

# app.register_blueprint(swaggerui_blueprint)

CORS(app, resources={r'*': {'origins': '*'}})

