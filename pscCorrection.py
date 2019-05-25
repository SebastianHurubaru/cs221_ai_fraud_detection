import cx_Oracle
from config import *

log = logging.getLogger('pscCorrection')

connection = cx_Oracle.connect("CS221", "CS221", "localhost/SEBI.168.86.68")

cursor = connection.cursor()


statement = 'select company_number from company where persons_with_significant_control = \'{}\''

cursor.execute(statement)


from rest import RESTClient
import json
from jsonpath_ng import jsonpath, parse

API_KEY="0K5Fn3TguQ_1OdFoSuzQREVG7aee1OKSYS5Mj5ns"
MAX_REQ_FOR_KEY=550
TIMEOUT=300 #seconds
BASE_URL="https://api.companieshouse.gov.uk"

restClient = RESTClient(API_KEY, MAX_REQ_FOR_KEY, TIMEOUT, BASE_URL)

def getCompanyPersonsWithSignificantControl(company_number):

    response = restClient.doRequest('/company/' + company_number + '/persons-with-significant-control', None)
    return response

# def updateCompanyPSC(company_number, persons_with_significant_control):
#
#     statement = 'update company set persons_with_significant_control=\'' + persons_with_significant_control + '\' where company_number=\'' + company_number + '\''
#     cursor.execute(statement)
#     connection.commit()


def updateCompanyPSC(company_number, persons_with_significant_control):
    statement = 'UPDATE company SET persons_with_significant_control = :v WHERE company_number = :k'
    cursor.execute(statement, {'k': company_number, 'v': persons_with_significant_control})
    connection.commit()


companies = []
for result in cursor:

    company_number = result[0]
    companies.append(company_number)

for idx, company_number in enumerate(companies):

    print(company_number)
    log.debug('On {} record and updating {} company'.format(idx, company_number))

    psc = getCompanyPersonsWithSignificantControl(company_number)

    updateCompanyPSC(company_number, json.dumps(psc))

