import base64
import httplib
import urllib

class GeoServer(object):
	def __init__(self, server, port, username, password):
		self.server = server
		self.port = port
		self.auth = 'Basic ' + base64.encodestring('%s:%s' % (username, password)).strip()

	def make_request(self, need_auth, url, body=None):
		conn = httplib.HTTPConnection(self.server, self.port)
		headers = {
			'Content-type':'application/xml',
			'Accept':'application/xml,text/plain'
		}

		if need_auth:
			headers['Authorization'] = self.auth

		method = 'POST' if body else 'GET'
		conn.request(method, url, body, headers)
		return conn.getresponse()

	def wfs(self, gml):
		return self.make_request(False, '/geoserver/wfs', gml.toxml())

