import websocket, json, asyncore, threading, time

class HookboxClient:
	def __init__(self, **kwargs):
		self.host = kwargs.pop('host', 'localhost')
		self.port = kwargs.pop('port', 8001)
		self.cookie_string = kwargs.pop('cookie_string', '')
		self.onOpen = kwargs.pop('onOpen', None)
		self.onError = kwargs.pop('onError', None)
		self.onSubscribed = kwargs.pop('onSubscribed', None)
		
		self.command_id = 1
		self.subscriptions = {}
		
		self.ws = websocket.WebSocket('ws://%s:%s/ws' % (self.host, self.port), onopen = self.__onOpen, onmessage = self.__onMessage, onclose = self.__OnClose)
		
		if kwargs: raise ValueError('Unexpected argument(s): %s' % ', '.join(kwargs.values()))
		
	def subscribe(self, channel):
		self.send("SUBSCRIBE", {"channel_name": channel})
		
	def disconnect(self):
		self.ws.close()
		
	def send(self, command, data):
		self.ws.send(json.dumps([self.command_id, command, data]) + '\r\n')
		self.command_id += 1
		
	def __onOpen(self):
		self.send("CONNECT", {"cookie_string": self.cookie_string})

	def __onMessage(self, data):
		data = json.loads(data)
		if data[1] == 'CONNECTED':
			#unused data[2]['name']?
			if self.onOpen: self.onOpen()
		elif data[1] == 'SUBSCRIBE':
			self.subscriptions[data[2]['channel_name']] = HookboxClientSubscription(self, data[2]['channel_name'])
			if self.onSubscribed: self.onSubscribed(data[2]['channel_name'], self.subscriptions[data[2]['channel_name']])
		elif data[1] == 'PUBLISH':
			if self.subscriptions[data[2]['channel_name']].onPublish: self.subscriptions[data[2]['channel_name']].onPublish(data[2])
		elif data[1] == 'ERROR':
			if self.onError: self.onError(data[2])
		else:
			#TODO: handle other commands
			pass
		
	def __OnClose(self):
		pass
		
class HookboxClientSubscription:
	def __init__(self, client, name):
		self.client = client
		self.name = name
		self.onPublish = None

	def publish(self, data):
		self.client.send("PUBLISH", {"channel_name": self.name, "payload": json.dumps(data)})
		
class HookboxClientSimple:
	def __init__(self, host, port, channel, onPublish):
		self.channel = channel
		self.onPublish = onPublish
	
		self.hookbox = HookboxClient(host = host, port = port, onOpen = self.__onOpen, onError = self.__onError, onSubscribed = self.__onSubscribed)
		
		t = threading.Thread(target = self.__loop)
		t.daemon = True
		t.start()
		
		self.lock = threading.Lock()
		self.lock.acquire()
		self.lock.acquire()
		
	def publish(self, data):
		self.subscription.publish(data)
	
	def __onOpen(self):
		self.hookbox.subscribe(self.channel)

	def __onError(self, error):
		print error['msg']

	def __onSubscribed(self, channelName, subscription):
		self.subscription = subscription
		subscription.onPublish = self.onPublish
		self.lock.release()
		
	def __loop(self):
		asyncore.loop(timeout = 0.5) #this timeout is a bit hackish - I have to write a new WebSocket class to fix this, I guess

