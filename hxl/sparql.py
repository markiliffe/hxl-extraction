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
		wkts.append((poly_type, coords))

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
		wkts.append((poly_type, coords))

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
		wkts.append((poly_type, coords))

	return wkts

