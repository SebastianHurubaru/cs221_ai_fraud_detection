import logging
import locale

import pandas as pd

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(thread)s %(message)s',
                    datefmt='%m-%d %H:%M:%S')

# input_dir = 'input-dev'

input_dir = 'C:/Users/sebas/Downloads/Accounts_Bulk_Data-2019-04-27'
# tags = ['FixedAssets', 'CurrentAssets', 'NetAssetsLiabilitiesIncludingPensionAssetLiability']

file_name_column = 'File Name'

tags = {'EntityCurrentLegalOrRegisteredName': 'Company name',
        'CountryFormationOrIncorporation': 'Country of incorporation',
        'XXX1': 'Date of incorporation',
        'StartDateForPeriodCoveredByReport': 'Starting date of financial statements',
        'EndDateForPeriodCoveredByReport': 'Year-end of financial statements',
        'NameEntityOfficer[0]': 'Name of director 1',
        'NameEntityOfficer[1]': 'Name of director 2',
        'NameEntityOfficer[2]': 'Name of director 3',
        'NameEntityOfficer[3]': 'Name of director 4',
        'NameEntityOfficer[4]': 'Name of director 5',
        'XXX[0]': 'Name of shareholder 1',
        'XXX[1]': 'Name of shareholder 2',
        'XXX[2]': 'Name of shareholder 3',
        'XXX[3]': 'Name of shareholder 4',
        'XXX[4]': 'Name of shareholder 5',
        'ToBeDoneAsAList': 'Registered office address',
        'XXX2': 'Name of company secretary',
        'NameEntityAuditors': 'Auditor',
        'DateSigningDirectorsReport': 'Date of signing the financial statements',
        'XXX3': 'Currency of financial statements'}

output_csv_file = 'output/features.csv'

locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')

numOfFeatures = 8
numOfOutputs = 1
numOfHiddenLayerUnits = (numOfFeatures + numOfOutputs) * 2
batch_size = 64
num_iterations = 500
validation_split = 0.1

MAX_REQ_FOR_KEY=500

API_KEYS= [("0K5Fn3TguQ_1OdFoSuzQREVG7aee1OKSYS5Mj5ns", MAX_REQ_FOR_KEY),
           ("CTdeE4B4nqb3vuip2jWQ4oMbajwC8uvlu-tSNLSs", MAX_REQ_FOR_KEY),
           ("QAABDOuTedqG6Y3sS70242hguHxX8lXJ8bWuXjNs", MAX_REQ_FOR_KEY),
           ("ieGbtv4XnrDE7ZsfrXlVatpW8K7z0S_hsdbpd3Wq", MAX_REQ_FOR_KEY)]

TIMEOUT=300 #seconds
BASE_URL="https://api.companieshouse.gov.uk"

FILINGS_BASE_URL='https://beta.companieshouse.gov.uk/company'

PROCESS_POOL_SIZE=16
THREAD_POOL_SIZE=10