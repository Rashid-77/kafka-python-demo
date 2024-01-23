import json
import time
from confluent_kafka import Producer, Consumer
from logger import get_logger

kafka_url = 'broker:9092'

logger = get_logger("ORDER")

logger.info('Order started')
logger.info('wait until kafka is started ...')
# wait until kafka is started and topics are created
time.sleep(30)

c = Consumer({
    'bootstrap.servers': kafka_url,
    'group.id': 'order_group',
    'auto.offset.reset': 'earliest'
})

p = Producer({'bootstrap.servers': kafka_url})
c.subscribe(['product'])

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

p.poll(0)
p.produce('order', json.dumps("how many cups?"), callback=delivery_report)
logger.info('message sent')
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
        z = json.loads(msg.value())
        logger.info(f'Received message: {json.loads(msg.value())}, {cnt}')
        if z.get("cups") > 0:
            time.sleep(2)
            p.produce('order', json.dumps("how many cups?"), callback=delivery_report)
            logger.info('message sent: "how many cups?"')

except KeyboardInterrupt:
    logger.info('stoped')
    c.close()