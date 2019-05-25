import requests
import json
import time

from config import *

log = logging.getLogger('rest')

class RESTClient:

    def __init__(self, api_key, max_req, timeout, base_url):
        self.api_key = api_key
        self.max_req = max_req
        self.timeout = timeout
        self.base_url = base_url

        self.number_of_req = 0

        self.session = requests.Session()
        self.session.auth = (self.api_key, '')

    def doTimeout(self):

        self.number_of_req = 0;
        time.sleep(self.timeout)

    def doRequest(self, partial_url, params):

        self.number_of_req += 1

        if self.number_of_req >= self.max_req:
            self.doTimeout()

        url = self.base_url + partial_url

        response = self.session.get(url, params=params)
        responseJson = response.json()
        log.debug(responseJson)

        return responseJson




