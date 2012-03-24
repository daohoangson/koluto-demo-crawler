import glob
import os
import resource
import signal
import sys
import time
import urllib
import xml.etree.ElementTree
import crawling_config
from crawling_lock import FileLock
from crawling_queue import FileQueue

FLAG_SLEEPING = False
FLAG_EXIT_NOW = False

def readFeed(feedUrl, feedMode, feedModeConfig):
	"""Processes feed from its url, mode and mode configuration. Return a list of links"""
	crawling_config.DEBUG('Reading %s (mode: %s)' % (feedUrl, feedMode))
	
	links = []
	
	try:
		feedContents = urllib.urlopen(feedUrl).read()
		
		if (feedMode == 'XPath'):
			# we are processing XPath mode
			# in this mode, the feed contents will be treated as XML
			# then we will find all elements which match the XPath in the feedModeConfig
			xmlObj = xml.etree.ElementTree.fromstring(feedContents)
			links = [link.text for link in xmlObj.findall(feedModeConfig)]
			crawling_config.DEBUG('Found %d links.' % len(links))
	except:
		crawling_config.DEBUG('Exception happens!')
		pass
	
	return links

def main():
	global FLAG_SLEEPING # will be set True if sleeping
	
	# get the list of feeds from the 'feeds' directory in the same directory with this script
	feedLists = glob.glob(crawling_config.DIR_FEED_LISTS + '*')
	
	while (True):
		# get the file queue for this run (this will lock the queue until it finishes)
		feedQueue = FileQueue(crawling_config.DIR_QUEUE, crawling_config.DIR_LOCKS)
		saved = 0

		# goes through feeds
		for feedList in feedLists:
			feedLock = FileLock(crawling_config.DIR_LOCKS + os.path.basename(feedList))
	
			if (feedLock.isLocked() == False):
				# the feed is not locked atm, we may proceed...
				# but first, we have to lock it
				feedLock.lock()

				try:
					feedFile = open(feedList, 'r')
					crawling_config.DEBUG('Processing %s' % feedList)
					
					feedUrls = feedFile.readline().strip().split(',')
					feedMode = feedFile.readline().strip()
					feedModeConfig = feedFile.readline().strip()
		
					for feedUrl in feedUrls:
						links = readFeed(feedUrl.strip(), feedMode, feedModeConfig)
						saved += feedQueue.saveList(links)
				except IOError:
					pass
		
				# removes the lock for other sessions
				feedLock.unlock()
			else:
				# oops, it's locked atm
				crawling_config.DEBUG('Bypassed %s because it is being locked.' % feedList)

		# frees the file queue
		feedQueue.close()
		
		crawling_config.DEBUG('Saved %d links to queue.' % saved)
		
		# checks if SIGINT is sent to this script
		if (FLAG_EXIT_NOW):
			print 'Stopping now!'
			break
		
		FLAG_SLEEPING = True
		crawling_config.DEBUG('Sleeping for %d seconds' % crawling_config.SLEEP_TIME)
		time.sleep(crawling_config.SLEEP_TIME)
		FLAG_SLEEPING = False
	
	print 'Bye bye'

def signalHandler(signal, frame):
	global FLAG_EXIT_NOW # will be set True if can not exit immediately
	
	if (FLAG_SLEEPING):
		# the main() is sleeping (between cycles)
		# we can safely exit now
		print 'SIGINT received. Exiting immediately.'
		sys.exit(1)
	else:
		# a cycle is running, we will schedule a stop
		FLAG_EXIT_NOW = True
		print 'SIGINT received. Will halt once the current cycle is complete...'

if (__name__ == '__main__'):
	signal.signal(signal.SIGINT, signalHandler)
	main()