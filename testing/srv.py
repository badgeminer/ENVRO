import sarracenia
import sarracenia.bulletin
import sarracenia.flow
import sarracenia.flow.subscribe
import sarracenia.instance
import sarracenia.sr
class MySubscriber(sarracenia.flow.subscribe.Subscribe):
    def gotMsg(self, msg):
        print(f"Received message:\n{msg}\n")

sub = MySubscriber()
sub.config(queue=True, keys=["weather.warnings"])  # Modify keys as needed
sub.run({'acceptUnmatched': True, 'download': True, 'mirror': False})
