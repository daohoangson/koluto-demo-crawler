import os
import sys
from BeautifulSoup import BeautifulSoup
import crawling_config

def lookForArticles(dir):
	"""Goes into specified directory and look for article files.
	Sub-directories will be processed also (recursively)"""
	contents = os.listdir(dir)
	
	for item in contents:
		itemPath = dir + item
		if (os.path.isfile(itemPath)):
			# found a file, parse it now
			if (item == '.gitignore'): continue
			if (item == '.DS_Store'): continue
			
			result = parseArticle(itemPath)
			
			if (result == False):
				print itemPath, (result != False)
		elif (os.path.isdir(itemPath)):
			# found a sub directory, recursively process it
			lookForArticles(itemPath + '/')

def parseArticle(articlePath):
	"""Parses article from the given path. Returns the article contents as str
	if it can be found or False if fails."""
	f = open(articlePath, 'r')
	contents = f.read()
	f.close()
	
	bs = BeautifulSoup(contents)
	
	# looks for all <p> tags which contain period or comma
	pTags = bs.findAll('p')
	pTagsFiltered = []
	for pTag in pTags:
		pTagStr = str(pTag)
		if (pTagStr.find('.') != -1 or pTagStr.find(',') != -1):
			pTagsFiltered.append(pTag)
	
	# find common parents
	parentTags = []
	for pTag in pTagsFiltered:
		parent = pTag.parent
		if (parent not in parentTags):
			parentTags.append(parent)
	
	# looking for a final answer
	finalAnswer = False
	if (len(parentTags) == 1):
		# there is only one parent tag found
		# so easy, just pick it as the final answer
		finalAnswer = parentTags[0]
	else:
		# there are more than one parent tags found
		# we will have to find the one contains the largest number of pTagsFiltered
		countMax = -1
		for parentTag in parentTags:
			count = 0
			
			# count pTagsFiltered
			for pTag in pTagsFiltered:
				if (pTag in parentTag.contents):
					count += 1
			
			# assign the answer if pTagFiltered count is larger than current max count
			if (count > countMax):
				finalAnswer = parentTag
				countMax = count
	
	if finalAnswer != False:
		# we got a final answer, returns str of it
		return str(finalAnswer)
	else:
		# no final answer is found, returns False
		return False

def main():
	lookForArticles(crawling_config.DIR_ARTICLES)
	
	print 'Bye bye'

if (__name__ == '__main__'):
	main()