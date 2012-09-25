import optparse
import sys

import hxl.geoserver
import hxl.gml
import hxl.sparql
import hxl.wkt

def main():
	p = optparse.OptionParser()
	p.add_option('--server', '-s', dest='server', default='127.0.0.1', help="GeoServer instance to connect to")
	p.add_option('--port', '-p', dest='port', default=8080)
	p.add_option('--user', '-u', dest='username', default='admin')

	o, pcodes = p.parse_args()

	if len(pcodes) == 0:
		p.print_usage()
		sys.exit(0)

	print 'GeoServer password for %s: ' % (o.username,),
	password = sys.stdin.readline().strip()

	if not password:
		print '\nNo password given'
		sys.exit(0)

	server = hxl.geoserver.GeoServer(o.server, o.port, o.username, password)

	for pcode in pcodes:
		print 'Importing %s...' % (pcode,),
		country = hxl.sparql.query_country_geometry(pcode)
		if country:
			(name, polygons) = country
			operation = hxl.gml.insert_multi_polygon_gml(pcode, name, polygons)
			response = server.wfs(operation)
			print
			print response.read()
		else:
			print 'Unknown pcode %s' % (repr(pcode),)

if __name__ == '__main__':
	main()
