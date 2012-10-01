import optparse
import sys

from hxl import HXLException
import hxl.geoserver
import hxl.sparql

def import_pcode(server, pcode):
	print 'Importing %s...' % (pcode,)

	try:
		country = hxl.sparql.query_country_information(pcode)
		if not country:
			print 'Unknown country'
			return

		(featureName,) = country
		server.create_multipolygon_layer(pcode, featureName)

		country = hxl.sparql.query_country_geometry(pcode)
		if country:
			(country_name, country_polygons) = country
			server.insert_multipolygon(pcode, country_name, country_polygons)

		apls = hxl.sparql.query_country_apls(pcode)
		apl_layer_name = pcode + '_APLs'
		server.create_multipoint_layer(apl_layer_name, featureName + ' APLs')

		if apls:
			server.insert_multipoint(apl_layer_name, apls)
				
	except HXLException as e:
		print e

def main():
	p = optparse.OptionParser(usage='usage: %prog [options] [pcode, pcode, ...]')
	p.add_option('--server', '-s', dest='server', default='127.0.0.1', help='GeoServer instance')
	p.add_option('--port', '-p', dest='port', type='int', default=8080)
	p.add_option('--user', '-u', dest='username', default='admin')
	p.add_option('--dbname', '-d', dest='dbname', default=None)

	p.add_option('--apls', dest='global_apls', action='store_true', default=False, help='Create layer with all APLs')
	p.add_option('--all', dest='all_pcodes', action='store_true', default=False, help='Import data from all countries')

	o, pcodes = p.parse_args()

	if not o.dbname:
		p.print_help()
		sys.exit(1)

	print 'GeoServer password for %s: ' % (o.username,),
	password = sys.stdin.readline().strip()

	if not password:
		print '\nNo password given'
		sys.exit(1)

	if o.all_pcodes:
		pcodes = hxl.sparql.query_country_pcodes()
	elif o.global_apls:
		pass
	elif not pcodes:
		print 'No pcodes given'
		sys.exit(1)

	server = hxl.geoserver.GeoServer(o.server, o.port, '/geoserver', o.username, password, o.dbname)

	if o.global_apls:
		apls = hxl.sparql.query_all_apls()

		try:
			server.create_multipoint_layer('APLs', 'Affected Population Locations')
			server.insert_multipoint('APLs', apls)
		except HXLException as e:
			print e

	for pcode in pcodes:
		import_pcode(server, pcode)

if __name__ == '__main__':
	main()
