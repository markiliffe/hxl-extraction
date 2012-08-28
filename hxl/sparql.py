import re
from SPARQLWrapper import SPARQLWrapper, JSON

import hxl.wkt

def do_sparql_query(query):
	sparql = SPARQLWrapper('http://hxl.humanitarianresponse.info/sparql')
	sparql.setQuery('''
prefix xsd: <http://www.w3.org/2001/XMLSchema#> 
prefix dct: <http://purl.org/dc/terms/> 
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
prefix hxl: <http://hxl.humanitarianresponse.info/ns/#>
prefix geo: <http://www.opengis.net/ont/geosparql#>

''' + query)

	sparql.setReturnFormat(JSON)
	return sparql.query().convert()

def query_country_geometry(query_pcode):
	countries = do_sparql_query('''
	SELECT DISTINCT ?featureName ?data WHERE {
	  ?country hxl:pcode "%s" ;
		hxl:featureName ?featureName ;
		geo:hasGeometry/geo:hasSerialization ?data .
	}
	LIMIT 1
	''' % (query_pcode,))
	
	wkts = []
	
	for country in countries['results']['bindings']:
		featureName = country['featureName']['value']
		data = country['data']['value']
		(poly_type, coords) = hxl.wkt.parse_wkt(data)
		wkts.append((featureName, poly_type, coords))

	return wkts

def query_country_apls(query_pcode):
	apls = do_sparql_query('''
	SELECT DISTINCT ?pcode ?featureName ?data WHERE {
	  ?p rdf:type hxl:APL ;
		hxl:pcode ?pcode ;
		hxl:featureName ?featureName ;
	        hxl:atLocation/hxl:pcode "%s" ;
	        geo:hasGeometry/geo:hasSerialization ?data .
	}       
	''' % (query_pcode,))

	wkts = []
	
	for apl in apls['results']['bindings']:
		pcode = apl['pcode']['value']
		featureName = apl['featureName']['value']
		data = apl['data']['value']
		(poly_type, coords) = hxl.wkt.parse_wkt(data)
		wkts.append((featureName, poly_type, coords))

	return wkts

def query_all_apls(query_pcode):
	apls = do_sparql_query('''
	SELECT DISTINCT ?pcode ?featureName ?data WHERE {
	  ?p rdf:type hxl:APL ;
		hxl:pcode ?pcode ;
		hxl:featureName ?featureName ;
	        geo:hasGeometry/geo:hasSerialization ?data .
	}       
	''' % (query_pcode,))

	wkts = []
	
	for apl in apls['results']['bindings']:
		pcode = apl['pcode']['value']
		featureName = apl['featureName']['value']
		data = apl['data']['value']
		(poly_type, coords) = hxl.wkt.parse_wkt(data)
		wkts.append((poly_type, featureName, coords))

	return wkts

def query_country_pcodes():
	pcode_results = do_sparql_query('''
	SELECT DISTINCT ?pcode WHERE {
		?country rdf:type hxl:Country ;
			hxl:pcode ?pcode .
	}
	''')

	pcodes = []
	for pcode_result in pcode_results['results']['bindings']:
		pcode = pcode_result['pcode']['value']
		pcodes.append(pcode)

	return pcodes

admin_level_re = re.compile('^.+/adminlevel([0-9]+)$')
def query_country_admin_levels(pcode):
	admin_level_results = do_sparql_query('''
	SELECT DISTINCT ?level WHERE {
		?c hxl:pcode "%s" .
		?admin hxl:atLocation* ?c .
		?admin hxl:atLevel ?level .
	}
	''' % (pcode,))

	admin_levels = set()

	for admin_level_result in admin_level_results['results']['bindings']:
		#admin levels appear to be stored as URIs, we need to parse out the
		#integer value from the URI
		admin_level_type = admin_level_result['level']['type']
		admin_level_value = admin_level_result['level']['value']

		if admin_level_type == 'uri':
			m = admin_level_re.match(admin_level_value)
			if m:
				(n,) = m.groups()
				n = int(n)
				admin_levels.add(n)
				continue

		raise Exception('Badly formed admin level %s' % (repr(admin_level_result['level']['value']),))

	admin_levels = list(admin_levels)
	admin_levels.sort()
	return admin_levels

def query_country_admin_level_geometry(query_pcode, query_level):
	query_level_uri = \
		'http://hxl.humanitarianresponse.info/data/locations/admin/%s/adminlevel%d' % (query_pcode.lower(), query_level)
	admin_level_results = do_sparql_query('''
	SELECT DISTINCT ?featureName ?data WHERE {
	?c hxl:pcode "%s" ;
		hxl:featureName ?featureName ;
		geo:hasGeometry/geo:hasSerialization ?data .
	?admin hxl:atLocation* ?c .
	?admin hxl:atLevel <%s> .
	}
	''' % (query_pcode, query_level_uri))

	admin_level_wkts = []
	for admin_level_result in admin_level_results['results']['bindings']:
		featureName = admin_level_result['featureName']['value']
		data = admin_level_result['data']['value']
		(poly_type, coords) = hxl.wkt.parse_wkt(data)
		admin_level_wkts.append((featureName, poly_type, coords))
	
	return admin_level_wkts
