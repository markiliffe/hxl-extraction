# hxl-extraction

A python script that takes HXL (Humanitarian eXchange Language) a situation and response standard and outputs GML. 

This can then be fired at a WFS (OGC WFS-T) compliant server. Currently tested against a Geoserver stack.

# Quickstart

Most of the import process is automated, however there is still a few manual steps that need to be performed on the GeoServer before the HXL data can be imported:

 1. Create PostGIS table on GeoServer using `install_database.sh`
 2. Configure GeoServer to use the newly created table.

## install\_database.sh

Create a PostGIS table suitable for GeoServer. The created table will be called 'hxlextract', owned by the user 'hxlextract'. It should prompt you to choose a password for the newly created user. Remember this password, you'll need it when configuring GeoServer later.

This script needs to be run on the server running GeoServer. You will need to run the script as a user who has privileges to change the local database; ask your local friendly admin for details.

Simply run `./install_database.sh`.

## Configure GeoServer

1. Log into the GeoServer web-interface as an admin user.
2. Click `Stores` on the left-hand menu.
3. Click `Add new Store`
4. Click `PostGIS` under the `Vector Data Sources` heading.
5. Configure the PostGIS Store:
 * Choose `topp` from the `Workspace` dropdown.
 * Type a friendly name in `Data Source Name` (e.g. `HXL Imported Data`)
 * You shouldn't need to change the `host` or `port` fields.
 * Type `hxlextract` into the `database` field
 * Type `hxlextract` into the `user` field.
 * Type the password that you choose in the `install_database.sh` step above into the `passwd` field.
 * Click the `Save` button at the bottom.
6. The next screen should be `New Layer`. The database is now configured, and you safely close the window.

## hxl2geoserver.py

Import HXL data into a GeoServer instance. Data can be imported from selected countries (selected by their pcodes), or the entire HXL datastore can be imported.

For each country, two layers are created:
 1. A polygon layer containing the country geometry.
 2. A point layer containing Affected Population Locations (APLs).

An optional 'Global APL' layer can be created containing all APLs in the HXL datastore.

Run `python hxl2geoserver.py --help` to see help.

For example, if you had a GeoServer web interface available at `http://172.16.241.131:8080/geoserver` with a user `admin` and a PostGIS table named `hxlextract`, and you wanted to import data for Pakistan, you would run:

    python hxl2geoserver.py -s 172.16.241.131 -p 8080 -u admin -d hxlextract PAK

You can import data for multiple pcodes in one command, e.g:

    python hxl2geoserver.py -s 172.16.241.131 -p 8080 -u admin -d hxlextract PAK IND AFG

You can import data for all countries by running:

    python hxl2geoserver.py -s 172.16.241.131 -p 8080 -u admin -d hxlextract --all

Add `--apls` to the command line to create a global layer of all APLs.

Note: `hxl2geoserver.py` assumes that the given pcode doesn't already exist in the GeoServer. It will throw an error if a given layer already exists. This means that you can't easily update country data once it already been imported. You will need to remove the layer from GeoServer (using the `Layers` link in the web-interface, then `Remove selected resources`), and then re-run `hxl2geoserver.py`. Updating existing data is on the TODO list.
