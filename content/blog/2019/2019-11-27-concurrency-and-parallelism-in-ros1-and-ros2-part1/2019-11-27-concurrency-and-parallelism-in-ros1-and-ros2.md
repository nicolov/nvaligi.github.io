Date: 2019-11-27
Slug: concurrency-and-parallelism-in-ros1-and-ros2-application-apis
Summary: Concurrency and parallelism in ROS 1 and ROS 2: application APIs
Title: Concurrency and parallelism in ROS 1 and ROS 2: application APIs
Tags: robotics, frameworks, ROS

Many of the ROS stacks I've worked have had trouble with unexpected latency
and jitter. These performance issues are often caused by the peculiar way in
which the framework manages concurrency and parallelism. This article
discusses the basics of concurrency in ROS 1 and 2, and how to use their APIs
to get better control over performance.

*This article is partially based on my presentation at ROSCon 2019.*

The typical ROS stack today is a patchwork of mostly-open-source code running
in independent nodes, and thus, in separate OS processes. More refined setups
use *nodelets* to take advantage of threading and reduce serialization
overhead. However, it remains true that many stacks leave a lot of performance
on the table due to sub-optimal use of concurrency primitives. At a human
level, it seems that there's small intersection between the people who enjoy
Robotics algorithms and those who like to tinker with Linux threading
primitives.

This article is the first of a series that tries to peek under the covers of
how concurrency works in ROS 1 (and 2) and present tools to improve behavior
at the application, framework, and OS level. In this first article, we're
going to look at the application and framework level, essentially describing
how ROS APIs like callbacks map to OS threads. As such, we're mostly going to
be focusing on the ROS runtime and application facing APIs. The next article
is going to continue this journey all the way from OS threads to CPU cores.

## The basic ROS execution model

`ros::init()`, which is the first line of code in any ROS 1 node, spawns a
couple of threads to manage incoming messages and run the corresponding
callbacks. As shown below, the *network* thread listens for incoming messages
on TCP sockets and pushes them on the *callback queue* after deserializing
them. The *spinner* thread pops messages from the queue and runs the user
code.

<img src="{attach}callback_queue.svg"
     style="max-width: 80%; transform: scale(0.9);"
     class="img-center" />

If the callback execution time is short enough, everything runs well even if
the CPU has a single core. As shown below, messages arrive at a fixed rate and
wake up the spinner thread, which runs the user-provided code and goes to
sleep again, well before the next message is expected to come in.

<img src="{attach}1-single-node.svg"
     style="max-width: 80%; transform: scale(1.5); padding: 1em;"
     class="img-center" />

However, if the callback execution time increases, execution periods would in
theory begin to overlap with each other. This is clearly impossible on a
single thread, as only one callback instance can be running at any given time.
Therefore incoming messages would start to queue up on the subscriber side
(this is all handled by the ROS runtime, with no intervention of knowledge
required from users).

<img src="{attach}2-overlap.svg"
     style="max-width: 80%; transform: scale(1.5); padding: 1em;"
     class="img-center" />

The size of the incoming message queue is set on the `subscribe` call. A sane
value might be `0`, so that no message gets dropped (at the cost of increased
latency).

## Multithreaded spinning

Dropping messages at the framework level is undesiderable in many cases,
because the application logic can usually deal with the backlog in smarter
ways. If indeed that's the case, the hope might be to throw to more hardware
at the problem. This means running callbacks in parallel (ie *spinning*) over
multiple CPU cores.

In ROS 1, this is achieved by replacing the default `ros::spin()` call with
either a `MultiThreadedSpinner` or an `AsyncSpinner`:

```cpp
ros::MultiThreadedSpinner spinner(2); // 2 threads
spinner.spin();

// or

ros::AsyncSpinner spinner(2);
spinner.start();
```

Both will spawn a number of spinner threads, but `MultiThreadedSpinner` will
block the current thread, whereas `AsyncSpinner` will do all its work in the
background.

**Side note**

Neither multithreaded spinner actually works as expected in this particular
example. By default, callback executions are protected by a mutex such that
only one callback per subscription can execute at any given time. The fix is
simple:

```cpp
ros::SubscribeOptions ops;
ops.template init<std_msgs::String>("chatter", 1000, chatterCallback);
ops.allow_concurrent_callbacks = true;
ros::Subscriber sub = nh.subscribe(ops);
```

**End of side note**

With a multithreaded spinner, two or more threads can run callbacks in
*parallel*, that is at the same time, provided that there are enough available
CPU cores in the system. This might increase throughout to the point where
queueing is avoided, as shown below:

<img src="{attach}3-multithreaded.svg"
     style="max-width: 80%; transform: scale(1.5); padding: 1em;"
     class="img-center" />

Of course, parallelism brings some headaches in terms of synchronization and
locking because multiple threads might now be accessing shared state at the
same time. Sprinkle `std::mutex` accordingly.

## Priority inversion

Now let's make things a bit more realistic:

<img src="{attach}4-priority-inversion.svg"
     style="max-width: 80%; transform: scale(1.5); padding: 1em;"
     class="img-center" />

Here we added a second callback (orange) on a second topic. The new callback
has *higher priority* than the old one. For example, we might have a planner
that receives both occupancy map updates and ranging messages for close
obstacles. If a new ranging message comes in saying that the robot is about to
crash, the planner should replan right away, rather than queueing up this
important message behind less time-sensitive occupancy map updates.

With a plain multi-threaded spinner, the high-priority callback might be stuck
waiting behind the low-priority (green) one. If this callback is on the
critical path from sensor to controls, we're increasing the reaction time of
the robot for no good reason.

If an orange message arrives within the time segments highlighted with the
thick black bars, there are no threads available to pick it up, and it will be
queued behind another lower-priority task. This is exactly what we don't want
to happen, and is called **priority inversion** in the literature of embedded
systems.

One might be tempted to increase the number of worker threads to avoid
queueing, but that is really just a band-aid, and not a real solution. For
reasons that we'll discuss in the next article, the number of callback threads
should track the number of CPU cores, and not the number of independent queues
in the system.

## Multiple callback queues

A better approach is to divide the callbacks in two or more queues
according to their priority, create multiple spinner threads, and assign a
queue to each of the spinners. The easiest way to achieve this in ROS 1 is by
partitioning subscriptions across different `NodeHandle`s:

```cpp
// Create a second NodeHandle
ros::NodeHandle secondNh;
ros::CallbackQueue secondQueue;
secondNh.setCallbackQueue(&secondQueue);
secondNh.subscribe("/high_priority_topic", 1,
                   highPriorityCallback);
```

```cpp
// Spawn a new thread for high-priority callbacks.
std::thread prioritySpinThread([&secondQueue]() {
    ros::SingleThreadedSpinner spinner;
    spinner.spin(&secondQueue);
});
prioritySpinThread.join();
```

The concept is similar in ROS 2, with the `Executor` interface replacing
spinners:

```cpp
// Create a Node and an Executor.
rclcpp::executors::SingleThreadedExecutor executor1;
auto node1 = rclcpp::Node::make_shared("node1");
executor1.add_node(node1);

// Create another.
rclcpp::executors::SingleThreadedExecutor executor2;
auto node2 = rclcpp::Node::make_shared("node2");
executor2.add_node(node2);

// Spin the Executor in a separate thread.
std::thread spinThread([&executor2]() {
    executor2.spin();
});
```

With this change, the ROS runtime will assign callbacks from different
subscriptions to their dedicated spinner threads. Therefore, it's possible to
make sure that there's always a thread available to pick up high-priority
work. Of course, this does *not* guarantee that high-priority callbacks will
actually be worked on by the CPU, because the Linux scheduler could decide to
let some other thread use the CPU instead.

## Conclusion

In fact, this is exactly the topic of the next article. Up until now, we have
presented the tools (multiple spinners and queues) that ROS provides to
control how incoming messages and their callbacks are mapped onto OS threads.
In the next article, we're going to complete the discussion and learn how the
Linux kernel maps these threads onto physical CPU cores.
