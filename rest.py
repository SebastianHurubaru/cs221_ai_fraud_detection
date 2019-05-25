import requests
import json
import time

from config import *

log = logging.getLogger('rest')

class RESTClient:

    def __init__(self, api_keys, max_req, timeout, base_url):
        self.api_keys = api_keys
        self.max_req = max_req
        self.timeout = timeout
        self.base_url = base_url

        self.number_of_max_req = 0
        self.key_idx = 0

        self.session = requests.Session()

    def doTimeout(self):

        time.sleep(self.timeout)

    def getNextApiKey(self):

        if self.key_idx == len(self.api_keys):
            self.key_idx = 0
            self.doTimeout()

        self.session.auth = (self.api_keys[self.key_idx][0], '')
        self.number_of_max_req = self.api_keys[self.key_idx][1]

        self.key_idx += 1


    def doRequest(self, partial_url, params):

        self.number_of_max_req -= 1

        if self.number_of_max_req <= 0:
            self.getNextApiKey()

        url = self.base_url + partial_url

        response = self.session.get(url, params=params)
        responseJson = response.json()
        log.debug(responseJson)

        return responseJson




