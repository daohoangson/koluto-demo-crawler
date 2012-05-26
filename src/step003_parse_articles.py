import os
import sys
import re, htmlentitydefs
import random
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup, Comment
from datetime import datetime
import crawling_config
from koluto import Koluto
import MySQLdb as mdb

conn = None

def getParsedFile(source, target, articleFile):
	return articleFile.replace(source, target)

def fileExists(filePath):
	try:
		f = open(filePath, 'r')
		f.close()

		return True
	except IOError:
		return False

def textOf(soup, getTag):
	def visible(soup):
		if (soup.parent.name in ['style', 'script']):
			return False
		# not needed to check for comment because they are stripped out at the beginning already
		# elif re.match('<!--.*-->', str(soup), re.DOTALL):
			# return False
		return True
	
	if (getTag):
		texts = soup
		visibleTexts = filter(visible, texts)
		textOf = u' '.join(map(unicode, visibleTexts))
	else:
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

	return koluto.submitDocument(contents, extraData, sections)

def lookForArticles(source, target, dir, submit = False):
	"""Goes into specified directory and look for article files.
	Sub-directories will be processed also (recursively)"""
	contents = os.listdir(dir)
	internal_count = 0
	
	for item in contents:
		itemPath = dir + item
		if (os.path.isfile(itemPath)):
			# found a file, parse it now
			if (item == '.gitignore'): continue
			if (item == '.DS_Store'): continue
			
			parsedFile = getParsedFile(source, target, itemPath)
			kolutoSubmited = False
			dbSubmited = False
			
			if (fileExists(parsedFile)):
				if (submit):
					kolutoSubmited = submitArticle(itemPath, parsedFile)
			else:
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
					
						if (submit):
							submitArticle(itemPath, parsedFile)
					
						internal_count += 1
					except:
						print "Problem working with " + itemPath
						pass
				else:
					print "Unable to parse " + itemPath
			
			if (submit and kolutoSubmited and conn):
				# submit to our database now
				try:
					cursor = conn.cursor()
					cursor.execute("\
						INSERT INTO tbl_article\
						(article_source, article_text)\
						VALUES\
						(%s, %s)\
					", (itemPath, contents))

					cursor.close()

					dbSubmited = True
				except mdb.Error:
					dbSubmited = False
			
			print (itemPath, kolutoSubmited, dbSubmited)
		elif (os.path.isdir(itemPath)):
			# found a sub directory, recursively process it
			if (item == '.git'): continue
			
			internal_count += lookForArticles(source, target, itemPath + '/', submit)
	
	return internal_count

def parseArticle(articlePath):
	"""Parses article from the given path. Returns the article contents as str
	if it can be found or False if fails."""
	f = open(articlePath, 'r')
	contents = f.read()
	f.close()
	
	try:
		bs = BeautifulSoup(contents, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
	except TypeError:
		return False
	
	# strips comments
	comments = bs.findAll(text=lambda text:isinstance(text, Comment))
	[comment.extract() for comment in comments] # bye bye!
	
	# looks for tags which contain period or comma
	pTags = bs.findAll([u'p', u'span', u'blockquote', u'div'])
	pTagsFiltered = []
	for pTag in pTags:
		if (pTag.name == 'div'):
			# get text from a <div> differently
			pTagStr = u''
			pDivTexts = pTag.findAll(text=True, recursive=False)
			if (pDivTexts != None):
				pTagStr = u' '.join(pDivTexts)
		else:
			pTagStr = textOf(pTag, False)
		
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
	
	# filter unwanted tags
	for parentTag in parentTags:
		unwantedTags = parentTag.findAll([u'table', u'a'])
		for unwantedTag in unwantedTags:
			belongsToAFilteredTag = False
			tmp = unwantedTag
			
			# go up the parse tree
			try:
				while (tmp.parent != parentTag):
					if (tmp.parent in pTagsFiltered):
						belongsToAFilteredTag = True
						break # while (tmp.parent != None):
					tmp = tmp.parent
			except:
				# may happen if we remove <table /> contain some <a /> for example
				pass
			
			if (belongsToAFilteredTag == False):
				# oops, this unwanted tag is not belong to any of the filtered tags
				# it must come from parent tags, remove it!
				unwantedTag.extract() # bye bye
	
	# looking for a final answer
	finalAnswer = False
	if (len(parentTags) == 1):
		# there is only one parent tag found
		# so easy, just pick it as the final answer
		finalAnswer = parentTags[0]
	else:
		# there are more than one parent tags found
		# we will have to find the biggest one
		lenMax = -1
		for parentTag in parentTags:
			lenThis = len(textOf(parentTag, False));
			
			# assign the answer if pTagFiltered count is larger than current max count
			if (lenThis > lenMax):
				finalAnswer = parentTag
				lenMax = lenThis
	
	if finalAnswer != False:
		# we got a final answer, returns it
		return textOf(finalAnswer, True)
	else:
		# no final answer is found, returns False
		return False

def main():
	global conn
	
	try:
		conn = mdb.connect(
			host=crawling_config.MYSQL_HOST,
			user=crawling_config.MYSQL_USER,
			passwd=crawling_config.MYSQL_PASSWORD,
			db=crawling_config.MYSQL_DATABASE,
			charset='utf8'
		)
		
		if (conn):
			conn.autocommit(True) # make it commit automatically so we can Ctrl+C anytime
			
			lookForArticles(crawling_config.DIR_ARTICLES, crawling_config.DIR_PARSED, crawling_config.DIR_ARTICLES, True)
			conn.close()
		else:
			print "No MySQL connection?"
	except mdb.Error, e:
		print "Error %d: %s" % (e.args[0],e.args[1])
	
	print 'Bye bye'

if (__name__ == '__main__'):
	main()