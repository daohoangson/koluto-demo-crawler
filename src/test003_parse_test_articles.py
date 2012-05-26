import crawling_config
from step003_parse_articles import lookForArticles

crawling_config.DIR_ARTICLES = crawling_config.DIR_TEST_ARTICLES
crawling_config.DIR_PARSED = crawling_config.DIR_TEST_PARSED

def main():
	parsed = lookForArticles(
		crawling_config.DIR_TEST_ARTICLES,
		crawling_config.DIR_TEST_PARSED,
		crawling_config.DIR_TEST_ARTICLES,
		False
	)
	
	print 'Parsed %d files!' % parsed

if (__name__ == '__main__'):
	main()