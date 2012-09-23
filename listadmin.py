#!/usr/bin/env python
import optparse
import sys

import hxl.geoserver
import hxl.sparql

def main():
	p = optparse.OptionParser()
	o, pcodes = p.parse_args()

	for pcode in pcodes:
		admin_levels = hxl.sparql.query_country_admin_levels(pcode)
		print '%s' % (pcode,)

		for admin_level in admin_levels:
			wkts = hxl.sparql.query_country_admin_level_geometry(pcode, admin_level)

			print '  Level %d:' % (admin_level,)

			for (name, _, _) in wkts:
				print '    %s' % (name,)


if __name__ == '__main__':
	main()
