import os
import sys
import logging
from dotenv import load_dotenv
from os.path import dirname
from os.path import join
import re
from ..constants import constants

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=int(os.environ.get(constants.LOG_LEVEL, constants.LOG_LEVEL_DEFAULT_VALUE)),
        datefmt='%Y-%m-%d %H:%M:%S')
        
        
def print_logo(version):
        version_len = len(version)
        print(
            """
███████╗██████╗  ██████╗ ████████╗██╗███████╗██╗   ██╗██████╗ 
██╔════╝██╔══██╗██╔═══██╗╚══██╔══╝██║██╔════╝██║   ██║██╔══██╗
███████╗██████╔╝██║   ██║   ██║   ██║███████╗██║   ██║██████╔╝
╚════██║██╔═══╝ ██║   ██║   ██║   ██║╚════██║██║   ██║██╔══██╗
███████║██║     ╚██████╔╝   ██║   ██║███████║╚██████╔╝██████╔╝
╚══════╝╚═╝      ╚═════╝    ╚═╝   ╚═╝╚══════╝ ╚═════╝ ╚═════╝ 
"""
            + "                                     "[: -(version_len + 2)]
            + "v{} ".format(version
            + "\n")
        )

def write_exception():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    logging.error("%s %s %s", exc_type, fname, exc_tb.tb_lineno, exc_info=1)



def generate_compare_array(strings):
    strings = strings.strip().lower()
    compare_array_values = []
    compare_array_values.append(strings)
    compare_array_values.append(re.sub(r'[^\w\s]','',strings).strip())
    for token in constants.SPLIT_TOKENS:
        compare_array_values.append(strings.split(token, 1)[0].strip())
        compare_array_values.append(re.sub(r'[^\w\s]','',strings.split(token, 1)[0]).strip())

    return list(set(compare_array_values))

def compare_strings(a, b):
    return compare(generate_compare_array(a), generate_compare_array(b))

def compare_string_to_exclusion(a, stringb):
    return compare_exclusions(a.split(), stringb)

def compare_exclusions(stringsa, stringsb):
    for stringa in stringsa:
        for stringb in stringsb:
            if stringa.strip().lower() == stringb.strip().lower():
                logging.warning("Found excluded word: %s. Skipping...", stringb)
                return True    
    return False

def compare(stringsa, stringsb, log_excluded=False):
    for stringa in stringsa:
        for stringb in stringsb:
            if stringa == stringb or stringb in stringa or stringa in stringb:
                if log_excluded is True:
                    logging.warning("Found excluded word: %s. Skipping...", stringb)
                return True    
    return False