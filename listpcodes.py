import optparse
import sys

import hxl.geoserver
import hxl.sparql

def main():
	pcodes = hxl.sparql.query_country_pcodes()
	print ' '.join(pcodes)

if __name__ == '__main__':
	main()
