Title: Phoenix WebSockets from the ground up
Date: 2016-05-31
Category: elixir
Slug: phoenix-websockets-ground-up
Summary: A look at the internals of Websockets support in the Phoenix web framework on Elixir.

Inspired by the [Phoenix is not your
application](http://youtube.com/watch?v=IDKCSheBc-8) presentation, I dug into
Phoenix's internals to investigate how to use a custom WebSockets protocol
while retaining the well-thought abstractions and patterns.  I'm especially
referring to Phoenix's solid pubsub backends, integration with the Cowboy HTTP
server, and configuration/logging handling.

I was surprised to see that the code involved is very small and readable, with
the exception of some magic patterns to shuffle between various shapes of
return values, GenServer state changes, and the like. On the bright side, such
code would have been hair-pulling to implement in a language without pattern
matching.

What follows is a log of my journey through the code base, and all the moving
pieces that come together for Phoenix's awesome WebSockets support.

## Configuration

First, we take a *top down* look at how a Phoenix application is configured to
handle WebSockets, starting from the user-provided entry point and reaching
the configuration of the Cowboy HTTP server.

### Endpoint (phoenix/endpoint.ex)

Your application's endpoint will use `Phoenix.Endpoint` and have one or more calls to
its `socket` macro to set up the URLs that will be handling websockets. The `socket`
macro accumulates socket information in the `@phoenix_sockets` attribute:

```elixir
defmacro socket(path, module) do
    quote do
        @phoenix_sockets {unquote(path), unquote(module)}
    end
end
```

and the `__before_compile__` macro creates a function that returns that
attribute itself:

```elixir
defmacro __before_compile__(env) do
    sockets = Module.get_attribute(env.module, :phoenix_sockets)

    quote do
        def __sockets__, do: unquote(sockets)
    end
end
```

The `Endpoint` also starts the `Adapter` supervision loop:

```elixir
def start_link do
    Adapter.start_link(@otp_app, __MODULE__)
end
```

### Adapter (phoenix/endpoint/adapter.ex)

The supervisor tree includes a `Phoenix.Endpoint.Server` supervisor, that
we're going to look at next.

### Endpoint.Server (phoenix/endpoint/server.ex)

Calls back to the `CowboyHandler` and starts supervising the `child_spec` it returns.

### Endpoint.CowboyHandler

The `child_spec` function looks at the sockets defined in the `Endpoint`. It
looks up the corresponding transport for each one and passes the bunch to the
`Plug.Adapters.Cowboy` Cowboy adapter.

## Communication

This section traces the flow of data arriving as a WebSockets message as it
bubbles up towards the application logic the developer has implemented. This
will take a *bottom-up* perspective, from the Cowboy handler to the user-
provided callbacks.

### Endpoint.CowboyWebSocket

When incoming messages arrive on the wire, Cowboy calls the appropriate functions on the
`CowboyWebSocket` module. In turn, these pass the payload up to the
corresponding function in the `Transports.WebSocket` module, such as:

```elixir
def websocket_handle({opcode = :text, payload}, req, {handler, state}) do
    handle_reply req, handler, handler.ws_handle(opcode, payload, state)
end
```

### Transport.WebSocket

`Transport.WebSocket` implements the `Socket.Transport` behaviour and uses many convenience functions defined there to handle connection, disconnection, serialization, and deserialization. In a sense, it acts as a middleman between the socket and the channel, shuffling messages back and forth when appropriate.

On *connection*, `Transports.WebSocket` calls back to the `connect` function
in `Socket.Transport`. After setting up a new `Socket` struct that will be
kept as part of the process state, that function calls back the `connect`
function in the user-defined module to handle authentication.

*Incoming messages* (`ws_handle`), are dispatched to the right channel using the `Socket.Transport.dispatch` function, that figures out the right channel by looking at the `HashDict`:

```elixir
def dispatch(%Message{} = msg, channels, socket) do
    channels
    |> HashDict.get(msg.topic)
    |> do_dispatch(msg, socket)
end
```

and then actually sends the payload to the `Channel` process:

```elixir
defp do_dispatch(channel_pid, msg, _socket) do
    send(channel_pid, msg)
    :noreply
end
```

Especially interesting is the `dispatch` function that handles new topic topic
subscriptions, with signature:

```elixir
defp do_dispatch(nil, %{event: "phx_join", topic: topic} = msg, socket) do
```

that checks whether the user has defined a channel corresponding to the
current topic,

```elixir
if channel = socket.handler.__channel__(topic, socket.transport_name) do
    socket = %Socket{socket | topic: topic, channel: channel}
```

has the `Socket` `join` it,

```elixir
Phoenix.Channel.Server.join(socket, msg.payload)
```

and replies positively to the client:

```elixir
{:joined, pid, %Reply{ref: msg.ref, topic: topic, status: :ok, payload: response}}
```

### Channel.Server

As the `Channel` module itself is only a behaviour that user code needs to
adhere to, most of the actual functionality is implemented in the Genserver at
`Channel.Server`. Each new socket connection causes a new `Channel.Server` to
be spun up. Precisely, it's the transport that calls the `join` function in
the `Channel.Server`:

```elixir
def join(socket, auth_payload) do
    ref = make_ref()
    case GenServer.start_link(__MODULE__, {socket, auth_payload, self(), ref}) do
```

in the `init` GenServer callback, the channel asks the `Pubsub.Server` to
subscribe to its topic:

```elixir
PubSub.subscribe(socket.pubsub_server, self(), socket.topic,
```

and then messages itself back the result of the subscription, so that it can
handle messages.

Broadcasts are sent through the pubsub server:

```elixir
def broadcast(pubsub_server, topic, event, payload) do
    PubSub.broadcast pubsub_server, topic, %Broadcast{
      topic: topic,
      event: event,
      payload: payload
    }
end
```

Finally, messages received from the pubsub server are handled by the user's
application logic implemented in the channel's `handle_in` function:

```elixir
def handle_info(%Message{topic: topic, event: event, payload: payload, ref: ref},
                %{topic: topic} = socket) do
    event
    |> socket.channel.handle_in(payload, put_in(socket.ref, ref))
    |> handle_result(:handle_in)
end
```

## Conclusions

While well thought-out, the internals are pretty tightly coupled to the topic-
based nature of Phoenix's WS protocol. Transports, channels, and the pubsub
server all operate by switching messages based on their topic. While flexibile
enough for most clean-slate real time applications, this choice makes it
somewhat hard to retro-fit an existing protocol without overhauling
significant parts of the stack.
