#!/usr/bin/env python
import requests, math, uuid, datetime, os, time, traceback
from bs4 import BeautifulSoup
from random import randint

### USER VARIABLES ###
LINK_LIMIT = 0 # Amount of links you're looking to get
OFFSET = 0 # Where to start requesting links
CATEGORY = 'algemeen'

# In seconds
UPPER_WAIT_LIMIT = 3
LOWER_WAIT_LIMIT = 1

# Setup
ROOT = "http://www.nu.nl"

# API endpoint
REQUEST_URL = "http://www.nu.nl/block/json/articlelist"

PAYLOAD = {
	'footer' : 'ajax',
	'section' : CATEGORY,
	'limit' : 8,
	'template' : 'plain',
	'offset' : OFFSET,
	'show_tabs' : 0,
}

# For maximum S T E A L T H M O D E
HEADERS = requests.utils.default_headers()
HEADERS.update(
	{
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
	}
)

LIST = []

if (LINK_LIMIT == 0):
	print('Going to attempt to grab all articles in section ' + str(PAYLOAD['section']))
	REQUESTS = 1000000000
else:
	REQUESTS = math.ceil(LINK_LIMIT/7)
	TOTAL_LINKS = REQUESTS*7
	print('Gonna get you ' + str(TOTAL_LINKS) + ' links (for a total of ' + str(REQUESTS) + ' requests) from section ' + str(PAYLOAD['section']))

now = datetime.datetime.now()
dirname = now.strftime("%H-%M-%S")
WORKPATH = os.getcwd() + '/data/' + dirname
os.makedirs(WORKPATH)

START_TIME = time.time()
# Helper methods
def clean_request(response):
	response = response.replace('\\n', ' ') # Removing newlines
	response = response.replace('\\', ' ') # Removing quote escape shit
	response = response.replace('\xa0', ' ') # Yay for Python encoding stuff
	return response

def extract_links(response):
	soup = BeautifulSoup(response, "html.parser")
	sublist = []
	for link in soup.find_all('a'):
		if not 'Geen artikelen gevonden' in str(link):
			try:
				if (
					link.get('href').startswith('#') == False # Filter out anchors
					):
				    LIST.append(link.get('href')) 
			except:
				print('Something went wrong when trying to go through the link: ' + str(link))
				traceback.print_exc()
		else:
			print('End of article list apparently, breaking link fetch...')
			return 1
	return 0

def extract_article_header(soup):
	header = soup.find_all('div', class_='item-excerpt')[0]
			
	return clean_request(header.get_text().strip())

def extract_article_text(soup):
	for divs in soup.find_all('div', {'data-type':'article.body'}):
		articleBody = divs.find_all('div', class_='block-content')[0]

		# Only keep the p tags
		divs = articleBody.find_all('div')
		for hit in divs:
			hit.decompose()
		
	return clean_request(articleBody.get_text().strip())

# Main
if __name__ == "__main__":
	print('Main initialised')
	os.makedirs(WORKPATH + '/' + PAYLOAD['section'])
	for i in range(0, REQUESTS):
		PAYLOAD['offset'] = OFFSET + i*int(PAYLOAD['limit'])
		print('Sending request for iteration: ' + str(i+1))
		time.sleep(randint(LOWER_WAIT_LIMIT,UPPER_WAIT_LIMIT))
		try:
			result = requests.get(REQUEST_URL, params=PAYLOAD, headers=HEADERS)
			if result.status_code == 200:
				responseBody = result.text
				responseBody = clean_request(responseBody)
				linkExtract = extract_links(responseBody)
				with open(WORKPATH + '/' + PAYLOAD['section'] + '/links.txt', "a") as linksFile:
					for link in LIST:
						linksFile.write(link + "\n")
				if linkExtract == 1:
					print('Looks like all articles were found. Continuing to text extraction...')
					break
				LIST.clear()
		except:
			print('Error, status code was ' + str(result.status_code))
			traceback.print_exc()

	print('Link list established, extracting text...')
	fileHandle = "1"
	filePath = WORKPATH + '/' + PAYLOAD['section'] + '/' + fileHandle + '.txt'
	loopcounter = 0

	with open(WORKPATH + '/' + PAYLOAD['section'] + '/links.txt') as links:
		LINKLIST = links.readlines()

	LINKLIST = [x.strip() for x in LINKLIST]
	TOTAL_LINKS = len(LINKLIST)
	
	for index,link in enumerate(LINKLIST):
		time.sleep(randint(LOWER_WAIT_LIMIT,UPPER_WAIT_LIMIT))
		try:
			response = requests.get(ROOT + link, headers=HEADERS)
			if response.status_code == 200:
				clean_response = clean_request(response.text)
				soup = BeautifulSoup(clean_response, "html.parser")

				if os.path.isfile(filePath):
					sizeInMB = os.path.getsize(filePath)/1000000
					if sizeInMB > 500:
						fileHandle = str(int(fileHandle) + 1)
						filePath = WORKPATH + '/' + PAYLOAD['section'] + '/' + fileHandle + '.txt'

				with open(filePath, "a") as contentfile:
					contentfile.write('\n')
					contentfile.write(extract_article_header(soup))
					contentfile.write(' ')
					contentfile.write(extract_article_text(soup))
					contentfile.write('\n')

				print('(' + str(index+1) + '/' + str(TOTAL_LINKS) + ') Write succesful for url: ' + str(link))
				loopcounter = index
		except:
			print('Error in request, response code was: ' + str(response.status_code))
			print('Index was ' + str(index) + ' when this error occurred.')
			print('URL was: ' + str(link) )
			errorFilePath = WORKPATH + '/' + PAYLOAD['section'] + '/errorlinks.txt'
			with open(errorFilePath, "a") as errorfile:
				errorfile.write('\n')
				errorfile.write(str(link))
			traceback.print_exc()

	elapsedTime = math.ceil(time.time() - START_TIME)
	print('Done! Crawled ' + str(loopcounter) + ' links!')
	print('Time elapsed: ' + str(elapsedTime) + 's or ' + str(elapsedTime/60) + 'm')

