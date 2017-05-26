#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#By Ulrich Thiel, VK2UTL/DK1UT
#Adds coordinates to calls.db

##############################################################################
# Imports
import sqlite3
import geocoder
import requests
import sys
import time
from tqdm import tqdm

dbconn = sqlite3.connect('calls.db')
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
dbconn.row_factory = dict_factory
dbcursor = dbconn.cursor()

#For initial geocoding
dbcursor.execute("SELECT * FROM Locations WHERE Geocode IS NULL")

#For update geocoding
#dbcursor.execute("SELECT * FROM Locations WHERE Geocode = 0") 

res = dbcursor.fetchall()
print str(len(res)) + " addresses selected for geocoding"

#keep session alive
with requests.Session() as session:
	for i in tqdm(range(len(res))):
		row = res[i]
		address = row['Street'] + ", " + row['Zip'] + " " + row['City'] + ", Germany"
		#print address
		g = geocoder.google(address, session=session)
		#print g.status
		if g.status == 'OVER_QUERY_LIMIT':
			print "Query limit reached (you should try again in 24h)"
			sys.exit(0)
		if g.status == 'ZERO_RESULTS' or g.status == 'ERROR - No results found' or g.lng == None:
			dbcursor.execute("UPDATE Locations SET Geocode = 0 WHERE Id = " + str(row['Id']))
		
		else:
			dbcursor.execute("UPDATE Locations SET Lng = " + str(g.lng) + ", Lat = " + str(g.lat) + ", Geocode = 1 WHERE Id = " + str(row['Id']))
		dbconn.commit()
		
dbconn.close()
