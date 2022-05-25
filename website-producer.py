#!/usr/bin/env python
#
# Copyright 2020 Confluent Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# =============================================================================
#
# Produce messages to Confluent Cloud
# Using Confluent Python Client for Apache Kafka
#
# =============================================================================

from confluent_kafka import Producer, KafkaError
import json
import ccloud_lib
import time
import argparse
from random import randint
from datetime import datetime

if __name__ == '__main__':

    # Read arguments and configurations and initialize
#-f -t -m -d This section is used if going to insert lots of files and using the bash to do so. 
 #   parser = argparse.ArgumentParser()
#    parser.add_argument("-f", "--config_file", required=True)
#    parser.add_argument("-t", "--topic", required=True)
#    parser.add_argument("-m", "--month", required=True)
#    parser.add_argument("-d", "--day", required=True)
#    args=parser.parse_args()
    args = ccloud_lib.parse_args()
    config_file = args.config_file
    topic = args.topic
#    month = args.month
#    day = args.day
    conf = ccloud_lib.read_ccloud_config(config_file)

    filename = "/home/mar32/data/" + datetime.today().strftime('%Y-%m-%d') + "_Event.json"
#    filename = "/home/mar32/data/2022-" + month + "-" + day + "_Event.json"
    # Create Producer instance
    producer_conf = ccloud_lib.pop_schema_registry_params_from_config(conf)
    producer = Producer(producer_conf)

    # Create topic if needed
    ccloud_lib.create_topic(conf, topic)

    delivered_records = 0

    # Optional per-message on_delivery handler (triggered by poll() or flush())
    # when a message has been successfully delivered or
    # permanently failed delivery (after retries).
    def acked(err, msg):
        global delivered_records
        """Delivery report handler called on
        successful or failed delivery of message
        """
        if err is not None:
            print("Failed to deliver message: {}".format(err))
        else:
            delivered_records += 1
            #print("Produced record to topic {} partition [{}] @ offset {}"
                  #.format(msg.topic(), msg.partition(), msg.offset()))
    f=open(filename)
    lines = json.load(f)
    f.close()
    count = 1
    for n in lines:
        record_key = n['tripId'];
        record_value = json.dumps({'count': count,'tripId':n["tripId"],'vehId' :n["vehId"], "leaveTime" :n["leaveTime"],"train":n["train"],"routeNumber":n["routeNumber"],"direction":n["direction"],"serviceKey":n["serviceKey"],"stopTime":n["stopTime"],"arriveTime":n["arriveTime"],"dwell":n["dwell"],"locationId":n["locationId"],"door":n["door"],"lift":n["lift"],"ons":n["ons"],"offs":n["offs"],"estimatedLoad":n["estimatedLoad"],"maximumSpeed":n["maximumSpeed"],"trainMileage":n["trainMileage"],"patternDistance":n["patternDistance"],"locationDistance":n["locationDistance"],"xCoor":n["xCoor"],"yCoor":n["yCoor"],"source":n["source"],"sched":n["sched"]})
        #print("Producing record: {}\t{}".format(record_key, record_value))
        count+=1
        producer.produce(topic, key=record_key, value = record_value,on_delivery=acked)
        # p.poll() serves delivery reports (on_delivery)
        # from previous produce() calls.
        producer.poll(0)

    producer.flush()
    print("{} messages were produced to topic {}!".format(delivered_records, topic))
    eventFile = "/home/mar32/data" + datetime.today().strftime('%Y-%m-%d') + '_Event.json'
    file = open("/home/mar32/insertFile.txt", 'a')
    strin= eventFile + " has consumed a count of " + str(count) + " lines \n"
    file.write(strin)
    file.close()
