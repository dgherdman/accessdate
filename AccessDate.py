#!/usr/bin/python
#
#  The 1st line tells UNIX like OS variants where to find the correct Python 
#  interpreter. This is ingnored by Operating systems such as Windows
#
#  accessdate.py
#
#  A python script to determine files which have not been modified since a 
#  specified date
#
#  Read through a recursive directory listing file (currently provided on
#  sharepoint)  parse the mtime of the file and compare it to the refernce
#  date provided as a  parameter.
#
#  parse out the directory path and the filename. We may want to produce lists
#  of files but not used in V1.0
#
#   version 1.1  22/04/22   Dave Herdman
#
#   Revision History
#   V1.0    21/03/22    Initial Release Process only file totals
#   V1.1    22/04/22    Modified to produce 3 output files with the names
#                       <input-file-path>_older.txt and 
#	                    <input-file-path>_recent.txt and 
#                       <input-file-path>_stats.csv
# 
#   Developed using the Pycharm IDE
#   See PyCharm help at https://www.jetbrains.com/help/pycharm/
#
#   Usage: accessdate.py <Path-of-File-to-Process> <Path-to-output-File-Directory>
#
import sys
import os
import os.path
import re
import datetime
from datetime import date
from datetime import timedelta

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # process the command line agruments (if any)
    if len(sys.argv) > 2:
        # Assume first argument is the path to the filename
        # Second aegument is the output files directory
        # silently ignore any other arguments
		# The output file path IS NOT a file name there 
        in_file = sys.argv[1]
        out_file_dir = sys.argv[2]
    else:
        print("Usage: accessdate.py  <input-file-path> <output-file-directory-path>")
        sys.exit("Incorrect number of arguments")



    dirlist = open(in_file, "r")
	
	# Formulate the output file names
    in_file_name = os.path.basename(in_file)
    in_file_fname = os.path.splitext(in_file_name)[0]
    nu_filename = in_file_fname + "_recent.txt"
    outfile1_name = os.path.join(out_file_dir,nu_filename)
    nu_filename = in_file_fname + "_older.txt"
    outfile2_name = os.path.join(out_file_dir,nu_filename)
    nu_filename = in_file_fname + "_stats.csv"
    stats_file_name = os.path.join(out_file_dir,nu_filename)
    outfile1 = open(outfile1_name,"w")
    outfile2 = open(outfile2_name, "w")

    # set pattern for a time field
    pat = re.compile(r'\d\d\:\d\d')

    # Determine the 13 month threshold date based on today's date. This
    # is probably not quite 13 months as the listing which we will
    # process is either days or weeks old but this is probably good 
    # enough for our requirements. An alternative would be to specify the
    # threshold date as a command line argument.

    curdate = date.today()
    thresh = timedelta(395)
    thresh_date = curdate - thresh

    # initialise number of file counters
    stale_file_cnt = 0
    live_file_cnt = 0

    # initialise the file size counters
    # These sizes will be held in gigabytes
    stale_file_size = 0
    live_file_size = 0

    for line in dirlist:
        elements=line.split()

        # process the elements in a line depending on what type of filesystem
        # object we are processing. This is denoted by the first character of
        # the posix umask field as listed below
        #
        #       First Character     meaning
        #           -               regular file
        #           d               directory
        #           l               soft link
        #           c               character special file
        #                             (probably unlikely for this application)
        #
        objecttype = elements[0][0]


        # There may be white space in the file & Directory names, so we can't
        #  rely on an element number to locate these. Instead, we scan forwards
        # for the full path & backwards for the filename.
        full_path = line[line.find(r'/'):]
        #print("full path %s" % (full_path,))
        file_name = full_path[full_path.rfind(r'/')+1:]
        #print("File name is %s" % (file_name,))
        dir_path = full_path[:full_path.rfind(r'/')+1]

        if objecttype == "-":
            # it's a regular file
            pass
        if objecttype == "d":
            # it's a directory
            pass
        if objecttype == "l":
            # it's a symbolic link
            pass

        # Now obtain mtime data
        txt_file_month = elements[5]
        file_day = int(elements[6])

        # The next field in the directory listing is either a time stamp
        # for files that have been modified in the last 6 months or a
        # 4 digit year for files that have been modified more than 6 months
        # ago . For ease of processing we convert time stamps into dates

        dto = datetime.datetime.strptime(txt_file_month,"%b")
        file_month = int(dto.month)

        if pat.match(elements[7]):
            # it is a time field so within 6 months. Note that this
            # code is curerently not general purpose and relies on
            # the current year being 2022
            if file_month > 4:
                # The year is 2021
                file_year = 2021
            else:
                file_year = 2022
        else:
            # It is a year field so more than 6 months ago
            file_year = int(elements[7])


        #
        # Now the date on the file is before the threshold we 
        # write out to the "recent" files log otherewise we
        # write it out to the "stale" files log. We also keep
        # talies of number of files and size
        #

        file_date = date(file_year,file_month,file_day)

        if file_date < thresh_date :
            # File is "stale"
            outfile2.write(line)
            stale_file_cnt += 1

            # Add to the cumulative size
            stale_file_size += int(elements[4])            

        else:
            # File is "live"
            outfile1.write(line)
            live_file_cnt += 1
            live_file_size += int(elements[4])

    # 
	# Output finishing totals
	# Then Close all files
    giga = 1000 * 1000 * 1000
	
    statsfile = open(stats_file_name,"w")
	
    statsfile.write("Total Files processed,Total live files,Total Live File size (GB),Total Stale files,Total Stale File size (GB)\n")
    statsfile.write(str(stale_file_cnt + live_file_cnt) + "," + str(live_file_cnt) \
      + "," + str(live_file_size/giga) + "," + str(stale_file_cnt) + "," + str(stale_file_size/giga) +"\n")
	  
    statsfile.close()
    outfile1.close()
    outfile2.close()