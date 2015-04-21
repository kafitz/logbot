import json
import redis

class RedisMessage():

    def __init__(self):
        self.r = redis.client.StrictRedis(host='192.168.5.10', port=6379)
        self.redis_channel = 'irc_msg'
        self.irc_channel = '#war_room'

    def send(self, message):
        msg = {
            'channel': self.irc_channel,
            'text': message
        }
        print("Sending message: {}".format(message))
        self.r.publish(self.redis_channel, json.dumps(msg))
