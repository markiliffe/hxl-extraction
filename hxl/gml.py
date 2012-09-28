import base64
import cgi
import httplib
import json
import lxml.etree as et

from hxl import HXLException
import hxl.wkt

gml_namespace = 'http://www.opengis.net/gml'
topp_namespace = 'http://www.openplans.org/topp'
wfs_namespace = 'http://www.opengis.net/wfs'

NSMAP = {
	'gml':gml_namespace,
	'topp':topp_namespace,
	'wfs':wfs_namespace
}

def gmlElement(tag):
	return et.Element('{%s}%s' % (gml_namespace, tag))

def gmlSubElement(parent, tag):
	return et.SubElement(parent, '{%s}%s' % (gml_namespace, tag))

def toppElement(tag):
	return et.Element('{%s}%s' % (topp_namespace, tag))

def toppSubElement(parent, tag):
	return et.SubElement(parent, '{%s}%s' % (topp_namespace, tag))

def wfsElement(tag, **kwargs):
	return et.Element('{%s}%s' % (wfs_namespace, tag), **kwargs)

def wfsSubElement(parent, tag):
	return et.SubElement(parent, '{%s}%s' % (wfs_namespace, tag))

def create_coordinates(coords):
	'''Convert list of (long,lat) pairs into one space separated string'''
	coords_string_array = []
	for (x, y) in coords:
		coords_string_array.append('%s,%s' % (x, y))

	coords_string = ' '.join(coords_string_array)

	coordinates = gmlElement('coordinates')
	coordinates.text = coords_string

	return coordinates

def gml_multipolygon(polygons):
	multiPolygon = gmlElement('MultiPolygon')
	multiPolygon.attrib['srsName'] = 'http://www.opengis.net/gml/srs/epsg.xml#4326'

	for polygon_geometry in polygons:
		polygonMember = gmlSubElement(multiPolygon, 'polygonMember')
		polygon = gmlSubElement(polygonMember, 'Polygon')
		outerBoundaryIs = gmlSubElement(polygon, 'outerBoundaryIs')

		linearRing = gmlSubElement(outerBoundaryIs, 'LinearRing')
		linearRing.append(create_coordinates(polygon_geometry.coords))

	return multiPolygon
		
def gml_multipoint(points):
	multiPoint = gmlElement('MultiPoint')
	multiPoint.attrib['srsName'] = 'http://www.opengis.net/gml/srs/epsg.xml#4326'

	for point_geom in points:
		#It's the caller's responsibility to check that all the points given
		#are actually points
		assert type(point_geom) is hxl.wkt.Point

		pointMember = gmlSubElement(multiPoint, 'pointMember')
		point = gmlSubElement(pointMember, 'Point')
		point.append(create_coordinates([point_geom.coord]))

	return multiPoint

def wfs_insert(layer_name, geometry, pcode=None, featureName=None):
	insert = wfsElement('Insert')
	layer = toppSubElement(insert, layer_name)

	the_geom = toppSubElement(layer, 'the_geom')
	the_geom.append(geometry)

	featureName_node = toppSubElement(layer, 'featureName')
	featureName_node.text = featureName

	pcode_node = toppSubElement(layer, 'pcode')
	pcode_node.text = pcode

	return insert

def wfs_transaction(operations):
	transaction = wfsElement('Transaction', nsmap=NSMAP)
	transaction.attrib['service'] = 'WFS'
	transaction.attrib['version'] = '1.0.0'

	for operation in operations:
		transaction.append(operation)

	return transaction

def wfs_insert_multipolygon(layer_name, name, polygons):
	operations = [wfs_insert(layer_name, gml_multipolygon(polygons))]
	return wfs_transaction(operations)

def wfs_insert_multipoint(layer_name, features):
	operations = [wfs_insert(layer_name, gml_multipoint([apl.point]), apl.pcode, apl.featureName) for apl in features]
	return wfs_transaction(operations)

class WFS(object):
	def __init__(self, server, port, path, username, password):
		self.server = server
		self.port = port
		self.path = path

		#FIXME: Credentials are sent in plain text :( Use HTTPS?
		self.auth = 'Basic ' + base64.encodestring('%s:%s' % (username, password)).strip()

	def make_request(self, need_auth, method, url, body=None):
		conn = httplib.HTTPConnection(self.server, self.port)
		headers = {
			'Accept':'application/xml,text/plain'
		}

		if body is None:
			pass
		elif type(body) is dict:
			headers['Content-type'] = 'application/json'
			body = json.dumps(body)

		elif type(body) is et._Element:
			headers['Content-type'] = 'application/xml'
			body = et.tostring(body)

		elif type(body) is str:
			headers['Content-type'] = 'text/plain'
		
		else:
			raise HXLException('Can\'t send %s' % type(body).__name__)

		if need_auth:
			headers['Authorization'] = self.auth

		print (self.path + '/' + url, body, headers)
		conn.request(method, self.path + '/' + url, body, headers)
		return conn.getresponse()

	def make_wfs_request(self, body=None):
		return self.make_request(True, 'POST', 'wfs', body)

	def describe_feature_type(self):
		assert False and 'implement me'

	def get_feature(self):
		assert False and 'implement me'

	def get_gml_object(self):
		assert False and 'implement me'

	def lock_feature(self):
		assert False and 'implement me'

	def insert_multipolygon(self, layer_name, name, polygons):
		operation = wfs_insert_multipolygon(layer_name, name, polygons)
		return self.make_wfs_request(operation)

	def insert_multipoint(self, layer_name, features):
		operation = wfs_insert_multipoint(layer_name, features)
		return self.make_wfs_request(operation)

