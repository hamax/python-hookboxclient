import socket, json

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
		self.buff = ''
		
		#connect
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((self.host, self.port))
		
		#handshake
		self.handshake = True
		self.socket.send('GET /ws HTTP/1.1\r\n')
		self.socket.send('Host: %s:%s\r\n' % (self.host, self.port))
		self.socket.send('Connection: Upgrade\r\n')
		self.socket.send('Upgrade: WebSocket\r\n')
		self.socket.send('\r\n')
		self.socket.send('\r\n')
		
		if kwargs: raise ValueError('Unexpected argument(s): %s' % ', '.join(kwargs.values()))
		
	def subscribe(self, channel):
		self.send("SUBSCRIBE", {"channel_name": channel})
		
	def disconnect(self):
		self.socket.close()
		
	def send(self, command, data):
		self.socket.send('\x00' + (json.dumps([self.command_id, command, data]) + '\r\n').encode('utf-8') + '\xff')
		self.command_id += 1
		
	def close(self):
		self.socket.close()

	def __onMessage(self, data):
		data = json.loads(data)
		if data[1] == 'CONNECTED':
			#unused data[2]['name']?
			if self.onOpen: self.onOpen()
		elif data[1] == 'SUBSCRIBE':
			if 'presence' in data[2]:
				#subscribed
				self.subscriptions[data[2]['channel_name']] = HookboxClientSubscription(self, data[2]['channel_name'])
				if self.onSubscribed: self.onSubscribed(data[2]['channel_name'], self.subscriptions[data[2]['channel_name']])
			else:
				#new member
				pass #TODO: handle presence
		elif data[1] == 'PUBLISH':
			if self.subscriptions[data[2]['channel_name']].onPublish: self.subscriptions[data[2]['channel_name']].onPublish(data[2])
		elif data[1] == 'ERROR':
			if self.onError: self.onError(data[2])
		else:
			#TODO: handle other commands
			pass
		
	def listen(self):
		while 1:
			data = self.socket.recv(1024)
			if not data: 
				print 'connection lost'
				break
			self.buff += data
			commands = self.buff.split('\r\n')
			self.buff = commands[-1]
			for command in commands[:-1]:
				if self.handshake:
					#empty command means handshake is over
					if not command:
						self.handshake = False
						self.send("CONNECT", {"cookie_string": self.cookie_string})
				else:
					while command[0] in ['\x00', '\xff']: command = command[1:]
					self.__onMessage(command)
		self.socket.close()
		
class HookboxClientSubscription:
	def __init__(self, client, name):
		self.client = client
		self.name = name
		self.onPublish = None

	def publish(self, data):
		self.client.send("PUBLISH", {"channel_name": self.name, "payload": json.dumps(data)})

