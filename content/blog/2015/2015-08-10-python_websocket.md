Title: Automatic reconnection of Websockets in Autobahn
Date: 2015-08-10
Category: web, backend, python
Slug: automatic-reconnection-websockets-autobahn
Summary: Websockets are an useful technology with lots of applications. Let's make them more reliable by detecting dropped connections and automatically re-creating them. We use Python and the Autobahn library.

After years spent fiddling with inferior technologies, web developers finally have a way to do slick and real-time two-way communication between browser and server. This functionality comes in the way of the Websocket API, which is supported in most [reasonably modern](http://caniuse.com/#feat=websockets) browsers.

Websockets are not only used within the browser though. Their simple message-based API can be successfully leveraged for communications of all kinds on top of TCP. In the case of Python, multiple libraries are available. Of these, [AutobahnJS](https://github.com/tavendo/AutobahnPython) looked the most promising to me due to:

- support for both Twisted and Python's core `asyncio`, for future proofing
- extensive test suite
- great examples and documentation

## The basic example

Getting started with Autobahn is easy with the included [examples](https://github.com/tavendo/AutobahnPython/tree/master/examples/asyncio/websocket/echo). However, this simple setup is not robust due to the very nature of TCP. Dropped connections are not detected until one of the two parties tries to send the message. This is usually not an issue for browser use, since the user would frequently refresh the page relatively frequently anyway.

On the other hand, server-to-server communication requires better handling of unstable connections. In the following sections, we will look at ways to make Websockets more resilient and re-estabilish the connection in case of problems.

## Pinging to detect broken connections

In our example setup, the server is available at a fixed IP address and waits for incoming connections from the client. Luckily, the Websocket protocol provides a ping/response mechanism to keep the connection alive (some more information on heartbeat pings is available [here](http://django-websocket-redis.readthedocs.org/en/latest/heartbeats.html)).

On the server, we modify the example to set additional protocol options:
    
    factory = WebSocketServerFactory(debug=False)
    factory.protocol = MyServerProtocol
    # enable automatic pinging
    factory.setProtocolOptions(autoPingInterval=5,
                               autoPingTimeout=2)

With this change, the server will detect a dropped connection after at most 5+2 seconds, i.e. once the ping timeout is over.

At this stage, the client is still unable to detect dropped connections until it tries to send a message. To solve the problem, we add logic to keep track of the time elapsed since the last ping request. This functionality is implemented as additional methods in the `WebSocketClientProtocol` subclass, as follows:

```
from autobahn.asyncio.websocket import WebSocketClientProtocol, \
WebSocketClientFactory

class MyClientProtocol(WebSocketClientProtocol):
    KEEPALIVE_INTERVAL = 5

    def check_keepalive(self):
        last_interval = time.time() - self.last_ping_time

        if last_interval > 2*self.PING_INTERVAL:
            # drop connection
            self.dropConnection(abort=True)
        else:
            # reschedule next check
            self.schedule_keepalive()

    def schedule_keepalive(self):
        """ Store the future in the class to cancel it later. """
        self.keepalive_fut = loop.call_later(self.PING_INTERVAL,
                                             self.check_keepalive)

    def onOpen(self):
        """ Start scheduling the keepalive check. """
        self.last_ping_time = time.time()
        self.schedule_keepalive()

    def onPing(self, payload):
        """ Respond to the ping request. """
        self.last_ping_time = time.time()
        self.sendPong(payload)

    def connection_lost(self, exc):
        """ Cancel the scheduled future. """
        self.keepalive_fut.cancel()
```

## Automatic reconnection

Thanks to the automatic ping, both client and server will detect dropped connections in a timely manner and close the connection. However, we would still like the client to try to reconnect indefinitely. First, we modify the `connection_lost` method to stop the event loop:

```
class MyClientProtocol(WebSocketClientProtocol):
    # ...

    def connection_lost(self, exc):
        """ Cancel the future and stop the event loop. """
        self.keepalive_fut.cancel()
        loop.stop()
```

We also add a `while True:` loop in the main code of the module, with a timeout to account for dropped packets during the initial connection:

```

while True:
    fut = loop.create_connection(factory, address, port)

    try:
        transport, protocol = loop.run_until_complete(
                                        asyncio.wait_for(fut, 5))
    except asyncio.TimeoutError:
        continue

    loop.run_forever()

    # a little timeout before trying again
    loop.run_until_complete(asyncio.sleep(5))

loop.close()

```

## Simulating dropped connections

Disconnecting the Ethernet cable to simulate dropped connections gets boring very quickly (especially with servers on the cloud..) Use these `iptables` commands to start dropping all packets exchanged with `$SERVER_IP`:

    iptables -A INPUT -s $SERVER_IP -j DROP;
    iptables -A OUTPUT -d $SERVER_IP -j DROP

and this one to get rid of the filter when done:

    iptables -D INPUT -s $SERVER_IP -j DROP;
    iptables -D OUTPUT -d $SERVER_IP -j DROP

## Conclusions

We have seen how to set up keepalive pings in the Python Autobahn Websocket library to quickly detect dropped connections and close them. With a little addition of code and some familiarity with Python's `asyncio` event loop, the client will also be able to re-estabilish dropped connections to the server.
