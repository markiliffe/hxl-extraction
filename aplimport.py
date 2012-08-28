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

	print 'GeoServer password for %s: ' % (o.username,),
	password = sys.stdin.readline().strip()

	if not password:
		print '\nNo password given'
		sys.exit(0)

	server = hxl.geoserver.GeoServer(o.server, o.port, o.username, password)

	wkts = hxl.sparql.query_all_apls()
	operation = hxl.gml.insert_multi_point_gml('APLs', wkts)
	response = server.wfs(operation)
	print
	print response.read()

if __name__ == '__main__':
	main()
