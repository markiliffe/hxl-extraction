hxl-extraction
==============

A python script that takes HXL (Humanitarian eXchange Language) a situation and response standard and outputs GML. 

This can then be fired at a WFS (OGC WFS-T) compliant server. Currently tested against a Geoserver stack.

geomimport.py
=============

Import geometry data for a specified country from a hxl store into a GeoServer instance. It works by converting the geometry into GML, and loading it into GeoServer via the WFS interface.

Usage:

    python ./geomimport.py -s <geoserver_hostname> -p <geoserver_port> [pcode, pcode, ...]

e.g.:

    python ./geomimport.py -s localhost -p 8080 PAK BFA
