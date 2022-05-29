import json
from urllib.request import urlopen
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from bs4 import BeautifulSoup
from pylab import rcParams

#Gathers the original data from the website
data = urlopen("http://www.psudataeng.com:8000/getBreadCrumbData")
filename = "/home/mar32/data/" + datetime.today().strftime('%Y-%m-%d') + ".json"
file = open(filename, 'w+b')
for line in data:
  file.write(line)
file.close()

#Parses the data and converts into a more suitable and readable version.
f = open(filename)
par = json.load(f)
f.close
filename = "/home/mar32/data/" + datetime.today().strftime('%Y-%m-%d') + "_Parsed.json"
file = open(filename, 'w+')
file.write("[\n")
count = 0
for sec in par:
    file.write('\t')
    file.write(json.dumps(sec))
    if(count < len(par)-1): # if this is the last section in the document
        file.write(',')
        count+=1
    file.write('\n')
file.write("]")
file.close

#Get the event stop data
html = urlopen("http://www.psudataeng.com:8000/getStopEvents")
eventFile = "/home/mar32/data/" + datetime.today().strftime('%Y-%m-%d') + '_Event.json'
soup = BeautifulSoup(html,'lxml')
text = soup.get_text() # get data
tripIds=[] #list to hold all trip Ids
ind=[] #list to hold all entries that are in the event data stops
res="[\n"

#gather all trip Id's into an array
tripList = soup.find_all('h3')
for item in tripList:
  clean = re.compile(r'\b\d*')
  item = str(item)
  cell = clean.findall(item)
  str_cell = str(cell) #strip components that aren't digits and turn it into a string
  numb="" #reset the string
  for part in str_cell: #goes through all index of the string
   if part.isdigit():#check to see if the segment is a digit
      numb+=str(part) #add it to a string
  tripIds.append(numb) #add to the list of trip id's

#gather all table data
rows = soup.find_all('tr')
count = -1 #use to determine what data entry we are working with at the moment
for row in rows:
  row_td = row.find_all('td')
  cell = str(row_td)
  clean = re.compile('<\S*?>')
  clean2 = re.sub(clean, '', cell) #simplify the data contents 
  line = ""
  if (clean2 != '[]'): #time to add it to a string
    for item in clean2:
      if item =='[': #beginning of the index
        #add tripId into data field
        line='[' + tripIds[count] + ','
      else:
        line+=item #add the rest of the index
    ind.append(line) #add to the list
  else:
    count+=1 #this is a dud, don't enter it (it's actually when there is a new h3 so it would be a new trip id number, or at least the next index of the trip id list)

#turn into json file
jFields=["vehId","leaveTime","train","routeNumber","direction","serviceKey","stopTime","arriveTime","dwell","locationId","door","lift","ons","offs","estimatedLoad","maximumSpeed","trainMileage","patternDistance","locationDistance","xCoor","yCoor","source","sched"]
rowCount=0# want to know if it is the last row (use for adding commas at the end of the row if there are more at the end
for line in ind:
  inCo=0 #index value to access the jFields list
  for car in line:
    if car == '[':
      res += '\t{"tripId":"' #begining of the entry
    elif car == ' ':
      continue #skippppppp
    elif car == ',':
      res += '","' + jFields[inCo] + '":"'  #new entry to add
      inCo +=1
    elif car == ']': #end of an entry
      if rowCount == len(ind)-1: #last entry
        res += '"}\n]'
      else:
        res += '"},\n'#more to come after this
    else:
      res += car #must be an component to add by itself
  rowCount+=1

#send data to a file
file = open(eventFile, 'w+')
file.write(res)
file.close()
