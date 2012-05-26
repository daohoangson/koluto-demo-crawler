import urllib, urllib2
import httplib
import base64

class Koluto:
	host = '127.0.0.1'
	port = 29690
	rootUrl = ''
	username = False
	password = False
	
	def __init__(self, host='127.0.0.1', port=29690):
		self.host = host
		self.port = port
		self.rootUrl = 'http://%s:%d' % (self.host, self.port)
	
	def setAuthInfo(self, username, password):
		self.username = username
		self.password = password
	
	def submitDocument(self, text, extraData=[], sections=[]):
		request = urllib2.Request(
			'%s/%s' % (self.rootUrl, 'documents'),
			self.urlEncode({
				'_responseFormat': 'json',
				'text': text,
				'extraData[]': extraData,
				'sections[]': sections
			}),
		)
		
		if (self.username != False and self.password != False):
			base64str = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
			request.add_header('Authorization', 'Basic %s' % base64str)
		
		try:
			handle = urllib2.urlopen(request)
			contents = handle.read()
		except IOError:
			contents = False
		except httplib.HTTPException:
			contents = False
		# we may catch all kind of exception but it's not a good practice...
		
		return contents
	
	def urlEncode(self, params={}):
		if not isinstance(params, dict): 
			raise Exception("You must pass in a dictionary!")
		params_list = []
		for k,v in params.items():
			if isinstance(v, list):
				params_list.extend([(k, x) for x in v])
			else:
				params_list.append((k, v))
		
		return urllib.urlencode(params_list)