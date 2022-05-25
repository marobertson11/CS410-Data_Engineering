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

data = urlopen("http://www.psudataeng.com:8000/getBreadCrumbData")
filename = "/home/mar32/data/" + datetime.today().strftime('%Y-%m-%d') + ".json"
file = open(filename, 'w+b')
for line in data:
  file.write(line)
file.close()

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
    if(count < len(par)-1):
        file.write(',')
        count+=1
    file.write('\n')
file.write("]")
file.close

html = urlopen("http://www.psudataeng.com:8000/getStopEvents")
eventFile = "/home/mar32/data/" + datetime.today().strftime('%Y-%m-%d') + '_Event.json'
soup = BeautifulSoup(html,'lxml')
text = soup.get_text()
tripIds=[]
ind=[]
res="[\n"

#gather all trip Id's into an array
tripList = soup.find_all('h3')
for item in tripList:
  clean = re.compile(r'\b\d*')
  item = str(item)
  cell = clean.findall(item)
  str_cell = str(cell)
  numb=""
  for part in str_cell:
   if part.isdigit():
      numb+=str(part)
  tripIds.append(numb)

#gather all table data
rows = soup.find_all('tr')
count=-1
for row in rows:
  row_td = row.find_all('td')
  cell = str(row_td)
  clean = re.compile('<\S*?>')
  clean2 = re.sub(clean, '', cell)
  line = ""
  if (clean2 != '[]'):
    for item in clean2:
      if item =='[':
#add tripId into data field
        line='[' + tripIds[count] + ','
      else:
        line+=item
    ind.append(line)
  else:
    count+=1

#turn into json file
jFields=["vehId","leaveTime","train","routeNumber","direction","serviceKey","stopTime","arriveTime","dwell","locationId","door","lift","ons","offs","estimatedLoad","maximumSpeed","trainMileage","patternDistance","locationDistance","xCoor","yCoor","source","sched"]
rowCount=0# want to know if it is the last row (use for adding commas at the end of the row if there are more at the end
for line in ind:
  inCo=0
  for car in line:
    if car == '[':
      res += '\t{"tripId":"'
    elif car == ' ':
      continue
    elif car == ',':
      res += '","' + jFields[inCo] + '":"'
      inCo +=1
    elif car == ']':
      if rowCount == len(ind)-1:
        res += '"}\n]'
      else:
        res += '"},\n'
    else:
      res += car
  rowCount+=1

#send data to a file
file = open(eventFile, 'w+')
file.write(res)
file.close()
