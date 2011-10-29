import glob
import os
import resource
import time
import urllib
import xml.etree.ElementTree
from crawling_lock import FileLock

DIR_FEED_LISTS = './feed-lists/'
DIR_LOCKS = './locks/'
DIR_QUEUE = './queue/'

def DEBUG(msg):
	print msg

def readFeed(feedUrl, feedMode, feedModeConfig):
	"""Process feed from its url, mode and mode configuration"""
	DEBUG('Reading %s (mode: %s)' % (feedUrl, feedMode))
	feedContents = urllib.urlopen(feedUrl).read()
	
	if (feedMode == 'XPath'):
		# we are processing XPath mode
		# in this mode, the feed contents will be treated as XML
		# then we will find all elements which match the XPath in the feedModeConfig
		xmlObj = xml.etree.ElementTree.fromstring(feedContents)
		links = [link.text for link in xmlObj.findall(feedModeConfig)]
		
		if (len(links) > 0):
			# we found some links, add to queue now
			queueFile = open(PATH_QUEUE, 'a')
			queueFile.write('\n'.join(links))
			queueFile.close()
			DEBUG('Queued %d links.' % len(links))

# get the list of feeds from the 'feeds' directory in the same directory with this script
feedLists = glob.glob(DIR_FEED_LISTS + '*')

# goes through feeds
for feedList in feedLists:
	feedLock = FileLock(DIR_LOCKS + os.path.basename(feedList))
	
	if (feedLock.isLocked() == False):
		# the feed is not locked atm, we may proceed...
		
		# but first, we have to lock it
		feedLock.lock()
		
		DEBUG('Processing %s' % (feedList))
		feedFile = open(feedList, 'r')
		feedUrls = feedFile.readline().strip().split(',')
		feedMode = feedFile.readline().strip()
		feedModeConfig = feedFile.readline().strip()
		
		for feedUrl in feedUrls:
			readFeed(feedUrl.strip(), feedMode, feedModeConfig)
		
		# removes the lock for other sessions
		feedLock.unlock()
