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
from google.cloud import storage


def create_file(self, filename):
  """Create a file.

  The retry_params specified in the open call will override the default
  retry params for this particular file handle.

  Args:
    filename: filename.
  """
  self.response.write('Creating file %s\n' % filename)

  write_retry_params = gcs.RetryParams(backoff_factor=1.1)
  gcs_file = gcs.open(filename,
                      'w',
                      content_type='text/plain',
                      options={'x-goog-meta-foo': 'foo',
                               'x-goog-meta-bar': 'bar'},
                      retry_params=write_retry_params)
  gcs_file.write('abcde\n')
  gcs_file.write('f'*1024*4 + '\n')
  gcs_file.close()
  self.tmp_filenames_to_clean_up.append(filename)

if __name__ == '__main__':
    # Read arguments and configurations and initialize
    print("Consumer mode activated\n")
    args = ccloud_lib.parse_args()
    config_file = args.config_file
    topic = args.topic
    conf = ccloud_lib.read_ccloud_config(config_file)

    # Create Consumer instance
    # 'auto.offset.reset=earliest' to start reading from the beginning of the
    #   topic if no committed offsets exist
    consumer_conf = ccloud_lib.pop_schema_registry_params_from_config(conf)
    consumer_conf['group.id'] = 'python_example_group_B'
    consumer_conf['auto.offset.reset'] = 'earliest'
    consumer = Consumer(consumer_conf)

    # Subscribe to topic
    consumer.subscribe([topic])

    # Process messages
    attempt = False
    total_count = 0
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
                    time.sleep(2.0)
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
                key_parsed = json.loads(record_key)

                count = data['index']
                total_count += count
                send = json.dumps(data, indent=2).encode()
                upload_blob_from_memory("datamaintaince", send, "CS410data-engineering")



    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
