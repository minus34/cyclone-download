#!/usr/bin/env python
 
import psycopg2, zipfile, os, urllib2

# custom parameters
output_dir = "C:\\temp\\"
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
file_names = ["IDW60266", "IDQ65248"]  # test product names
# file_names = ["IDW60266", "IDD65401", "IDQ65248", "IDW60267", "IDD65402", "IDQ65249", "IDW60268", "IDQ65251",
#               "IDQ65250", "IDD65408", "IDW60283", "IDD65409", "IDQ65252"]

# BoM cyclone layer names (shouldn't need to be edited)
layer_names = ["areas", "fix", "track", "windarea"]

# shp2pgsql command line - don't edit!
shp2pgsql_cmd = "shp2pgsql -d -D -s 4283 -i -I \"%s\%s.%s.shp\" %s.%s -t 2D | psql -U %s -d %s -h %s -p %s"


# Setup Proxy for web request - some proxies don't like this
# proxy = urllib2.ProxyHandler({'ftp': '<your proxy IP address>'})
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

# download each file, unzip it and add it to postgres database
i = 0

for file_name in file_names:
    download_file = url + file_name + ".zip"
    output_zip_dir = output_dir + file_name
    file_dir = output_zip_dir + ".zip"

    # # Delete ZIP file if it exists - disable this so you can use the test files
    # try:
    #     os.remove(file_dir)
    # except OSError:
    #     pass

    try:
        # # disable this so you can use the test files
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
        # cyclone not active for this area or your db stuffed up!
        pass

# get new stats on tables for minor performance improvement
for layer_name in layer_names:
    perm_table_name = "cyclone_" + layer_name
    cur.execute("ANALYSE bom.%s;" % (perm_table_name,))

print "\nFINISHED: Look for shp2pgsql errors\n"

print str(i) + " BoM cyclone datasets loaded"
