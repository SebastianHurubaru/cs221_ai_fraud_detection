from config import *
from data.database import *
from company_house_data_extractor.rest import RESTClient
import json
from jsonpath_ng import parse
import requests

log = logging.getLogger('backtrackSearch')

visited_officers = []
visited_companies = []

restClient = RESTClient(API_KEYS, TIMEOUT, BASE_URL)

def searchTroikaEntities(entity, K):

    is_company, company_numbers = isCompany(entity)
    if is_company is True:
        for company_number in company_numbers:
            searchCompany(company_number, K)
        return

    is_officer, officer_ids = isOfficer(entity)
    if is_officer is True:
        for officer_id in officer_ids:
            searchOfficer(officer_id, K)


def searchCompany(company_number, K):

    if K is 0: return

    if company_number in visited_companies:
        return

    visited_companies.append(company_number)

    # get company profile
    companyProfile = getCompanyProfile(company_number)
    log.debug(companyProfile)

    # get company's persons with significant control
    pscs = getCompanyPersonsWithSignificantControl(company_number)
    populatePSCData(pscs)
    log.debug(pscs)

    # get company's officers
    companyOfficers = getCompanyOfficers(company_number)
    log.debug(companyOfficers)

    # get company's filing history
    companyFilings = getCompanyFilings(company_number)
    log.debug(companyFilings)
    transaction_ids = parse('$.items[*].transaction_id').find(companyFilings)
    for transaction_id in transaction_ids:
        getFilingDocument(company_number, transaction_id.value)

    # insert in the database
    insertCompany(company_number, json.dumps(companyProfile), json.dumps(companyOfficers), json.dumps(pscs), json.dumps(companyFilings))

    # for each officer call searchTroikaOfficer(entity, K-1)
    officer_ids = [officerLink.value.split('/')[2] for officerLink in parse('$.items[*].links.officer.appointments').find(companyOfficers)]
    for officer_id in officer_ids:
        searchOfficer(officer_id, K - 1)


def searchOfficer(officer_id, K):

    if officer_id in visited_officers:
        return

    visited_officers.append(officer_id)

    # get the appointments
    appointments = getOfficerAppointments(officer_id)
    log.debug(appointments)

    # insert in the database
    insertOfficer(officer_id, json.dumps(appointments))

    if K is 0: return

    # for each appointment get the company name and call searchTroikaCompany(company, K):
    appointments_company_numbers = parse('$.items[*].appointed_to.company_number').find(appointments)
    for company_number in appointments_company_numbers:
        searchCompany(company_number.value, K)


def searchForValidCompanies(K):

    df = pd.read_csv("../data/Towns_List.csv")

    for town in df['Town']:

        log.debug('Getting {} companies for {} town'.format(K, town))

        is_company, company_numbers = isCompany(town)
        if is_company is True:
            for idx, company_number in enumerate(company_numbers):
                if K == idx:
                    break
                searchCompany(company_number.value, 1)

def isCompany(entity):

    # strip all spaces when querying
    params = {'q' : entity.replace(' ', '')}
    response = restClient.doRequest('/search/companies', params)

    number_of_results = parse('$.total_results').find(response)

    if number_of_results[0].value > 0:
        return True, parse('$.items[*].company_number').find(response)

    return False, None

def getCompanyProfile(company_number):

    response = restClient.doRequest('/company/' + company_number, None)
    return response


def getCompanyPersonsWithSignificantControl(company_number):

    response = restClient.doRequest('/company/' + company_number + '/persons-with-significant-control', None)
    return response

def getCompanyFilings(company_number):
    response = restClient.doRequest('/company/' + company_number + '/filing-history', None)
    return response

def getFilingDocument(company_number, transaction_id, format='xhtml'):

    session = requests.Session()

    url = FILINGS_BASE_URL + '/' + company_number + '/filing-history/' + transaction_id + '/document'
    params = {'format': format,
              'download': '0'}

    response = session.get(url, params=params)
    if response.status_code == 200:
        log.debug(response.text)
        insertCompanyFiling(company_number, transaction_id, format, response.text)
    else:
        insertCompanyFiling(company_number, transaction_id, format, 'None')
    session.close()

def populatePSCData(persons_with_significant_control):

    psc_list = [psc.value for psc in parse('$.items[*]').find(persons_with_significant_control)]
    for psc in psc_list:
        psc_id = parse('$.links.self').find(psc)[0].value.split('/')[-1]
        insertPSC(psc_id, json.dumps(psc), 'good')


def getCompanyOfficers(company_number):
    response = restClient.doRequest('/company/' + company_number + '/officers', None)
    return response

def isOfficer(entity):
    # strip all spaces when querying
    params = {'q': entity.replace(' ', '')}
    response = restClient.doRequest('/search/officers', params)

    number_of_results = parse('$.total_results').find(response)

    if number_of_results[0].value > 0:
        return True, [officerLink.value.split('/')[2] for officerLink in parse('$.items[*].links.self').find(response)]

    return False, None

def getOfficerAppointments(officer_id):
    response = restClient.doRequest('/officers/' + officer_id + '/appointments', None)
    return response


def fillVisitedCompanies():

    global visited_companies

    visited_companies = get_all_company_numbers()

# searchTroikaEntities('Cascado AG', 100)

# fillVisitedCompanies()
# searchForValidCompanies(100)