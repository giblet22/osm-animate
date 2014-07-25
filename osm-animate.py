import os
import glob
from bs4 import BeautifulSoup
import re
from dateutil import parser
from dateutil import relativedelta

## input settings
osm_file = "/Users/andrewbollinger/Downloads/suratmap.osm"
place_name = "surat" ## for the gif

## use snap.c to convert osm file to format suitable for datamaps
os.system("cat " + osm_file + " | ./snap > datamapfile")

## use beautiful soup to get timestamps from osm file and set frames (should ideally be done in C but I don't know how)

soup = BeautifulSoup(open(osm_file))

ways = soup.find_all('way')
rows = []
print "There are " + repr(len(ways))+ " ways"
for way in ways:
    rows.append([way['id'],way['timestamp'],0])

rs = sorted(rows, key=lambda entry: entry[1])
for row in rs:
    rd = relativedelta.relativedelta(parser.parse(row[1]),parser.parse(rs[0][1]))
    row[2] = rd.years * 12 + rd.months

total_frames = max(rs, key = lambda x: x[2])[2]

## also get a bounding box for later rendering

nodes = soup.find_all('node')
nll = []
for node in nodes:
    nll.append([node['lat'],node['lon']])

min_lat = min(nll, key = lambda x: x[0])[0]
min_lon = min(nll, key = lambda x: x[1])[1]
max_lat = max(nll, key = lambda x: x[0])[0]
max_lon = max(nll, key = lambda x: x[1])[1]

## use above info to save each frame as a separate file
with open('datamapfile') as f:
    lines = f.readlines()
    for i in range(0,total_frames):
        output = []
        ## create temp array of ids that match this frame
        flt = filter(lambda x: x[2] == i,rs)
        flt_ids = [flt[j][0] for j in range(0,len(flt))]
        ## iterate over lines and check ids against fitered list
        for line in lines:
            if (re.search("id=(\d+)",line).group(1) in flt_ids):
                output.append(line)
        g = open('frame_' + repr(i+1).zfill(4), 'w')
        g.write(''.join(output))
        g.close()

## get the frames
frame_list = glob.glob("frame*")

## encode
for index, file in enumerate(frame_list):
    os.system("cat " + file + " | ./encode -o \"" + str(index+1) +"\" -z 12")

## render
for d in range(1,total_frames+1):
    os.system("./render -t 0 -A -- \"" + str(d) + "\" 12 " + min_lat + " " + min_lon + " " + max_lat + " " + max_lon + " > " + str(d).zfill(4) +".png")

## animate
os.system("convert -coalesce -dispose 1 -delay 20 -loop 0 *.png " + place_name + ".gif") ## still need to add first frame of black background
