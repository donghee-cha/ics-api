
import re

def is_valid_cellphone(str):
    cellphone_regex = re.compile("^01([0|1|6|7|8|9])-?([0-9]{3,4})-?([0-9]{4})$")
    return cellphone_regex.search(str)
