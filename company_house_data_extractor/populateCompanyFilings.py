from config import *
from data.database import *
from company_house_data_extractor.recursiveSearch import getCompanyFilings

from multiprocessing import Pool

from multiprocessing.dummy import Pool as ThreadPool
from functools import partial

import json
from jsonpath_ng import jsonpath, parse

log = logging.getLogger('populateCompanyFilings')

def populateCompanyFilings():

    company_numbers = get_all_company_numbers()

    for company_number in company_numbers:

        company_filings = getCompanyFilings(company_number)
        updateCompanyFilings(company_number, json.dumps(company_filings))


def processCompany(company_number):

    company_filings = get_company_filings(company_number)
    items = parse('$.items').find(company_filings)
    for item in items[0].value:
        insertPartialCompanyFiling(company_number, item['transaction_id'], 'xhtml', json.dumps(item))


# populateCompanyFilings()


if __name__ == '__main__':

    company_numbers = get_all_company_numbers()

    companyPool = Pool(PROCESS_POOL_SIZE)
    companyPool.map_async(processCompany, company_numbers)
    companyPool.close()
    companyPool.join()
