import pika

parameters = pika.URLParameters('amqp://alpha:alpha@10.0.0.41')

connection = pika.BlockingConnection(parameters)

channel = connection.channel()

channel.basic_publish('test',
                      'flare',
                      'message body value',
                      pika.BasicProperties(content_type='text/plain',
                                           delivery_mode=pika.DeliveryMode.Persistent))

channel.basic_publish('test',
                      'flare',
                      'message body value',
                      pika.BasicProperties(content_type='text/plain',
                                           delivery_mode=pika.DeliveryMode.Persistent))

channel.basic_publish('test',
                      'flare',
                      'message body value',
                      pika.BasicProperties(content_type='text/plain',
                                           delivery_mode=pika.DeliveryMode.Persistent))

connection.close()