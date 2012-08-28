def extract(data, start, end):
	assert data.startswith(start)
	assert data.endswith(end)
	return data[len(start):-(len(end) + 1)]

def parse_coords(data):
	coords = data.split(',')
	coords = map(lambda s: s.split(' '), coords)
	return map(lambda s: (float(s[0]), float(s[1])), coords)

def parse_wkt(data):
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
		assert False

