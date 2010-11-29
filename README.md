# python-hookboxclient
python-hookboxclient is a Python Hookbox client library.

## Usage
See the examples.

## API reference

It's very similar to the javascript library (http://hookbox.org/docs/javascript.html) - functions have the same names and parameters

### HookboxClient(host = 'localhost', port = 8001, cookie_string = '', onOpen = None, onError = None, onSubscribed = None)
Returns a HookboxClient connected to a remote host. 
In order to allow communication over this socket, `asyncore.loop()`
must be called by the client.
See example.py

### HookboxClient.subscribe(channel)
Subscribes to the channel.

