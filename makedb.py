#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# By Ulrich Thiel, VK2UTL/DK1UT
# Reads calls.txt and creates calls.db


##############################################################################
# Imports
import re
import sqlite3
import sys

##############################################################################
# Fixing characters and umlauts, remove garbage
def fix(str):
	str = re.sub("u\"", "ü", str)
	str = re.sub("o\"", "ö", str)
	str = re.sub("a\"", "ä", str)
	str = re.sub("A\"", "Ä", str)
	str = re.sub("U\"", "Ü", str)
	str = re.sub("O\"", "Ö", str)
	str = re.sub("\"", "", str)
	str = re.sub("\n", "", str)
	str = re.sub("\f", "", str)
	str = re.sub("Seite [0-9]{1,3}", "", str)
	str = re.sub("[1-6][\s]*Liste der.*Klubstation", "", str)
	return str
	
##############################################################################
# Fixing city names
def fixCity(str):
	#insert dash
	pos = re.search("[a-z][A-Z]",str)
	if pos == None:
		return str	
	else:
		pos = pos.start()
		return str[0:pos+1]+"-"+str[pos+1:]

##############################################################################
# Main program

# Read date from callbook
callbookdate = ""
with open('calls.txt') as f:
	for line in f:
		line = unicode(line, 'utf-8')	
		if line.find("Januar") != -1 or line.find("Februar") != -1 or line.find("März") != -1 or line.find("April") != -1 or line.find("Mai") != -1 or line.find("Juni") != -1 or line.find("Juli") != -1 or line.find("August") != -1 or line.find("September") != -1 or line.find("Oktober") != -1 or line.find("November") != -1 or line.find("Dezember") != -1:
			line = re.sub("vom[ ]*", "", line)
			callbookdate = line
			break

callbookdatesplit = callbookdate.split(" ")
callbookmonth = ""
if callbookdatesplit[1] == "Januar":
	callbookmonth = "01."
elif callbookdatesplit[1] == "Februar":
	callbookmonth = "02."
elif callbookdatesplit[1] == "März":
	callbookmonth = "03."
elif callbookdatesplit[1] == "April":
	callbookmonth = "04."
elif callbookdatesplit[1] == "Mai":
	callbookmonth = "05."
elif callbookdatesplit[1] == "Juni":
	callbookmonth = "06."
elif callbookdatesplit[1] == "Juli":
	callbookmonth = "07."
elif callbookdatesplit[1] == "August":
	callbookmonth = "08."
elif callbookdatesplit[1] == "September":
	callbookmonth = "09."
elif callbookdatesplit[1] == "Oktober":
	callbookmonth = "10."
elif callbookdatesplit[1] == "November":
	callbookmonth = "11."
elif callbookdatesplit[1] == "Dezember":
	callbookmonth = "12."

callbookdate = callbookdatesplit[0]+callbookmonth+callbookdatesplit[2]
callbookdate = re.sub("\n", "", callbookdate)
print "Callbook date: " + str(callbookdate)

# Read file and extract call records
calls = [] #will be the array of call records
call = ""	#for reading lines
with open('calls.txt') as f:
	for line in f:		
		
		# start with fixing string
		# form feed character at line beginning yields regexp failure for unknown reason (reported)
		line = unicode(line, 'utf-8')
		line = fix(line)
		
		#match call sign		
		if re.match("D[A-R][0-9][A-Z]+", line): #match call sign
			if call != "":
				calls.append(call)
				call = ""
			call = line
		else:
			call = call + line	

#flush
calls.append(fix(call)) 

#now process data
#this is not perfect but it works
callsprocessed = []	
for call in calls:
	fields = call.split(";")
	callsign = fields[0].split(",")[0]
	callclass = fields[0].split(",")[1]
	name = fields[0].split(",")[2]
	name = re.sub("^[\s]*", "", name)
	name = re.sub("[\s]*$", "", name)
	callclass = re.sub("^[\s]*", "", callclass)
	if len(fields) == 1:	#no address given

		callsprocessed.append({'Call': callsign, 'Class': callclass, 'Name': name, 'Street':None, 'Zip':None, 'City':None})
	else:
		if len(fields) == 3:	#one address given
			street = fields[1]
			street = re.sub("^[\s]*", "", street)
			street = re.sub("[\s]*$", "", street)
			city = fields[2].split(",")[0]	#just in case, there are some errors in the PDF eg DB0ATV
			city = re.sub("^[\s]*", "", city)
			city = re.sub("[\s]*$", "", city)
			zip = city[0:5]
			city = city[6:]
			city = fixCity(city)
			
			callsprocessed.append({'Call': callsign, 'Class': callclass, 'Name': name, 'Street':street, 'Zip':zip, 'City':city})
			
		elif len(fields) == 4:	#two addresses given
			street1 = fields[1]
			street1 = re.sub("^[\s]*", "", street1)
			street1 = re.sub("[\s]*$", "", street1)
			city1 = fields[2].split(",")[0]
			street2 = fields[2].split(",")[1]
			city2 = fields[3]
			street1 = re.sub("^[\s]*", "", street1)
			street1 = re.sub("[\s]*$", "", street1)
			city1 = re.sub("^[\s]*", "", city1)
			city1 = re.sub("[\s]*$", "", city1)
			zip1 = city1[0:5]
			city1 = city1[6:]
			street2 = re.sub("^[\s]*", "", street2)
			street2 = re.sub("[\s]*$", "", street2)
			city2 = re.sub("^[\s]*", "", city2)
			city2 = re.sub("[\s]*$", "", city2)
			zip2 = city2[0:5]
			city2 = city2[6:]
			city1 = fixCity(city1)
			city2 = fixCity(city2)

			callsprocessed.append({'Call': callsign, 'Class': callclass, 'Name': name, 'Street':street1, 'Zip':zip1, 'City':city1})
			callsprocessed.append({'Call': callsign, 'Class': callclass, 'Name': name, 'Street':street2, 'Zip':zip2, 'City':city2})
	
print "Records: " + str(len(callsprocessed))

#now, add data to database (intelligently)
dbconn = sqlite3.connect('calls.db')
dbcursor = dbconn.cursor()

#create temporary table
dbcursor.execute("DROP TABLE IF EXISTS CallsignsTmp")
dbcursor.execute("CREATE TABLE CallsignsTmp AS SELECT * FROM Callsigns WHERE 0")
for call in callsprocessed:
	columns = ', '.join(call.keys())
	placeholders = ', '.join('?' * len(call))
	sql = 'INSERT INTO CallsignsTmp ({}) VALUES ({})'.format(columns, placeholders)
	dbcursor.execute(sql, call.values())

#update table
#what we actually want to do here is to update the db intelligently and keep history if changes. this in not implemented yet.
for call in callsprocessed:
	call['Date'] = callbookdate
	columns = ', '.join(call.keys())
	placeholders = ', '.join('?' * len(call))
	sql = 'INSERT INTO Callsigns ({}) VALUES ({})'.format(columns, placeholders)
	dbcursor.execute(sql, call.values())
	
#cleanup
dbcursor.execute("DROP TABLE CallsignsTmp")
dbcursor.execute("VACUUM")
				
dbconn.commit()
dbconn.close()