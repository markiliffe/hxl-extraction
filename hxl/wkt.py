from hxl import HXLException

#Geometry in HXL is stored as 'Well-Known Text' strings in the hasSerialization property. 

def extract(data, start, end):
	if not data.startswith(start):
		raise HXLException('Malformed WKT: Couldn\'t find %s' % (repr(start),))

	if not data.endswith(end):
		raise HXLException('Malformed WKT: Couldn\'t find %s' % (repr(end),))

	return data[len(start):-(len(end) + 1)]

def parse_coords(data):
	coords = data.split(',')
	coords = map(lambda s: s.split(' '), coords)
	return map(lambda s: (float(s[0]), float(s[1])), coords)

def parse_wkt(data):
	'''Parse a WKT string and return a tuple of (type, coordinates)'''

	if data.startswith('POLYGON '):
		data = extract(data, 'POLYGON ((', '))')
		return ('POLYGON', parse_coords(data))

	elif data.startswith('MULTIPOLYGON '):
		data = extract(data, 'MULTIPOLYGON (((', ')))')
		return ('MULTIPOLYGON', map(parse_coords, data.split(')),((')))

	elif data.startswith('POINT '):
		data = extract(data, 'POINT (', ')')
		return ('POINT', parse_coords(data))

	else:
		raise HXLException('Unknown WKT type %s' % (repr(data.split(' ', 1)[0])))

__all__ = ['parse_wkt']
