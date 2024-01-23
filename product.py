import json
import time
from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient, NewTopic
from logger import get_logger


kafka_url = 'broker:9092'

logger = get_logger("PROD")
logger.info('Product started')
logger.info('wait until kafka is started ...')
# wait until kafka is started
time.sleep(20)  


#------------------------------------------------------------------------------
# Topics creating
a = AdminClient({'bootstrap.servers': kafka_url})
# a.delete_topics(["order", "product"])
new_topics = [NewTopic(topic, num_partitions=3, replication_factor=1) for topic in ["order", "product"]]
# Note: In a multi-cluster production scenario, it is more typical to use a 
# replication_factor of 3 for durability.

# Call create_topics to asynchronously create topics. A dict
# of <topic,future> is returned.
fs = a.create_topics(new_topics)

# Wait for each operation to finish.
for topic, f in fs.items():
    try:
        f.result()  # The result itself is None
        logger.info(f"Topic {topic} created")
    except Exception as e:
        logger.error(f"Failed to create topic {topic}: {e}")
#------------------------------------------------------------------------------

c = Consumer({
    'bootstrap.servers': kafka_url,
    'group.id': 'prod_group',
    'auto.offset.reset': 'earliest'
})

c.subscribe(['order'])
p = Producer({'bootstrap.servers': kafka_url})

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

p.poll(0)
cups = 12
cnt = 0
try:
    while True:
        msg = c.poll(0.3)

        if msg is None:
            continue
        if msg.error():
            logger.info(f"Consumer error: {msg.error()}")
            continue

        cnt += 1
        logger.info(f'Received message: {json.loads(msg.value())}, {cnt}')
        w = {"cups": cups}
        p.produce('product', json.dumps(w), callback=delivery_report)
        logger.info('message sent')
        if cups == 0:
            continue
        cups -= 1

except KeyboardInterrupt:
    logger.info('stoped')
    c.close()