import cx_Oracle
from config import *
from data.database import get_all_company_numbers
import pandas as pd
import json
from jsonpath_ng import parse
import numpy as np

import deep_neural_network.feature_extractor

import multiprocessing

connection = cx_Oracle.connect("CS221", "CS221", "localhost/SEBI.168.86.68")

log = logging.getLogger('feature_extractor.py')

df = pd.read_csv('../data/company_debt_equity_data.csv', header=0, dtype=str)

def initProcess(share):
  deep_neural_network.feature_extractor.features_data = share

def read_company(company_number):

    cursor = connection.cursor()
    statement = 'select * from company where company_number = \'{}\''.format(company_number)

    cursor.execute(statement)
    for result in cursor:
        return json.loads(result[2]), json.loads(result[3]), result[4]

    return None, None, None


def extract_features(company_number):

    officers, pscs, label = read_company(company_number)

    # feeature 1: total (active and inactive) number of officers
    result = parse('$.total_results').find(officers)
    total_number_of_officers = result[0].value if len(result) > 0 else 0

    # feeature 2: total number of active officers
    result = parse('$.active_count').find(officers)
    number_of_active_officers = result[0].value if len(result) > 0 else 0

    # feeature 3: total number of inactive officers
    number_of_inactive_officers = total_number_of_officers - number_of_active_officers

    # feature 4: number of non-persons officers
    result = parse('$.items[*].identification.legal_form').find(officers)
    number_of_non_persons_officers = len(result)

    # feeature 5: total (active and ceased) number of persons with significant control
    result = parse('$.total_results').find(pscs)
    total_number_of_psc = result[0].value if len(result) > 0 else 0
    if total_number_of_psc == None:
        result = parse('$.items[*]').find(pscs)
        total_number_of_psc = len(result)

    # feeature 6: number of active persons with significant control
    result = parse('$.active_count').find(pscs)
    number_of_active_psc = result[0].value if len(result) > 0 else 0
    if number_of_active_psc == None:
        number_of_active_psc = 0

    # feeature 7: total number of inactive officers
    number_of_ceased_psc = total_number_of_psc - number_of_active_psc

    # feature 8: number of non-persons persons with significant control
    result = parse('$.items[*].identification.legal_form').find(pscs)
    number_of_non_psc = len(result)

    # feature 9: debt to equity ratio. Default to 10%
    debt_to_equity = 0.1
    if company_number in df['company_number'].values:
        select_indices = list(np.where(df["company_number"] == company_number)[0])
        debt = float(df.iloc[select_indices]['debt'].values[0])
        equity = float(df.iloc[select_indices]['equity'].values[0])
        debt_to_equity = debt / equity if equity != 0. else 0.

    # output: good(0) or bad(1)
    output = 0 if label == 'good' else 1

    deep_neural_network.feature_extractor.features_data.append(
        [company_number, total_number_of_officers, number_of_active_officers, number_of_inactive_officers,
         number_of_non_persons_officers, total_number_of_psc, number_of_active_psc, number_of_ceased_psc,
         number_of_non_psc, debt_to_equity, output])

    log.debug('Finished extracting features for company {}'.format(company_number))


def extract_features_for_all_companies(file_name):

    company_numbers = get_all_company_numbers()

    manager = multiprocessing.Manager()
    feature_data = manager.list()

    transactionPool = multiprocessing.Pool(PROCESS_POOL_SIZE, initializer=initProcess, initargs=(feature_data,))
    transactionPool.map(extract_features, company_numbers)
    transactionPool.close()
    transactionPool.join()

    results = [data for data in feature_data]
    df = pd.DataFrame(results)
    df.columns = ['Company number',
                  'Total number of officers', 'Number of active officers', 'Number of inactive officers', 'Number of non-persons officers',
                  'Total number of person with significant control', 'Number of active persons with significant control',
                  'Number of ceased persons with significant control', 'Number of non-persons with significant control', 'Debt/Equity',
                  'Good/Bad']

    df.to_csv(file_name, index=False)

if __name__ == '__main__':
    extract_features_for_all_companies('../data/all_companies_features.csv')