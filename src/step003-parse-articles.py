import os
import sys
import re, htmlentitydefs
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
from datetime import datetime
import crawling_config
from koluto import Koluto

def getParsedFile(articleFile):
	return articleFile.replace(crawling_config.DIR_ARTICLES, crawling_config.DIR_PARSED)

def fileExists(filePath):
	try:
		f = open(filePath, 'r')
		f.close()

		return True
	except IOError:
		return False

def textOf(soup):
	def visible(soup):
		if (soup.parent.name in ['style', 'script']):
			return False
		elif re.match('<!--.*-->', str(soup), re.DOTALL):
			return False
		return True
	
	texts = soup.findAll(text=True)
	visibleTexts = filter(visible, texts)
	textOf = u' '.join(visibleTexts)
	return textOf
	
def submitArticle(itemPath, parsedPath):
	koluto = Koluto()
	koluto.setAuthInfo('sondh', '1')
	
	extraData = []
	sections = []
	
	mtime = os.path.getmtime(itemPath)
	timeobj = datetime.fromtimestamp(mtime)
	sections.append(timeobj.strftime('%Y%m%d'))
	
	f = open(parsedPath, 'r')
	contents = f.read()
	f.close()
	
	koluto.submitDocument(contents, extraData, sections)

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
			
			parsedFile = getParsedFile(itemPath)
			if (fileExists(parsedFile)):
				submitArticle(itemPath, parsedFile)
				continue
			
			result = parseArticle(itemPath)
			
			if (result != False):
				# only save result if it's parsable
				try:
					os.makedirs(os.path.dirname(parsedFile))
				except OSError:
					# the directory exists
					pass
				
				try:
					f = open(parsedFile, 'w')
					f.write(result.encode('utf-8'))
					f.close()
					
					submitArticle(itemPath, parsedFile)
				except:
					exit(1)
					pass
			else:
				print "Unable to parse " + itemPath
		elif (os.path.isdir(itemPath)):
			# found a sub directory, recursively process it
			if (item == '.git'): continue
			
			lookForArticles(itemPath + '/')

def parseArticle(articlePath):
	"""Parses article from the given path. Returns the article contents as str
	if it can be found or False if fails."""
	f = open(articlePath, 'r')
	contents = f.read()
	f.close()
	
	bs = BeautifulSoup(contents, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
	
	# looks for all <p> tags which contain period or comma
	pTags = bs.findAll([u'p', u'span', u'blockquote'])
	pTagsFiltered = []
	for pTag in pTags:
		pTagStr = textOf(pTag)
		# if (pTagStr.find('.') != -1 or pTagStr.find(',') != -1):
		if (pTagStr.find('.') != -1):
			# try to get to the highest level tag with single child
			while len(pTag.parent.contents) == 1:
				pTag = pTag.parent
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
		# return unescape(u''.join([unicode(pTag) for pTag in pTagsFiltered if pTag in finalAnswer.contents]))
		return textOf(finalAnswer)
	else:
		# no final answer is found, returns False
		return False

def main():
	lookForArticles(crawling_config.DIR_ARTICLES)
	
	print 'Bye bye'

if (__name__ == '__main__'):
	main()