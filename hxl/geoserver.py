import json
import lxml.etree as et
import time

from hxl import HXLException
from hxl.gml import WFS
import hxl.wkt

class GeoServer(WFS):
	def __init__(self, server, port, path, username, password, datastore):
		WFS.__init__(self, server, port, path, username, password)
		self.datastore = datastore

	def make_rest_request(self, method, url, body=None):
		return self.make_request(True, method, 'rest/' + url, body)

	def featuretype_url(self, layer_name):
		return 'workspaces/topp/datastores/%s/featuretypes/%s.json' % (self.datastore, layer_name)

	def get_layer(self, layer_name):
		response = self.make_rest_request('GET', self.featuretype_url(layer_name))
		
		if response.status != 404:
			return json.loads(response.read())

	def update_layer(self, layer_name, featuretype):
		response = self.make_rest_request('PUT', self.featuretype_url(layer_name), featuretype)
		
		if response.status != 200:
			raise HXLException(response.read())

	def create_layer(self, layer_name, layer_title, attrs):
		attributes = []

		for (name, binding) in attrs.items():
			attributes.append({'name':name, 'binding':binding})

		operation = {
			'featureType': {
				'name':layer_name,
				'nativeName':layer_name,
				'title':layer_title,
				'abstract':'HXL imported data (%s)' % (time.ctime(),),
				'srs':'EPSG:4326',

				'attributes': {
					'attribute': attributes
				}
			}
		}

		response = self.make_rest_request(
			'POST',
			'workspaces/topp/datastores/%s/featuretypes.json' % (self.datastore,),
			operation
		)

		if response.status != 201:
			raise HXLException(response.read())

	def create_multipolygon_layer(self, layer_name, layer_title):
		return self.create_layer(
			layer_name,
			layer_title,
			{'the_geom':'com.vividsolutions.jts.geom.MultiPolygon'}
		)

	def create_multipoint_layer(self, layer_name, layer_title):
		return self.create_layer(
			layer_name,
			layer_title,
			{
				'the_geom':'com.vividsolutions.jts.geom.MultiPoint',
				'pcode':'java.lang.String',
				'featureName':'java.lang.String'
			}
		)

	def update_bounding_box(self, featuretype, polygons):
		minx, miny, maxx, maxy = hxl.wkt.bounding_box(polygons)

		nativeBoundingBox = featuretype['featureType']['nativeBoundingBox']
		nativeBoundingBox['minx'] = minx
		nativeBoundingBox['maxx'] = maxx
		nativeBoundingBox['miny'] = miny
		nativeBoundingBox['maxy'] = maxy

		latLonBoundingBox = featuretype['featureType']['latLonBoundingBox']
		latLonBoundingBox['minx'] = minx
		latLonBoundingBox['maxx'] = maxx
		latLonBoundingBox['miny'] = miny
		latLonBoundingBox['maxy'] = maxy

		return featuretype

	def insert_multipolygon(self, layer_name, name, polygons):
		featuretype = self.get_layer(layer_name)
		featuretype = self.update_bounding_box(featuretype, polygons)

		self.update_layer(layer_name, featuretype)
		return WFS.insert_multipolygon(self, layer_name, name, polygons)

	def insert_multipoint(self, layer_name, features):
		featuretype = self.get_layer(layer_name)
		featuretype = self.update_bounding_box(featuretype, [feature.point for feature in features])

		self.update_layer(layer_name, featuretype)
		return WFS.insert_multipoint(self, layer_name, features)

