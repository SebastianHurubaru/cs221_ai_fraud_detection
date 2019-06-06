from config import *
import cx_Oracle
import json
from jsonpath_ng import parse

log = logging.getLogger('database.py')
connection = cx_Oracle.connect("CS221", "CS221", "localhost/SEBI.168.86.68", threaded=True)
connection.autocommit = True
cursor = connection.cursor()


def insertCompany(company_number, profile, officers, persons_with_significant_control, filings):

    statement = 'MERGE INTO company USING dual ON ( company_number=:2 ) \
                WHEN MATCHED THEN UPDATE SET profile=:3 , officers=:4, persons_with_significant_control=:5, filings=:6 \
                WHEN NOT MATCHED THEN INSERT (company_number, profile, officers, persons_with_significant_control, filings) \
                VALUES (:2, :3, :4, :5, :6)'
    cursor.execute(statement, (company_number, profile, officers, persons_with_significant_control, filings))
    


def insertOfficer(officer_id, appointments):
    # statement = 'insert into officer(officer_id, appointments) values (:2, :3)'
    statement = 'MERGE INTO officer USING dual ON ( officer_id = :2 ) \
                    WHEN MATCHED THEN UPDATE SET appointments =:3  \
                    WHEN NOT MATCHED THEN INSERT (officer_id, appointments)  \
                    VALUES (:2, :3)'
    cursor.execute(statement, (officer_id, appointments))
    

def updateCompanyPSC(company_number, persons_with_significant_control):
    statement = 'UPDATE company SET persons_with_significant_control = :v WHERE company_number = :k'
    cursor.execute(statement, {'k': company_number, 'v': persons_with_significant_control})
    

def updateCompanyFilings(company_number, filings):
    statement = 'UPDATE company SET filings = :v WHERE company_number = :k'
    cursor.execute(statement, {'k': company_number, 'v': filings})
    

def insertPSC(psc_id, psc_data, label):

    statement = 'MERGE INTO person_with_significant_control USING dual ON ( psc_id=:2 ) \
                WHEN MATCHED THEN UPDATE SET psc_data=:3  \
                WHEN NOT MATCHED THEN INSERT (psc_id, psc_data)  \
                VALUES (:2, :3)'
    cursor.execute(statement, (psc_id, psc_data))
    

def insertCompanyFiling(company_number, transaction_id, format, content):

    # statement = 'MERGE INTO company_filing USING dual ON ( company_number=:2 AND transaction_id=:3 AND format=:4 ) \
    #             WHEN MATCHED THEN UPDATE SET content=:5  \
    #             WHEN NOT MATCHED THEN INSERT (company_number, transaction_id, format, content)  \
    #             VALUES (:2, :3, :4, :5)'
    # cursor.execute(statement, (company_number, transaction_id, format, content))

    cursor = connection.cursor()
    log.info('Saving')
    try:
        cursor.callproc("pINSERT_COMPANY_FILING",
                        [company_number, transaction_id, format, content])

    except UnicodeEncodeError:
        cursor.callproc("pINSERT_COMPANY_FILING",
                        [company_number, transaction_id, format, "Error"])

    cursor.close()

    log.info('Done saving')

def transactionExists(company_number, transaction_id, format='xhtml'):

    cursor = connection.cursor()
    statement = 'select count(*) from company_filing where company_number = \'{}\' and transaction_id = \'{}\' and format = \'{}\''.format(company_number, transaction_id, format)

    cursor.execute(statement)

    for result in cursor:
        if result[0] != 0:
            return True

    return False

def get_company_filing_transaction_ids(company_number):

    cursor = connection.cursor()
    statement = 'select filings from company where company_number = \'{}\''.format(company_number)

    cursor.execute(statement)

    transaction_ids = []
    for result in cursor:
        items = parse('$.items[*].transaction_id').find(json.loads(result[0]))
        for item in items:
            transaction_ids.append(item.value)

    return transaction_ids

def get_all_company_numbers():

    cursor = connection.cursor()
    statement = 'select company_number from company'
    # statement = 'select company_number from company where company_number = \'{}\''.format('11137739')

    cursor.execute(statement)

    company_numbers = []
    for result in cursor:
        company_numbers.append(result[0])

    return company_numbers

def get_no_filing_company_numbers():

    cursor = connection.cursor()
    statement = 'select c.company_number from company c where not exists (select company_number from company_filing where company_number = c.company_number)'
    # statement = 'select company_number from company where company_number = \'{}\''.format('11137739')

    cursor.execute(statement)

    company_numbers = []
    for result in cursor:
        company_numbers.append(result[0])

    return company_numbers




