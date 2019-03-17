Date: 2019-03-17
Slug: occupancy-mapping-benchmarks
Summary: Benchmarking Occupancy Mapping libraries
Title: Benchmarking Occupancy Mapping libraries
Tags: robotics, navigation

This article looks at the performance of three different 3D Occupancy Mapping
libraries for Robotics. You can find the code on [my
GitHub](https://github.com/nicolov/occupancy_mapping_benchmarks), together
with a CI configuration that builds and runs the tests in the cloud.

<img src="{attach}occupancy_map_structure.png" style="max-width: 80%"
class="img-center" />

Robots that navigate in unknown environments need to figure out where obstacles
are. Perhaps the most common way to do this is with **Occupancy Maps**, where
the environment is discretized in a grid with fixed resolution (say, 0.05
meters). As the robot moves around, each _voxel_ is marked as occupied or free
based on sensor measurements. In most applications, the belief of the state of
each voxel is updated probabilistically by integrating sensor data, be it LIDAR
or RGBD cameras. In this article, we're not going to focus on how to implement
this probabilistic model, but only on the *data structures* that can be used to
efficiently store the occupancy map.

## The requirements

The most basic requirement for a grid data structure is to be able to set,
store, and retrieve data that is linked to a specific position $(x, y, z)$ in
the world frame. This is easy enough to implement by storing values in a 3D
array with the desired voxel size (depending on the precision required in the
application). However, typical values for the voxel size (0.05 to 0.2 meters)
require insane amounts of memory. Luckily, it just so happens that most of the
space in the environment is free, so we can be a bit smarter and avoid wasting
any memory on it. One way or another, all three of the libraries considered in
this article take advantage of this.

In most situations, the size of the environment is not known at the beginning of
the mission. Data structures should allow inserting data at arbitrary positions,
without the need for resizing or costly copies of data. This requirement might
seem trivial, but it's easy to see how it's not satisfied by the fixed-size 3D
array introduced in the previous sections (reallocations and copies would be
needed to increase the size of the map).

From the point of view of computation costs, there are two main use cases we
want to consider:

- during mapping, the occupancy grid must be updated according to incoming
  sensor measurements. Both LIDARs and RGBD cameras measure the distance of a
  world point P from the sensor. A trivial model would assume that all world
  points on the line from the sensor center all the way to the P should be
  marked as free. Likewise, P should be marked as occupied. In the real world,
  measurements are affected by error and noise, which are usually tackled with a
  probabilistic model (usually a Binary Bayes filter in log odds form for
  convenience). In this article, we're not really concerned with this
  probabilistic models, since they can be applied to all data structures. We're
  just going to be simulating sensor updates by associating a floating point
  value with each voxel.

- during planning, the map is queried to avoid obstacles and find free space
  where the planner can direct the robot. While query patterns vary depending on
  the chosen planning algorithm, a typical request might be to find all occupied
  voxels within a certain distance of the robot.

## The contestants

I've written code to compare the performance of three open-source libraries that
implement datastructures for occupancy mapping:

- [OctoMap](https://octomap.github.io/)
- [SkiMap](https://github.com/m4nh/skimap_ros)
- [OpenVDB](https://www.openvdb.org/)

Since all three libraries satisfy the common requirements introduced in the
previous section, we're just going to describe why they are unique.

**OctoMap** is a very commonly used library whose paper dates back to 2010. It
pretty much is a textbook application of *octrees*, a hierarchical tree-based
structure where 3D space is recursively divided in smaller portions. Since
recursion can be stopped when the required voxel size is reached, the complexity
of the look-up is bounded to constant-time. By taking advantage of the tree
structure, mapping free space takes up less memory. Since the library is tailored to
Robotics applications, it's really easy to integrate into an existing stack.

**SkiMap** is another Robotics-focused library with the explicit aim of being a
faster alternative to OctoMap. Instead of octotrees, it uses *skiplists*, a
fancy datastructure that combines some of the advantages of linked list
(constant-time insertion at any point of the list) with those of arrays
(constant-time next-element lookup) and hash tables (constant-time lookups of
arbitrary elements).

**OpenVDB** is the only library here that has won an Academy Award! It hails
from the Computer Graphics world, where it's used to store and manipulate the
large amount of particles that are used when rendering animated movies. Even if
it's not widely used in Robotics, its core value proposition is ideal for
occupancy mapping: *"a hierarchical data structure and a suite of tools for the
efficient manipulation of sparse, possibly time-varying, volumetric data
discretized on a three-dimensional grid.* I found [this Youtube
video](https://www.youtube.com/watch?v=7hUH92xwODg) to be a good resource in
understanding what makes the underlying data structure so unique.

## Results

While the same concepts apply to both (3D) LIDAR mapping and RGBD dataset, I'm
more interested in the latter and decided to use data from the well-known [TUM
RGBD dataset](https://vision.in.tum.de/data/datasets/rgbd-dataset). Images are
recorded with a Microsoft Kinect sensor (active infrared with a 640x480
resolution). Luckily, the data already comes with ground trajectories, so we can
focus on the mapping aspect of SLAM, without having to worry about localization.

I wrote [some simple
code](https://github.com/nicolov/occupancy_mapping_benchmarks) to simulate
inserting the point clouds into the occupancy map, using the same settings for
all three libraries. The measurement model is really simple: each $(x, y, z)$
point is first transformed from the camera frame into the world frame (using the
ground-truth trajectory in the dataset), and marked as occupied in the occupancy
map. As mentioned earlier, in the real world you would probably want to adopt a
probabilistic measurement model to account for noise. For this dataset, even
this primitive approach works fine, as the underlying data is pretty clean. We
can use OctoMap's visualization tool, `octovis` to visualize the resulting map:

<img src="{attach}occupancy_map.png" style="max-width: 80%"
class="img-center" />

If you squint hard enough, you can see the desk in the center of the room. This
map was generated from the
`rgbd_dataset_freiburg3_long_office_household-2hz-with-pointclouds.bag` file (available [here](https://vision.in.tum.de/data/datasets/rgbd-dataset/download#freiburg3_long_office_household),
which contains 165 depth images recorded over 85 seconds. `octovis` also allows us to choose which octotree level to render. For example,
we can look at larger voxels:

<img src="{attach}occupancy_map_lowres.png" style="max-width: 80%"
class="img-center" />

As expected, the result is the same for all three libraries. More interestingly,
here are the running times:

<img src="{attach}plot.png" style="max-width: 80%"
class="img-center" />

Or in table form:

| Library   |   Runtime [sec] |
|:----------|----------------:|
| SkiMap    |         4.42933 |
| OctoMap   |         3.9841  |
| OpenVDB   |         2.25164 |

## Conclusion

OpenVDB does live up to its promise of being well optimized, clocking almost
twice as fast as OctoMap. SkiMap is somewhat competitive with OctoMap, while
being less mature and a significantly simpler implementation. In a follow-up
article, I'll add new benchmarks to test some common query patterns that would
be useful for planning trajectories in the generated occupancy map.
