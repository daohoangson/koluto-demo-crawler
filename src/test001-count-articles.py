import os
import crawling_config

def countArticles(dir):
	count = 0
	contents = os.listdir(dir)
	
	for item in contents:
		itemPath = dir + item
		if (os.path.isfile(itemPath)):
			# found a file
			if (item == '.gitignore'): continue
			if (item == '.DS_Store'): continue
			
			count += 1
			if (os.path.getsize(itemPath) == 0):
				print 'Empty file: %s' % itemPath
		elif (os.path.isdir(itemPath)):
			if (item == '.git'): continue
			
			# found a sub directory, recursively process it
			count += countArticles(itemPath + '/')
	
	if (count == 0):
		print 'Directory with no file: %s' % dir
	
	return count

def main():
	print 'Counting articles and looking for empty files...'
	#articles = countArticles(crawling_config.DIR_ARTICLES)
	#print 'Articles: %d' % articles
	
	print 'Counting parsed and looking for empty files...'
	parsed = countArticles(crawling_config.DIR_PARSED)
	print 'Parsed: %d' % parsed
	

if (__name__ == '__main__'):
	main()