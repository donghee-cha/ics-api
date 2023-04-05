"""
매개변수 헬퍼 입니다
"""
import logging

logger = logging.getLogger(__name__)


def check_required_param(new_request, requires):
    parameter_dict = new_request.args.to_dict()
    is_validate = 1

    logger.info("<<<<< REQUEST API PARAMETER >>>>>> {}".format(parameter_dict))
    if requires:

        for key in requires:
            if key not in parameter_dict:
                is_validate = 0
            else:
                if parameter_dict[key] == "":
                    is_validate = 0

        if len(requires) == 0:
            is_validate = 0

    return is_validate


def check_required_form_data(new_request, requires):
    parameter_dict = new_request.form.to_dict()
    is_validate = 1
    if new_request.path != '/v1/check/status' and new_request.path != '/dev/check/status':
        logger.info("<<<<<<<<<<[REQUEST API PARAMETER ] {} >>>>>>>>>>>".format(parameter_dict))
    if requires:
        for key in requires:

            if key not in parameter_dict:
                is_validate = 0
            else:

                if parameter_dict[key] == "" or parameter_dict[key].replace(" ", "") == "":
                    is_validate = 0

        if len(requires) == 0:
            is_validate = 0

    return is_validate
