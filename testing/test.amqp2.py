import pika
import pika.amqp_object
import pika.callback
import pika.connection
import pika.data
import pika.delivery_mode
import pika.exchange_type



testSrv = pika.URLParameters("amqp://alpha:alpha@10.0.0.41")


connection2 = pika.BlockingConnection(testSrv)
channel2 = connection2.channel()

#result2 = channel2.queue_declare('flare')


channel2.basic_publish("","flare","TEST")
# Callback function to handle received messages
def callback(ch, method, properties, body):
    print(method.delivery_tag,method)
    
    print(body)
    print(f"Received message: {body.decode()}")
    channel2.basic_ack(delivery_tag=method.delivery_tag)

# Start consuming messages
channel2.basic_consume(queue="flare", on_message_callback=callback)

try:
    channel2.start_consuming()
except KeyboardInterrupt:
    print("Stopping...")
    connection2.close()
