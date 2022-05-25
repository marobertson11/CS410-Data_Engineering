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

def distConvert(distance):
  if(distance == '0'):
    return 'Out'
  else:
    return 'Back'

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
    tripData = []
    tripStart = "UPDATE Trip SET "
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
                    time.sleep(5.0)
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
                triper = data['tripId']
                veh = data['vehId']
                rouNumb = data['routeNumber']
                dire = data['direction']
                if triper and dire and veh and rouNumb:
                    goodData+=1
                    if(int(triper) in tripNums):
                        newDir = distConvert(dire)
                        tripData.append(tripStart + 'route_id = '  + str(rouNumb) + ", direction = '" + newDir + "' WHERE trip_id = " + triper + ' AND vehicle_id = ' + veh + ';')
                else:
                    badData +=1
            #        print("Record does not pass the vibe check")
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
        eventFile = "/home/mar32/data" + datetime.today().strftime('%Y-%m-%d') + '_Event.json'
        file = open("/home/mar32/insertFile.txt", 'a')
        strin= eventFile + " has consumed a count of " + str(goodData) + " lines \n"
        file.write(strin)
        file.close()
        print('\n', "Valid data: {}\n Invalid data: {}".format(goodData, badData))
        DBname = "postgres"
        DBuser = "postgres"
        DBpwd = "Letmein67!"
        conn = dbconnect()
        load(conn, tripData)
