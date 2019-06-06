from config import *
from data.database import *
from company_house_data_extractor.recursiveSearch import getCompanyFilings

import json
from jsonpath_ng import jsonpath, parse

log = logging.getLogger('populateCompanyFilings')

def populateCompanyFilings():

    company_numbers = get_all_company_numbers()

    for company_number in company_numbers:

        company_filings = getCompanyFilings(company_number)
        updateCompanyFilings(company_number, json.dumps(company_filings))

populateCompanyFilings()
