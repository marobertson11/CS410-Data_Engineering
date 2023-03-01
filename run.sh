#!/bin/sh
cd ./examples/clients/cloud/python
virtualenv ccloud-venv
source ./ccloud-venv/bin/activate
./topic_clean.py -f /home/mar32/examples/librdkafka.config -t datajob
sleep 5
./data_producer.py -f /home/mar32/examples/librdkafka.config -t datajob 
sleep 5
./data_consumer.py -f /home/mar32/examples/librdkafka.config -t datajob
sleep 5
./topic_clean.py -f /home/mar32/examples/librdkafka.config -t datajob

./topic_clean.py -f /home/mar32/examples/librdkafka.config -t eventjob
sleep 5
./website-producer.py -f /home/mar32/examples/librdkafka.config -t eventjob
sleep 5
./website-consumer.py -f /home/mar32/examples/librdkafka.config -t eventjob
sleep 5
./topic_clean.py -f /home/mar32/examples/librdkafka.config -t eventjob
STR=$(date +%Y-%m-%d)".json"
FILE=/home/mar32/data/$STR
gsutil cp $FILE gs://cs410data
echo complete
