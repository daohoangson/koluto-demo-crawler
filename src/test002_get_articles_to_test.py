import os
import shutil
import random
import crawling_config
from step003_parse_articles import fileExists

def lookForArticlesAndCopyTo(source, target, dir, level = 1):
	"""Goes into specified directory and look for article files.
	Sub-directories will be processed also (recursively)"""
	contents = os.listdir(dir)
	internal_count = 0;
	
	for item in contents:
		itemPath = dir + item
		
		if (os.path.isfile(itemPath)):
			# found a file, copy it now
			if (item == '.gitignore'): continue
			if (item == '.DS_Store'): continue
			
			r = random.randint(0, 1)
			if (r == 0):
				# bad luck, not copy this file
				continue;
			
			targetPath = itemPath.replace(source, target);
			if (fileExists(targetPath) == False):
				try:
					os.makedirs(os.path.dirname(targetPath))
				except OSError:
					# the directory exists
					pass
				
				try:
					shutil.copy2(itemPath, targetPath)
					print 'copied %s to %s ' % (itemPath, targetPath)
					internal_count += 1
				except:
					# unable to copy file
					pass
		elif (os.path.isdir(itemPath)):
			# found a sub directory, recursively process it
			if (item == '.git'): continue
			
			internal_count += lookForArticlesAndCopyTo(source, target, itemPath + '/', level + 1)
		
		if ((level > 1) and (internal_count > 10)):
			break
	
	return internal_count
	
def main():
	copied = lookForArticlesAndCopyTo(
		crawling_config.DIR_ARTICLES,
		crawling_config.DIR_TEST_ARTICLES,
		crawling_config.DIR_ARTICLES
	)

	print 'Copied %d files!' % copied

if (__name__ == '__main__'):
	main()