#!/usr/bin/env python
 
import psycopg2, urllib, zipfile, os, urllib2, ftplib
# import subprocess, traceback

# Add path to the CGIS Python modules (IMPORTANT: choose development or production modules below)
# sys.path.append(r"\\L10-GEOSDI\PythonLibraries\Production")

# Import cgis modules
# from cgis import logutils

# Configure logging
# logFile = os.path.abspath(__file__).replace(".py", ".log") # Log written to the same directory, with the same name, as the .py script
# logging.basicConfig(filename = logFile, level = logging.DEBUG, format = "%(asctime)s %(levelname)s: %(message)s", datefmt = "%m/%d/%Y %I:%M:%S%p")

# logutils.log("info", "-------------------------------------------------------------------------------")
# logutils.log("info", "START")


# custom parameters
# output_dir = "C:\\temp\\"
output_dir = "C:\\minus34\\Python Code\\cyclone-download\\data\\"
url = "ftp://anonymous:anonymous@ftp.bom.gov.au:21/anon/gen/fwo/"

# postgres parameters
db_user_name = "postgres"
# db_password = "<yourpassword>"
db_server = "localhost"
db_name = "events"
db_schema = "bom"
db_port = 5432

# postgres connect string - need to use password version if trust not set on server
# db_conn_string = "host='%s' dbname='%s' user='%s' password='%s' port=%s"
db_conn_string = "host='%s' dbname='%s' user='%s' port=%s"

# BoM cyclone product names (shouldn't need to be edited)
file_names = ["IDW60266", "IDQ65248"]
# file_names = ["IDW60266", "IDD65401", "IDQ65248", "IDW60267", "IDD65402", "IDQ65249", "IDW60268", "IDQ65251",
#               "IDQ65250", "IDD65408", "IDW60283", "IDD65409", "IDQ65252"]

# BoM cyclone layer names (shouldn't need to be edited)
layer_names = ["areas", "fix", "track", "windarea"]

# shp2pgsql command line - don't edit!
shp2pgsql_cmd = "shp2pgsql -d -D -s 4283 -i -I \"%s\%s.%s.shp\" %s.%s -t 2D | psql -U %s -d %s -h %s -p %s"


# Setup Proxy for web request - not sure this is actually working
# proxy = urllib2.ProxyHandler({'ftp': '10.139.234.40'})
# opener = urllib2.build_opener(proxy)
# urllib2.install_opener(opener)

# connect to postgres
try:
    # need to use password version if trust not set on server
    # conn = psycopg2.connect(db_conn_string % (db_server, db_name, db_user_name, db_password, db_port))
    conn = psycopg2.connect(db_conn_string % (db_server, db_name, db_user_name, db_port))
except:
    print "Unable to connect to the postgres"

conn.autocommit = True
cur = conn.cursor()

# logutils.log("info", "Connected to Postgres")

# download each file, unzip it and add it to postgres database
i = 0

for file_name in file_names:
    download_file = url + file_name + ".zip"
    output_zip_dir = output_dir + file_name
    file_dir = output_zip_dir + ".zip"

    # # Delete ZIP file if it exists
    # try:
    #     os.remove(file_dir)
    # except OSError:
    #     pass

    try:
        # urllib.urlretrieve(download_file, file_dir)
        # print file_name + " downloaded"

        # Unzip the file
        fh = open(file_dir, 'rb')
        z = zipfile.ZipFile(fh)
        for name in z.namelist():
            z.extract(name, output_zip_dir)

        fh.close()

        print file_name + " unzipped"

        # Import into Postgres using shp2pgsql
        for layer_name in layer_names:

            table_name = "temp_" + file_name.lower() + "_" + layer_name
            perm_table_name = "cyclone_" + layer_name

            try:
                # load shapefile into postgres
                os.system(shp2pgsql_cmd % (output_zip_dir, file_name, layer_name, db_schema, table_name,
                                                     db_user_name, db_name, db_server, db_port))

                # insert new records into main cyclone table where they don't already exist
                sql = "INSERT INTO bom.%s " \
                      "SELECT tmp.* FROM bom.%s AS tmp " \
                      "WHERE NOT EXISTS (SELECT * FROM bom.%s AS bom " \
                      "WHERE bom.distid = tmp.distid AND bom.issuetime = tmp.issuetime);" \

                cur.execute(sql % (perm_table_name, table_name, perm_table_name))

            except:
                print "fatal", "Unable to import " + file_name + "." + layer_name + ": "

        i += 1
    except urllib2.URLError:  # not sure if this is the right exception to catch
        print "Problem with Internet connection"
    except:
        # cyclone not active for this area
        pass

# get new stats on tables for minor performance improvement
for layer_name in layer_names:
    perm_table_name = "cyclone_" + layer_name
    cur.execute("ANALYSE bom.%s;" % (perm_table_name,))

print "\nFINISHED: Look for shp2pgsql errors\n"

print str(i) + " BoM cyclone datasets loaded"






# Not using this at the moment
# url = 'ftp://ftp2.bom.gov.au/anon/gen/fwo/IDD10195.pdf'
# url = 'http://www.bom.gov.au/web03/ncc/www/awap/rainfall/totals/daily/grid/0.05/latest.grid.Z'
# request = urllib2.Request(url)
# u = urllib2.urlopen(request)

# fred = urllib2.urlopen("ftp://ftp.bom.gov.au/anon/gen/fwo/IDW60266.zip", "IDW60266.zip").read()
# print str(fred)

# ftp = ftplib.FTP("ftp.bom.gov.au")
# ftp.login("anonymous", "Pass")
# ftp.cwd("/anon/gen/fwo")

# ftp = ftplib.FTP(host="")

# request = urllib2.Request(download)
# # request.set_proxy('http://10.139.234.40:80', 'ftp')
# response = urllib2.urlopen(request)

# req = urllib2.Request('ftp://example.com/')
# request = urllib2.FTPHandler.ftp_open(download)

#
# output = open(file_dir, "w")
# output.write(response.read())
# output.close()


# Download the zipped shapefile - this works, but not from an FTP site :-(
# urllib.urlretrieve("http://www2.census.gov/geo/tiger/TIGER2011/TRACT/tl_2011_04_tract.zip", "tl_2011_04_tract.zip")
# urllib.urlretrieve("ftp://ftp.bom.gov.au/anon/gen/fwo/IDW60266.zip", "IDW60266.zip")
# urllib.urlretrieve("ftp://ftp.bom.gov.au/anon2/home/ncc/cyclone/Newcyclonedatabase.zip", "Newcyclonedatabase.zip")
# urllib.urlretrieve("ftp://ftp2.bom.gov.au/anon/gen/fwo/IDQ10090.pdf", "IDQ10090.pdf")
