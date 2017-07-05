Date: 2017-07-04
Slug: faster-bazel-remote-caching-benchmark
Summary: Faster Bazel builds with remote caching
Title: Faster Bazel builds with remote caching: a benchmark
Tags: cpp bazel

**tldr;** Remote caching is simple to set up and makes repeated builds _50x_
faster.

In my [previous article](/benchmark-bazel-build-cpp.html), I've benchmarked
the Bazel build system on a C++ project, and found that it performs well, but
doesn't really offer a compelling story over alternatives. In this article,
I'll explore one of Bazel's unique selling points, **remote caching**, and
show that it delivers great speedups.

How remote caching works
------------------------

Most build systems only track file timestamps or other metadata, but Bazel
hashes the _content_ of source code as part of its strict dependency checks.
With such a system in place, caching is trivial, since intermediate build
artifacts can simply be stored and retrieved by recursively aggregating the
hashes of their dependencies in the build graph.

For this benchmark, I've followed the [documentation](https://github.com/bazel
build/bazel/blob/master/src/main/java/com/google/devtools/build/lib/remote/REA
DME.md) and configured the simplest supported cache backend, an `nginx` server
with HTTP `PUT` support for storing new files. This is all handled by the same docker-compose setup that configures the Docker for the actual build (the code is [here](https://github.com/nicolov/bazel-benchmarks)).

The benchmark
-------------

The benchmark is the same as my [previous article](/benchmark-bazel-build-
cpp.html), and simulates a standard development workflow:

- do a fresh build of the project
- build again, without modifying any file (_no-op_ build)
- checkout a different commit, 2 weeks apart
- do an incremental build of this new commit
- revert to the original commit

The plot compares the running times for each of these steps, <font
color="blue">without</font> and <font color="green">with</font> remote caching
enabled:

<img src="{attach}results_with_cache.png"
     class="img-center"
     alt="Bazel remote caching benchmark"
     style="max-width: 500px"/>

Enabling remote caching has a slight negative effect on the first two builds,
since pushing the intermediate artifacts to the cache adds latency. However,
this means that the third build only takes ~ 20 seconds to complete (**50x
speedup**), since all the artifacts are already stored. For reference, the
total size of the cache is ~2.5GB, so the bandwidth requirements are
significant and the network may be a bottleneck during cached builds.

I have repeated the test using a fresh Docker container, and the cache is
indeed usable by different instances, as expected.

Conclusions
-----------

Simply pointing Bazel to an nginx server is enough to massively speed up
repeated builds of C++ projects. In real life, some additional setup would be
needed to keep che cache size bounded, and to make sure that build machines
have enough bandwidth to the cache server.
