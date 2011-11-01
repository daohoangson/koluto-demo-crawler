import os
import crawling_config

def countArticles(dir):
	count = 0
	contents = os.listdir(dir)
	
	for item in contents:
		itemPath = dir + '/' + item
		if (os.path.isfile(itemPath)):
			# found a file
			count += 1
			if (os.path.getsize(itemPath) == 0):
				print 'Empty file: %s' % itemPath
		elif (os.path.isdir(itemPath)):
			# found a sub directory, recursively process it
			count += countArticles(itemPath)
	
	return count

def main():
	print 'Counting articles and looking for empty file...'
	articles = countArticles(crawling_config.DIR_ARTICLES)
	print 'Articles: %d' % articles

if (__name__ == '__main__'):
	main()