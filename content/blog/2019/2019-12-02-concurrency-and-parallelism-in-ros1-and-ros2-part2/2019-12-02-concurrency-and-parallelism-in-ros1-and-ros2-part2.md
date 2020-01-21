Date: 2019-12-02
Slug: concurrency-and-parallelism-in-ros1-and-ros2-part-2
Summary: Concurrency and parallelism in ROS 1 and ROS 2 (part 2)
Title: Concurrency and parallelism in ROS 1 and ROS 2 (part 2)
Tags: robotics, frameworks, ROS

This is the second article in a series that tries to give developers the right
knowledge about tackling performance (and latency in particular) problems with
ROS. The [previous article]() covered the journey from the ROS API to Linux
threads. This article will complete the journey by introducing how these threads
are mapped to Linux threads.

*This article is partially based on my presentation at ROSCon 2019.*

## The toolbox

As we've seen in the previous article, the ROS API offers `CallbackQueue`s and
`Spinner`s to control how specific callbacks and topics are mapped onto OS
threads. The next step is to control how these threads are mapped to CPU cores.
That's the job of the OS scheduler, which keeps a list of active threads
waiting for CPU time, and multiplexes them on invidual CPU cores.

Since resuming, swapping, or pausing a thread incurs quite a bit of latency,
the choices made by the OS scheduler have a big impact on the overall
performance of the system. The best option is just to avoid the problem
altogether. As long the stack doesn't spawn more threads than there are CPU
cores, the job of the scheduler is easy. Since _one thread = one CPU core_,
application-level APIs (eg. spinners) are enough to give the developer full
control over the CPU.

However, I've never seen a ROS stack that manages to achieve this goal. In ROS
1, even the simplest C++ node spawns at least 5 threads. Granted, most of them
are IO-bound (for example waiting on network sockets), but that's still quite a
lot of threads for the kernel to manage. This means that we'll need to introduce
OS-level tools to control how threads are mapped onto CPU cores.

The next sections will introduce the 4 most commonly used tools for this in
Robotics:

- thread priorities
- the deadline scheduler
- a kernel with real-time (`PREEMPT_RT`) patches
- CPU affinities and `cpuset`s

## Thread priorities

Assigning thread priorities is the most intuitive and widely known tool to
control scheduling. Threads with higher priority _tend to_ get more CPU time
over time (we'll see more about this later). Priorities can be set with the
`nice` command line tool or the `setpriority(2)` syscall.

While priorities are a useful tool, they're not sufficient for robotics
applications. The default scheduling algorithm in Linux (`SCHED_OTHER`) is
based on time-sharing, and therefore allows a low priority thread to steal CPU
time away from an higher priority one, as long as the overall distribution of
CPU time is met.

Luckily, Linux offers other scheduling policies that offer more control to the
developer.

## The deadline scheduler

The deadline scheduler (`SCHED_DEADLINE`) is an alternative scheduler that
individual threads can opt in to. Deadline-scheduled threads inform the kernel
that they require `n` microseconds of CPU time every time period of `m`
milliseconds. After running a schedulability check to ensure that all
deadline-scheduled threads can co-exist on the machine, the scheduler
guarantees each kernel their time slice. Deadline scheduled tasks have
priority over all others in the system, and are guaranteed not to interfere
with each other.

For reference, it's actually fairly straightfoward for a task to opt in
to the deadline scheduling class. Here, the task declares that it needs
10 milliseconds of CPU time every 30 milliseconds.

```cpp
struct sched_attr attr;

attr.size = sizeof(attr);
attr.sched_flags = 0;
attr.sched_nice = 0;
attr.sched_priority = 0;

/* This creates a 10ms/30ms reservation */
attr.sched_policy = SCHED_DEADLINE;
attr.sched_runtime = 10 * 1000 * 1000;
attr.sched_period = attr.sched_deadline = 30 * 1000 * 1000;

int ret = sched_setattr(0, &attr, flags);
```

## Real-time capable kernel

`SCHED_DEADLINE` is a clear improvement over the deadline scheduler in terms of
latency, but there's still a problem. The kernel might still have to interrupt
user tasks to run housekeeping chores and service syscalls.

This problem can be solved by using a

## CPU core affinity and cpusets

# Wrapping up

## Conclusion
