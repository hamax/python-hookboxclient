#!/usr/bin/python

import hookboxclient, time

def onPublish(frame):
	print '[%s] %s: %s' % (frame['datetime'], frame['user'], frame['payload'])

if __name__ == '__main__':
	hookbox = hookboxclient.HookboxClientSimple('localhost', 8001, 'chat', onPublish)
	
	#HookboxClientSimple creates a new thread for listening, so you don't have to worry about it
	while True: 
		hookbox.publish('I have some data.')
		time.sleep(10)

