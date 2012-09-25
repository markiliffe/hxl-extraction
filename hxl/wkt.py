from hxl import HXLException

#Geometry in HXL is stored as 'Well-Known Text' strings in the hasSerialization property. 
#WKT data looks like:
#	POLYGON ((1 2, 3 4))
#	POINT (12.34 32.12)
#	MULTIPOLYGON (((1 2, 3 4)),((3 4, 5 6)))

class Polygon(object):
	def __init__(self, coords):
		self.coords = coords

class Point(object):
	def __init__(self, coord):
		self.coord = coord

def extract(data, start, end):
	if not data.startswith(start):
		raise HXLException('Malformed WKT: Couldn\'t find %s' % (repr(start),))

	if not data.endswith(end):
		raise HXLException('Malformed WKT: Couldn\'t find %s' % (repr(end),))

	return data[len(start):-len(end)]

def parse_coord(data):
	coord = data.split(' ')

	if len(coord) == 2:
		(x, y) = coord
		return (float(x), float(y))
	else:
		raise HXLException('Malformed co-ordinate %s' % (repr(coord),))

def parse_coords(data):
	coords = data.split(',')
	return map(parse_coord, coords)

def parse_wkt(data):
	'''Parse a WKT string and return a tuple of (type, coordinates)'''

	if data.startswith('POLYGON '):
		data = extract(data, 'POLYGON ((', '))')
		return [Polygon(parse_coords(data))]

	elif data.startswith('MULTIPOLYGON '):
		data = extract(data, 'MULTIPOLYGON (((', ')))')
		polygons = data.split(')),((')
		return [Polygon(parse_coords(polygon)) for polygon in polygons]

	elif data.startswith('POINT '):
		data = extract(data, 'POINT (', ')')
		return Point(parse_coord(data))

	else:
		raise HXLException('Unknown WKT type %s' % (repr(data.split(' ', 1)[0])))

__all__ = ['parse_wkt']

def assert_coord_eq(l, r):
	(lx, ly) = l
	(rx, ry) = r

	epsilon = 0.00001

	assert lx < rx + epsilon
	assert lx > rx - epsilon

	assert ly < ry + epsilon
	assert ly > ry - epsilon

def wkt_coord_test():
	coord = parse_coord('12.34 56.78')

	assert type(coord) is tuple
	assert len(coord) == 2

	assert_coord_eq(coord, (12.34, 56.78))

def wkt_point_test():
	data = 'POINT (11.11 22.22)'

	points = parse_wkt(data)

	assert type(points) is list
	assert len(points) == 1

	assert type(points[0]) is Point
	print points[0].coord
	assert_coord_eq(points[0].coord, (11.11, 22.22))

def wkt_polygon_test():
	data = 'POLYGON ((11.11 22.22,33.33 44.44,55.55 66.66,11.11 22.22))'

	polygons = parse_wkt(data)
	assert len(polygons) == 1

	[polygon] = polygons

	assert type(polygon) is Polygon
	assert len(polygon.coords) == 4
	assert_coord_eq(polygon.coords[0], (11.11, 22.22))
	assert_coord_eq(polygon.coords[1], (33.33, 44.44))
	assert_coord_eq(polygon.coords[2], (55.55, 66.66))
	assert_coord_eq(polygon.coords[3], (11.11, 22.22))

def wkt_multi_polygon_test():
	data = 'MULTIPOLYGON (((11.11 22.22,33.33 44.44,11.11 22.22)),((55.55 66.66,77.77 88.88,11.11 22.22,55.55 66.66)))'

	polygons = parse_wkt(data)
	assert len(polygons) == 2

	[polygon1, polygon2] = polygons

	assert type(polygon1) is Polygon
	assert len(polygon1.coords) == 3
	assert_coord_eq(polygon1.coords[0], (11.11, 22.22))
	assert_coord_eq(polygon1.coords[1], (33.33, 44.44))
	assert_coord_eq(polygon1.coords[2], (11.11, 22.22))

	assert type(polygon2) is Polygon
	assert len(polygon2.coords) == 4
	assert_coord_eq(polygon2.coords[0], (55.55, 66.66))
	assert_coord_eq(polygon2.coords[1], (77.77, 88.88))
	assert_coord_eq(polygon2.coords[2], (11.11, 22.22))
	assert_coord_eq(polygon2.coords[0], (55.55, 66.66))


