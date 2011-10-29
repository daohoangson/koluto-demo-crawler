import glob
import os
import resource
import time
import urllib
import xml.etree.ElementTree
from crawling_lock import FileLock
from crawling_queue import FileQueue

DIR_FEED_LISTS = './feed-lists/'
DIR_LOCKS = './locks/'
DIR_QUEUE = './queue/'

def DEBUG(msg):
	print msg

def readFeed(feedUrl, feedMode, feedModeConfig):
	"""Processes feed from its url, mode and mode configuration. Return a list of links"""
	DEBUG('Reading %s (mode: %s)' % (feedUrl, feedMode))
	feedContents = urllib.urlopen(feedUrl).read()
	links = []
	
	if (feedMode == 'XPath'):
		# we are processing XPath mode
		# in this mode, the feed contents will be treated as XML
		# then we will find all elements which match the XPath in the feedModeConfig
		xmlObj = xml.etree.ElementTree.fromstring(feedContents)
		links = [link.text for link in xmlObj.findall(feedModeConfig)]
	
	return links

# get the list of feeds from the 'feeds' directory in the same directory with this script
feedLists = glob.glob(DIR_FEED_LISTS + '*')
# get the file queue for this run (this will lock the queue until it finishes)
feedQueue = FileQueue(DIR_QUEUE, DIR_LOCKS)

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
			links = readFeed(feedUrl.strip(), feedMode, feedModeConfig)
			feedQueue.saveList(links)
		
		# removes the lock for other sessions
		feedLock.unlock()

# free the file queue
feedQueue.close()