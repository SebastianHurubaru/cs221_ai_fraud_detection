import requests
from config import *
from data.database import *
from company_house_data_extractor.recursiveSearch import getFilingDocument
from multiprocessing import Pool

from multiprocessing.dummy import Pool as ThreadPool
from functools import partial

import json
from jsonpath_ng import jsonpath, parse

log = logging.getLogger('populateCompanyFilings')


def populateCompanyFilings():

    company_numbers = get_all_company_numbers()

    companyPool = Pool(PROCESS_POOL_SIZE)
    companyPool.map_async(processCompany, company_numbers)
    companyPool.close()
    companyPool.join()

def processCompany(company_number):

    transaction_ids = get_company_filing_transaction_ids(company_number)

    transactionPool = ThreadPool(THREAD_POOL_SIZE)
    transactionPool.map(partial(processTransactionId, company_number=company_number), transaction_ids)
    transactionPool.close()
    transactionPool.join()


def processTransactionId(transaction_id, company_number):

    if transactionExists(company_number, transaction_id) == False:
        getFilingDocument(company_number, transaction_id)


if __name__ == '__main__':

    company_numbers = get_all_company_numbers()
    # company_numbers = get_no_filing_company_numbers()

    companyPool = Pool(PROCESS_POOL_SIZE)
    companyPool.map_async(processCompany, company_numbers)
    companyPool.close()
    companyPool.join()

# populateCompanyFilings()