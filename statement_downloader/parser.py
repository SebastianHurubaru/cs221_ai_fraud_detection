import urllib2
import re
import zipfile
import os

from bs4 import BeautifulSoup
from urlparse import urljoin

class WebsiteScraper(object):
	"""A class that allows parsing of a website and downloading all
	files that match a pattern.

	Attributes
	----------
	NO_EXTRACT: int
		An integer that specifies no extraction should take place.
	EXTRACT: int
		An integer that specifies extractio should take place.
	starting_page: str
		Part of the website address that's also joined with the file address.
	"""

	NO_EXTRACT = 0
	EXTRACT = 1
	def __init__(self, starting_page):
		if starting_page:
			self.starting_page = starting_page if starting_page else ''

	def download_all(self, website, regexp_str, directory, extract = 0):
		"""
		Parses a website and downloads all files that fit a specific
		pattern.

		Parameters
		----------
		website: str
			Address of the website or part of it. This will be joined with
			self.starting_page and be used to connect to the source of
			files we want to download.
		regexpr_str: str
			A string that specifies what files the function should look for
			when parsing the website. An exact match is needed in order for
			a file to be downloaded.
		directory: str
			A folder where the donwloaded files should be saved in. Could be
			both relative and absolute.
		extract: int
			An integer that specifies whether the files should be extracted
			on the fly after being downloaded.
		"""

		try:
			os.makedirs(directory)
		except OSError as e:
			if e.errno == os.errno.EEXIST:
				pass
			else:
				raise

		reg_exp = re.compile(regexp_str)
		page = urllib2.urlopen(urljoin(self.starting_page, website))

		soup = BeautifulSoup(page, 'html.parser')
		a_tags = soup.find_all('a')
		for tag in a_tags:
			link = tag['href']
			if reg_exp.match(link):
				path = os.path.join(directory, link)
				print 'Downloading ' + link
				rq = urllib2.Request(urljoin(self.starting_page, link))
				res = urllib2.urlopen(rq)

				if not os.path.exists(path):
					try:
						os.makedirs(os.path.dirname(path))
					except OSError as e:
						if e.errno != os.errno.EEXIST:
							raise

				with open(path, 'wb') as file:
					file.write(res.read())

				if extract:
					zip_ref = zipfile.ZipFile(path)
					zip_ref.extractall(directory)
					zip_ref.close()

					os.remove(path)

				res.close()

starting_page = 'http://download.companieshouse.gov.uk/'

regexp_daily = r'Accounts_Bulk_Data-20\d{2}-\d{2}-\d{2}\.zip'
website_daily = '/en_accountsdata.html'


regexp_monthly = r'Accounts_Monthly_Data.*20\d{2}\.zip'
website_monthly = '/en_monthlyaccountsdata.html'

regexp_historic = r'archive/Accounts_Monthly_Data.*20\d{2}\.zip'
website_historic = '/historicmonthlyaccountsdata.html'


directory = "pdfs/"

scraper = WebsiteScraper(starting_page)

scraper.download_all(website_daily, regexp_daily, directory, WebsiteScraper.NO_EXTRACT)
#scraper.download_all(website_monthy, regexp_monthly, directory, WebsiteScraper.NO_EXTRACT)
#scraper.download_all(website_historic, regexp_historic, directory, WebsiteScraper.NO_EXTRACT)
