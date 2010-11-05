# bscrawler lite by Ian Lurie
# Huge kudos to BeautifulSoup
# lite version differs only in that it does not use database storage
#!/usr/bin/env python
import sys
import httplib
import urllib2
import urlparse
import string
from BeautifulSoup import BeautifulSoup, SoupStrainer
from time import gmtime, strftime, time


print "start time ",strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"\n\n\n"
try:
    root = sys.argv[1]
except IndexError:
    print "  Usage: ./bscrawler.py link"
    print "  Example: ./bscrawler.py http://www.portent.com/"
    exit()

linkz = []
crawled = []
errorz = []
imgz = []
counter = 0
start = time()
result=0

parsedRoot = urlparse.urlparse(root)

if parsedRoot.port == 80:
    hostRoot = parsedRoot.netloc[:-3]
else:
    hostRoot = parsedRoot.netloc

linkz.append(root)

conn = httplib.HTTPConnection(hostRoot) # open http request


for l in linkz:
	pagelinkz = []
	giffound = l.find('.gif')
	jpgfound = l.find('.jpg')
	pngfound = l.find('.png')
	pdffound = l.find('.pdf')
	conn = urllib2.urlopen(l) # get the url
	src = conn.read() # read page contents
	code = conn.code # read response code - later need to make this more sensible
	links = SoupStrainer('a') # grab all anchors
	imgs = SoupStrainer('img') # grab all img elements
	bs = BeautifulSoup(src, parseOnlyThese=links) # parse for anchors
	try:
		if (giffound == -1) & (jpgfound == -1) & (pngfound == -1) & (pdffound == -1): 
			print "Crawling\t",l,"\t",code
			# loop through all of the anchors found on the page
			# crawler only records the FIRST time it finds a link. If a link is on 20 pages
			# it will still only show up once in the log.
			for j in bs.findAll('a', {'href':True}):
				testresult = 0
				absUrl = urlparse.urljoin(l, j['href'])
				absUrl = absUrl.strip()
				parsedUrl = urlparse.urlparse(absUrl)
				# check for any images that snuck in via a link
				giffound = absUrl.find('.gif')
				jpgfound = absUrl.find('.jpg')
				pngfound = absUrl.find('.png')
				if (giffound == -1) & (jpgfound == -1) & (pngfound == -1):
					filetype = 1
				else:
					filetype = 2
				if parsedUrl.port == 80:
					hostUrl = parsedUrl.netloc[:-3]
				else:
					hostUrl = parsedUrl.netloc
					absUrl = urlparse.urlunparse((parsedUrl.scheme, hostUrl, parsedUrl.path, parsedUrl.params, parsedUrl.query, parsedUrl.fragment))
				if (parsedUrl.scheme == 'http') & \
				((parsedUrl.netloc.endswith('.' + hostRoot)) | (parsedUrl.netloc == hostRoot)) & \
				(absUrl not in linkz):
					tester = absUrl.find('#')
					if tester == -1:
						cleanUrl = absUrl.strip()
						print '\t' + cleanUrl + '\tpage'
						linkz.append(cleanUrl)
						counter = counter + 1
					else:
						counter = counter + 1
			
# now to try to grab some images on the same page
# the crawler records EVERY place images are found, not just the first. Long story, but we needed this at Portent.
			bsi = BeautifulSoup(src, parseOnlyThese=imgs)
			for i in bsi.findAll('img', {'src':True}):
				absUrl = urlparse.urljoin(l, i['src'])
				parsedUrl = urlparse.urlparse(absUrl)
				conn = urllib2.urlopen(absUrl) # get the url
				icode = conn.code # read response code 
				try:
					if parsedUrl.port == 80:
						hostUrl = parsedUrl.netloc[:-3]
					else:
						hostUrl = parsedUrl.netloc
					absUrl = urlparse.urlunparse((parsedUrl.scheme, hostUrl, parsedUrl.path, parsedUrl.params, parsedUrl.query, parsedUrl.fragment))
					if (parsedUrl.scheme == 'http') & \
						((parsedUrl.netloc.endswith('.' + hostRoot)) | (parsedUrl.netloc == hostRoot)):
						cleanUrl = absUrl.strip()
						cleanUrl = cleanUrl.replace('&','&amp;')
						print '\t',cleanUrl,'\timage','\t',icode
						imgz.append(cleanUrl)
						counter = counter + 1
				except:
					print sys.exc_info()
					pass
	except:
		print sys.exc_info()
		pass


print "Completed at ",strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()),"\n\n\n",counter," urls in ", (time() - start)
