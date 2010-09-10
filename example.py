#!/usr/bin/python

import hookboxclient, asyncore

def onOpen():
	hookbox.subscribe('chat')
	
def onError(error):
	print error['msg']

def onSubscribed(channelName, subscription):
	if channelName == 'chat':
		subscription.onPublish = onChatPublish
		subscription.publish("Hey, guys!")
	
def onChatPublish(frame):
	print '[%s] %s: %s' % (frame['datetime'], frame['user'], frame['payload'])

if __name__ == '__main__':	
	hookbox = hookboxclient.HookboxClient(onOpen = onOpen, onError = onError, onSubscribed = onSubscribed)

	try:
		asyncore.loop()
	except KeyboardInterrupt:
		hookbox.disconnect()

