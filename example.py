#!/usr/bin/python

import hookboxclient

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
	hookbox = hookboxclient.HookboxClient(host = 'akira.hamax.si', port = 8002, onOpen = onOpen, onError = onError, onSubscribed = onSubscribed)

	hookbox.listen()

