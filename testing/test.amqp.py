import pika

# Connection parameters
amqp_url = "amqps://anonymous:anonymous@dd.weather.gc.ca"
exchange = "q_anonymous.sr_subscribe.cap-xml_conf.flare_envirotron"
routing_key = "*.WXO-DD.alerts.cap.#"  # Adjust this to subscribe to specific data

# Establish connection
params = pika.URLParameters(amqp_url)

connection = pika.BlockingConnection(params)
channel = connection.channel()

# Declare exchange (it must match the one used by ECCC)
channel.exchange_declare(exchange=exchange, exchange_type='topic', durable=True)

# Create a temporary queue and bind it to the exchange with the routing key
result = channel.queue_declare('q_anonymous_flare')
queue_name = result.method.queue
queue_name = ""
channel.queue_bind(queue_name,exchange,routing_key )

print(f"Listening for messages on routing key: {routing_key}")

# Callback function to handle received messages
def callback(ch, method, properties, body):
    print(f"Received message: {body.decode()}")

# Start consuming messages
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping...")
    connection.close()
