from config import *

log = logging.getLogger('backtrackSearch')

from rest import RESTClient
import json
from jsonpath_ng import jsonpath, parse

API_KEY="0K5Fn3TguQ_1OdFoSuzQREVG7aee1OKSYS5Mj5ns"
MAX_REQ_FOR_KEY=600
TIMEOUT=600 #seconds
BASE_URL="https://api.companieshouse.gov.uk"

visited_officers = []
visited_companies = []

restClient = RESTClient(API_KEY, MAX_REQ_FOR_KEY, TIMEOUT, BASE_URL)

def searchTroikaEntities(entity, K):

    is_company, company_numbers = isCompany(entity)
    if is_company is True:
        for company_number in company_numbers:
            searchTroikaCompany(company_number, K)
        return

    is_officer, officer_ids = isOfficer(entity)
    if is_officer is True:
        for officer_id in officer_ids:
            searchTroikaOfficer(officer_id, K)


def searchTroikaCompany(company_number, K):

    if K is 0: return

    if company_number in visited_companies:
        return

    visited_companies.append(company_number)

    # get company profile
    companyProfile = getCompanyProfile(company_number)
    log.debug(companyProfile)

    # get company's persons with significant control
    pscs = getCompanyPersonsWithSignificantControl(company_number)
    log.debug(pscs)

    # get company's officers
    companyOfficers = getCompanyOfficers(company_number)
    log.debug(companyOfficers)

    # for each officer call searchTroikaOfficer(entity, K-1)
    officer_ids = [officerLink.value.split('/')[2] for officerLink in parse('$.items[*].links.officer.appointments').find(companyOfficers)]
    for officer_id in officer_ids:
        searchTroikaOfficer(officer_id, K - 1)



def searchTroikaOfficer(officer_id, K):

    if K is 0: return

    if officer_id in visited_companies:
        return

    visited_officers.append(officer_id)

    # get the appointments
    appointments = getOfficerAppointments(officer_id)
    log.debug(appointments)

    # for each appointment get the company name and call searchTroikaCompany(company, K):
    appointments_company_numbers = parse('$.items[*].appointed_to.company_number').find(appointments)
    for company_number in appointments_company_numbers:
        searchTroikaCompany(company_number.value, K)

def isCompany(entity):

    # strip all spaces when querying
    params = {'q' : entity.replace(' ', '')}
    response = restClient.doRequest('/search/companies', params)

    number_of_results = parse('$.total_results').find(response)

    if number_of_results[0].value > 0:
        return True, parse('$.items[*].links[*].self').find(response)

    return False, None

def getCompanyProfile(company_number):

    response = restClient.doRequest('/company/' + company_number, None)
    return response


def getCompanyPersonsWithSignificantControl(company_number):

    response = restClient.doRequest('/company/' + company_number + '/persons-with-significant-control-statements', None)
    return response


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


searchTroikaEntities('Cascado AG', 2)