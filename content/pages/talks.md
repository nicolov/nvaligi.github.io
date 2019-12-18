Title: Talks
Slug: talks

<hr>

<h3>2019</h3>

<hr>

<h3 style="margin-bottom: -0.5em">
        Concurrency in ROS 1 and 2: from AsyncSpinner to MultithreadedExecutor
</h3>

<i>ROS Conference 2019</i> &nbsp; <a href="https://vimeo.com/379127709">Video</a> &nbsp; <a href="https://roscon.ros.org/2019/talks/roscon2019_concurrency.pdf">Slides</a>

Unexpected latency is a common problem in ROS-based stacks. This talk
discusses how the ROS runtime maps ROS primitives like publish/subscribe into
OS threads for concurrent execution, and what ROS APIs we can use to control
this process. The second part of the talk covers how the Linux scheduler
allocates these threads for execution on typical CPUs, and which knobs can be
used to optimize this process for robotics applications.

<!-- -->

<h3 style="margin-bottom: -0.5em">
        Optimizing after the optimizer: Link Time and Profile Guided Optimization
</h3>

<i>Italian C++ Conference 2019</i> &nbsp; <a href="https://www.italiancpp.org/itcppcon19-talks/#5">Video and slides</a>

Link Time Optimization (LTO) and Profile Guided Optimization (PGO) are two
complementary techniques for improving the performance of C++ code beyond what’s
normally achieved by optimizing compilers. In most projects, optimization and
inlining opportunities are limited because C++ inherits the concept of
independent translation units from C. LTO sidesteps this issue by deferring
emission of the final binary code to the linker. After turning on LTO, Firefox
saw 5% and up improvements in some benchmarks. PGO uses profiling data collected
at runtime to optimize decisions made by the compiler, like branch predictions
and code placement. This talk will explore LTO and PGO as implemented by clang.
We’ll show how to enable these features in an example project, and dissect the
generated code to understand how they work.

<hr>

<h3>2018</h3>

<hr>

<h3 style="margin-bottom: -0.5em">
        Lessons learned building a self-driving car on ROS
</h3>

<i>ROS Conference 2018</i> &nbsp; <a href="https://vimeo.com/292693011">Video</a> &nbsp; <a href="https://roscon.ros.org/2018/presentations/ROSCon2018_LessonsLearnedSelfDriving.pdf">Slides</a>

Cruise Automation’s self driving car runs on top on ROS. This talk will share
some of the lessons we learned while scaling up the ROS stack to a very complex
Robotics problem and 500+ engineers. We will talk about performance,
reliability, code organization and health, and the ways we have found ROS to
excel or fall short.
