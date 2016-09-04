Title: Open source Visual SLAM evaluation
Date: 2016-09-01
Slug: open-source-visual-slam-evaluation
Summary: We compare a few open-source visual navigation systems on real-life data and discuss their pros and cons from a practical point of view.

Navigation is a critical component of just any autonomous system, and cameras are a wonderfully cheap way of addressing this need. From among the dozens of open-source packages shared by researchers worldwide, I've picked a few promising ones and benchmarked them against a **indoor drone** dataset. The results will be useful to hackers and DIYers that want to add localization capabilities to their drone or autonomous vehicle. All the code I used for running the tests, benchmarking, and plotting the results is available [on my Github](https://github.com/nicolov/vslam_evaluation).

## The contenders

There's a few fundamentally different approaches to visual-based localization, developed over decades of research. I've tried to pick the most useful representative of each family to paint a broad picture and help you decide which route to take.

- [*libviso2*](http://www.cvlibs.net/software/libviso/) is a crafty implementation of an old idea, *stereo odometry*. As such, it needs a pair of synchronized cameras and only computes camera movement through point-to-point correspondences between neighboring frames. This means that the computational load will stay roughly constant over time, as there's no need to build a map of the environment. As long as the scene has constrasty/pointy features, *viso2* will provide decent velocity data, but the estimated position will drift over time, as small errors accumulate over time.

- [*ORB-SLAM2*](https://github.com/raulmur/ORB_SLAM2) comes from a different family and is a state-of-the-art **SLAM** system. As the camera explores the scene, the software builds an extensive map of features that is used for tracking and *loop-closure* (recognizing previously visited areas of the map). SLAM systems are more precise and drift less than odometry approaches, but are generally more computationally expensive.

- [*Rovio*](https://github.com/ethz-asl/rovio) is somewhat of an hybrid between the two solutions above. I call it *short-term SLAM*, since its map is limited to the 20-30 most recent features. Most importantly, rovio is a *monocular* system and only needs a single camera to run, which is great. However, it relies on an IMU (accelerometer + gyroscope sensor) to provide the sense of scene scale that's missing from a single camera. In practice, this means you'll potentially have to add a $10 sensor to your robot.

## The evaluation

I've used the *EuRoC* dataset from ETHZ Zurich (available [here](http://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets)) since it has high-quality stereo images, the IMU data needed by rovio, and accurate ground truth from a laser system. These are 10-20m indoor trajectories recorded on a small drone.

While *viso2* and *rovio* already come with good ROS support, ORB-SLAM2 is a rather poor citizen of the ecosystem, so I wrote a new wrapper [here](). Some more work was required to make sure that the camera calibration was set correctly and that the reference frames were aligned among the different implementations. All the code you need to re-run the evaluation is [on Github](https://github.com/nicolov/vslam_evaluation).

## Accuracy results

The following plot compares the estimated trajectories against ground truth.

<iframe width="800" height="500" frameborder="0" scrolling="no" src="https://plot.ly/~nikoperugia/35.embed"></iframe>

The results are not surprising: ORB-SLAM is the most accurate, and tracks the actual trajectory amazingly well. Rovio is a close second, whereas the purely odometric *viso2* accumulates a substantial drift over time. I've also evaluated ORB-SLAM in its special *localization* mode that disables mapping of new features and thus works like odometry.

## Computational load

Of course, accuracy alone doesn't tell the whole picture, since most autonomous robots suffer from hardware limitations of some sort. None of these algorithms run on the GPU, so we're only looking at the CPU here. An highly-unscientific benchmark suggests the following running times for the four algorithms:

<iframe width="600" height="400" frameborder="0" scrolling="no" src="https://plot.ly/~nikoperugia/37.embed"></iframe>

*Rovio* is much faster than *viso2* here, probably because it only matches ~30 features per frame compared to ~200 for *viso2* (which also runs an expensive RANSAC check to detect outlier corrispondences). In any case, that's impressive for a monocular system that doesn't even benefit from multiple cameras.

Expectedly, ORB-SLAM is much slower than the other two, and only runs in real time thanks to multithreading. I would have assumed local mapping to make a bigger difference, but that didn't seem to be the case.

## Conclusion

If you don't need accurate mapping and loop closures, *Rovio* is an excellent performer. The slower (and less accurate) *Viso2* could be useful on computationally constrained platforms where adding a stereo camera is more convienent than setting up the IMU needed for Rovio. *ORB-SLAM* confirmed its good reputation for accuracy but may be too expensive to run on today's mobile platforms.