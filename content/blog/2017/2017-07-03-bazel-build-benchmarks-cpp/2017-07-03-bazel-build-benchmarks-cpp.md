Date: 2017-07-03
Slug: benchmark-bazel-build-cpp
Summary: Benchmarking the Bazel build system on real-life C++
Title: Benchmarking the Bazel build system on real-life C++
Tags: cpp bazel

**tldr;**: Bazel does a good job on local builds. Check out my [second article
](benchmark-bazel-build-cpp.html) for the juicy bits on remote caching.

[Bazel](http://bazel.build) is the open-source version of Google's internal
build system that is used to build their billions of lines of code. Google's
PR machine has been effective so far, and it seems that the project is picking
up steam. But how fast is it for real-life projects? I ran my own benchmarks
to find out.

Picking a project to benchmark
------------------------------

Large C++ projects have a tendency to build very slowly, due to unfortunate
language "features" and tooling that has never really outgrown design
constraints from the 70s.

I scoured GitHub for one such project with a Bazel build already set-up, and
came across [drake](https://github.com/RobotLocomotion/drake), a robotics
toolbox by MIT CSAIL. The migration from CMake to Bazel is actually underway
as I'm writing this, and you can follow its progress on [this GitHub
issue](https://github.com/RobotLocomotion/drake/issues/3129).

`cloc` reports a fair amount of C++ code, even without considering all the
third party dependencies that are downloaded from external repos (some of
which are quite substantial, like the Bullet physics library).

>
Language|files|blank|comment|code
:-------|-------:|-------:|-------:|-------:
C++|817|21778|18847|110883
C/C++ Header|544|12379|34730|42462
MATLAB|333|2327|3313|10292
CMake|104|1360|1819|7301
Python|70|993|1365|3387

Build time benchmarks
---------------------

I've prepared a Docker image and some Python scripts to time how long Bazel
takes to build the drake tree. While drake actually ships with a CMake build
too, any direct comparison would be biased since the set of targets between
the two differ quite a lot. The code is available on [my
GitHub](https://github.com/nicolov/bazel-benchmarks).

The `benchmarks.py` script is designed to simulate real-life development
workflows, and will run through the following steps:

- checkout the code
- do a fresh build of the drake project
- build again, without modifying any file (_no-op_ build)
- checkout a different commit
- do an incremental build of this new commit
- revert to the original commit
- build again

To approximate day-to-day changes to the codebase, I've picked two commits
roughly two weeks apart. `git diff` says that ~30k lines differ between the
two. Elapsed times for each of these steps look like this:

<img src="{attach}timings.png"
     class="img-center"
     alt="Bazel build system benchmark"
     style="max-width: 500px"/>

While the first build takes around 20 minutes, re-building after upgrading to
the newer commit only takes ~ 50% of that, confirming that dependency tracking
is doing *something* (but it's really hard to find out how much of this is to
Bazel's credit).

One thing I'm really excited about is that _no-op_ builds (i.e. when no file
is modified) are really fast: under 2 seconds for tens of thousands of C++
files. Such great performance can likely attributed to the Bazel daemon
running in the background and maintaining a cache to speed up dependency
checks.

Conclusions
-----------

Bazel seems to handle local builds just fine, and provides a good out-of-the
box experience where a single command downloads third party dependencies and
builds the project. However, this is something that many other build systems,
including CMake, can provide already. In this area, Bazel doesn't really serve
a compelling story, except for the arguably cleaner configuration format.

However, Bazel also supports **remote caching and execution**, where build
artifacts can be shared between multiple workstations to speed up builds, and
even built on a pool of workers instead. These neat features were born out of
Google's massive scale, and are enabled by Bazel's very strict approach to
build dependencies. Have a look at my [second article](on my blog) for more
information and benchmarks about them.
