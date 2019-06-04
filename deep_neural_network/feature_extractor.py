import cx_Oracle
from config import *
from data.database import get_all_company_numbers
import pandas as pd
import json
from jsonpath_ng import parse

connection = cx_Oracle.connect("CS221", "CS221", "localhost/SEBI.168.86.68")

log = logging.getLogger('feature_extractor.py')



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

    # output: good(0) or bad(1)
    output = 0 if label == 'good' else 1

    return [total_number_of_officers, number_of_active_officers, number_of_inactive_officers, number_of_non_persons_officers, total_number_of_psc, number_of_active_psc, number_of_ceased_psc, number_of_non_psc, output]

def extract_features_for_all_companies(file_name):

    data = []

    company_numbers = get_all_company_numbers()
    for idx, company_number in enumerate(company_numbers):
        log.info('Extracting features for {}'.format(company_number))
        data.append([company_number] + extract_features(company_number))
        log.info('Finished processing {} out of {} records'.format(idx + 1, len(company_numbers)))

    df = pd.DataFrame(data)
    df.columns = ['Company number',
                  'Total number of officers', 'Number of active officers', 'Number of inactive officers', 'Number of non-persons officers',
                  'Total number of person with significant control', 'Number of active persons with significant control', 'Number of ceased persons with significant control', 'Number of non-persons with significant control',
                  'Good/Bad']

    df.to_csv(file_name, index=False)

extract_features_for_all_companies('../data/all_companies_features.csv')