import glob
import os
import re
import signal
import sys
import time
import urllib
import urlparse
import crawling_config
from crawling_lock import FileLock
from crawling_queue import FileQueue

FLAG_SLEEPING = False
FLAG_EXIT_NOW = False

def getLinkFile(link):
	parsed = urlparse.urlparse(link)
	
	path = parsed.path
	
	if (len(os.path.basename(link)) == 0):
		# this link is the SEO-friendly link
		# there is no filename, make the last directory name the filename
		path = os.path.dirname(path)
	
	return crawling_config.DIR_ARTICLES \
		+ parsed.netloc.replace(':', '_') \
		+ path \
		+ re.sub(r'[^a-zA-Z0-9_\.]', '_', parsed.query)

def fileExists(linkFile):
	try:
		f = open(linkFile, 'r')
		f.close()
		
		return True
	except IOError:
		return False

def fetchLink(link, linkFile):
	dir = os.path.dirname(linkFile)
	
	try:
		os.makedirs(dir)
	except OSError:
		# the directory exists
		pass
	
	try:
		contents = urllib.urlopen(link).read()	
		
		f = open(linkFile, 'w')
		f.write(contents)
		f.close()
		
		# print "\a";
	except:
		pass

def main():
	while (True):
		# get the file queue for this run (this will lock the queue until it finishes)
		feedQueue = FileQueue(crawling_config.DIR_QUEUE, crawling_config.DIR_LOCKS, 'r')
		links = feedQueue.getItems()
		
		# goes through links
		for link in links:
			linkFile = getLinkFile(link)
			
			if (fileExists(linkFile) == False):
				# the link is not fetched, we will do it now
				crawling_config.DEBUG('Fetching %s.' % link)
				fetchLink(link, linkFile)
		
		feedQueue.delete()
		
		crawling_config.DEBUG('Sleeping for %d seconds' % crawling_config.SLEEP_TIME)
		time.sleep(crawling_config.SLEEP_TIME)
				
	print 'Bye bye'

def signalHandler(signal, frame):
	print 'SIGINT received. Exiting immediately.'
	sys.exit(1)

if (__name__ == '__main__'):
	signal.signal(signal.SIGINT, signalHandler)
	main()
