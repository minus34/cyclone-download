#!/usr/bin/env bash

AWS_PROFILE="minus34"
FTP_URL="ftp://anonymous:anonymous@ftp.bom.gov.au:21/anon/gen/fwo"
WORKING_FOLDER="/Users/$(whoami)/tmp/bom"

curl --insecure "${FTP_URL}/IDQ65248.zip" -o "${WORKING_FOLDER}/IDQ65248.zip"
curl --insecure "${FTP_URL}/IDQ65252.zip" -o "${WORKING_FOLDER}/IDQ65252.zip"

aws --profile=${AWS_PROFILE} s3 cp ${WORKING_FOLDER} s3://minus34.com/opendata/bom/cyclone/2025/alfred --acl public-read --recursive




# make script executable
#chmod a+x /Users/hughsaalmans/git/minus34/cyclone-download/xx_download_and_copy_to_s3.sh

# crontab commands
#
# crontab -e  # i to start editing, ESC to stop, :wq to save and exit
#
#crontab -l  # list all cron jobs
#
#SHELL=/bin/bash
#PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
#
#@hourly /Users/hughsaalmans/git/minus34/cyclone-download/xx_download_and_copy_to_s3.sh
