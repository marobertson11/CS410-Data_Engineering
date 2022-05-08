#!/usr/bin/env python
# Consume messages from Confluent Cloud
# Using Confluent Python Client for Apache Kafka
# =============================================================================

from confluent_kafka import Consumer
import json
import ccloud_lib
import time
import pandas as pd
from datetime import datetime
import psycopg2

def trip(info): #Determine if numTrip is empty or not
  if(info): return True
  return False

def timeEmpty(info): #DETERMINE IF ACT_TIME IS EMPTY OR NOT
  if(info): return True
  return False

def day(info):#DETERMINE IF OPD_DATE IS EMPTY
  if(info): return True
  return False

def lat(info):#GPS_LATITDUE IS EMTPY
  if(info): return True
  return False

def log(info):#GPS_LONGITUDE IS EMPTY
  if(info): return True
  return False

def direc(info):#DIRECTION IS EMPTY
  if(info): return True
  return False

def velo(info):#IF VELOCITY IS EMPTY
  if(info): return True
  return False

def vehId(info):#IF VEHICLE_ID IS EMPTY
  if(info): return True
  return False

def direCheck(info):#IF DIRECTION IS BETWEEN 0-359
  numb=int(info)
  if (numb>=0 and numb<=359):
    return True
  return False

def timeCheck(info):#IF ACT_TIME IS BETWEEN 0-86399 (WITHIN THE TIME OF 1 DAY
  numb=int(info)
  if (numb>=0 and numb<=86399):
    return True
  return False

def checkMonth(date):#TURN STRING MONTH INTO DIGIT FORM OF STRING
  if (date[3:6] == "JAN"):
      return "01"
      if (date[3:6] == "FEB"):
      return "02"
  if (date[3:6] == "MAR"):
      return "03"
  if (date[3:6] == "APR"):
      return "04"
  if (date[3:6] == "MAY"):
      return "05"
  if (date[3:6] == "JUN"):
      return "06"
  if (date[3:6] == "JUL"):
      return "07"
  if (date[3:6] == "AUG"):
      return "08"
  if (date[3:6] == "SEP"):
      return "09"
  if (date[3:6] == "OCT"):
      return "10"
  if (date[3:6] == "NOV"):
      return "11"
  if (date[3:6] == "DEC"):
      return "12"

def checkDay(date):#DETERMINE WHAT DAY OF THE WEEK THE DATE IS
  date = pd.Timestamp(date)
  if(date.dayofweek >=0 and date.dayofweek <= 5):
    return "Weekday"
  elif(date.dayofweek == 6):
    return "Saturday"
  else:
    return "Sunday"

def dbconnect(): #CONNECT TO SQL DATABASE
  connection = psycopg2.connect(host="localhost", database=DBname, user=DBuser, password=DBpwd,)
#  connection.autocommit = True
  return connection

def load(conn, cmds):
  with conn.cursor() as cursor:
    for cmd in cmds:
      cursor.execute(cmd)
    conn.commit()

def loadTripIds():
  ids=[]
  file = open("/home/mar32/trip_idNumbers.txt", 'r')
  lines = file.readlines()
  file.close()
  for item in lines:
    ids.append(int(item))
  return ids


if __name__ == '__main__':
    # Read arguments and configurations and initialize
    print("Consumer mode activated\n")
    args = ccloud_lib.parse_args()
    config_file = args.config_file
    topic = args.topic
    conf = ccloud_lib.read_ccloud_config(config_file)
        tripNums = loadTripIds()
    goodData = 0#COUNT OF VALID DATA
    badData = 0 # COUNT OF DATA THAT IS REMOVED
    breadData = []
    tripData = []
    breadStart = "INSERT INTO BreadCrumb VALUES("
    tripStart = "INSERT INTO Trip VALUES("
    date=""

    # Create Consumer instance
    # 'auto.offset.reset=earliest' to start reading from the beginning of the
    #   topic if no committed offsets exist
    consumer_conf = ccloud_lib.pop_schema_registry_params_from_config(conf)
    consumer_conf['group.id'] = 'python_example_group_1'
    consumer_conf['auto.offset.reset'] = 'earliest'
    consumer = Consumer(consumer_conf)

    # Subscribe to topic
    consumer.subscribe([topic])

    # Process messages
    attempt = False
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                # No message available within timeout.
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                print("Waiting for message or event/error in poll()")
                if (attempt == True):
                    print("Exiting now...")
                    break
                else:
                    time.sleep(10.0)
                    attempt = True
                continue
            elif msg.error():
                print('error: {}'.format(msg.error()))
            else:
                # Check for Kafka message
                attempt = False
                record_key = msg.key()
                record_value = msg.value()
                data = json.loads(record_value)
                #print(data)
                triper = data['numTrip']
                timer = data['actTime']
                date = data['date']
                lon = data['longitude']
                later = data['latitude']
                dire = data['direction']
                veloc = data['velocity']
                veh = data['vehId']
                if triper and timer and date and lon and later and dire and veloc and veh and direCheck(dire) and timeCheck(timer):
                    goodData+=1
                    #print("Consumed record with key {} and value {}, passed validations, and updated total count to {}".format(record_key, record_value, goodData))
                    month = checkMonth(date)
                    newDate = "20" + date[-2:] + "-" + month + "-" + date[:2]
                    Time = int(timer)
                    hours = Time // 3600
                    Time -= (hours * 3600)
                    minutes = Time // 60
                    seconds = Time - (minutes * 60)
                    tstamp = newDate + " " + str(hours) + ":" + str(minutes) + ":" + str(seconds)
                    if(int(triper) not in tripNums):
                        service_key = checkDay(newDate) #what day of week
                        tripDir = 'NULL' #out / back
                        route_id = 'NULL'
                        tripData.append(tripStart + str(triper) + ", " + str(route_id) + ", " + str(veh) + ", '" + service_key + "', " + tripDir + ");")
                        tripNums.append(int(triper))
                    breadData.append(breadStart + "'" + str(tstamp) + "', " + str(later) + ", " + str(lon) + ", " + str(dire) + ", " + str(veloc) + ", " + str(triper) + ");")
                else:
                    badData +=1
            #        print("Record does not pass the vibe check")
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
        filename = "/home/mar32/data/" + date + "20_Parsed.json"
        file = open("/home/mar32/insertFile.txt", 'a')
        strin= filename + " has consumed a count of " + str(goodData) + " lines \n"
        file.write(strin)
        file.close()
        breadData.append("SELECT * FROM BreadCrumb;")
        tripData.append("SELECT * FROM Trip;")
        file = open("/home/mar32/trip_idNumbers.txt", 'w')
        for item in tripNums:
            file.write(str(item))
            file.write('\n')
        file.close()
        print('\n', "Valid data: {}\n Invalid data: {}".format(goodData, badData))
        #print("\n",tripData,"\n")
        #print("\n",breadData,"\n")
        DBname = "postgres"
        DBuser = "postgres"
        DBpwd = "Letmein67!"
        conn = dbconnect()
        load(conn, tripData)
        load(conn, breadData)                                                                                            
