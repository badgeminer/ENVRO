import pika

# Connection parameters
amqp_url = "amqps://anonymous:anonymous@dd.weather.gc.ca/"
exchange = "q_anonymous.sr_subscribe.cap-xml_conf.flare_envirotron"
routing_key = "*.WXO-DD.alerts.cap.#"  # Adjust this to subscribe to specific data

# Establish connection
params = pika.URLParameters(amqp_url)

testSrv = pika.URLParameters("amqp://flare:flare@10.0.0.41")

connection = pika.BlockingConnection(params)
channel = connection.channel()

connection2 = pika.BlockingConnection(testSrv)
channel2 = connection2.channel()


# Declare exchange (it must match the one used by ECCC)
#channel.exchange_declare(exchange="", exchange_type='topic', durable=True)

# Create a temporary queue and bind it to the exchange with the routing key
result = channel.queue_declare(exchange)#'q_anonymous_flare')
queue_name = result.method.queue
print(queue_name)
channel.queue_bind(queue_name,"xpublic",routing_key )
#result2 = channel2.queue_declare('flare')

print(f"Listening for messages on routing key: {routing_key}")
channel2.basic_publish("","flare","TEST",pika.BasicProperties(content_type='text/plain',
                                           delivery_mode=pika.DeliveryMode.Transient))

# Callback function to handle received messages
def callback(ch, method, properties, body):
    print(f"Received message: {body.decode()}")
    channel2.basic_publish("","flare",f"{ch} {body.decode()}",pika.BasicProperties(content_type='text/plain',
                                           delivery_mode=pika.DeliveryMode.Transient))

# Start consuming messages
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping...")
    connection.close()
    channel2.basic_publish("","flare","Leaving")
    connection2.close()
