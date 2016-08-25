Title: Tutorial on robotics for developers

I've written a project-based tutorial to introduce other developers to the exciting world of robotics software. By the end of it, you'll have created a fairly complete SLAM system that uses cameras and IMUs for localizing a robot.

The project is built using some of the most common technologies, including ROS and OpenCV and requires some proficiency in C++ programming and Linux. I've assumed no previous knowledge in computer vision or robotics, though.

If you want to have a look before starting to read, the source code is available [on GitHub](https://github.com/nicolov/robotics_for_developers).

The [getting started post]({filename}/robotics-for-developers/1_getting_started/article.md) talks about the different software components in a robotic system and introduces the objective of the project.

The [architecture post]({filename}/robotics-for-developers/2_architecture/article.md) discusses the different parts of a SLAM (localization) system and how to connect them together with ROS.

The [camera post]({filename}/robotics-for-developers/3_camera/article.md) lays down some basic concepts of Computer Vision and non-linear optimization needed to find the camera position when observing a fiducial marker like this one:

<img src="{filename}/robotics-for-developers/3_camera/frame_example.jpg" style="width: 400px" class="img-center" />

The [next post]({filename}/robotics-for-developers/4_time_evolutions/article.md) talks about some ideas in filtering and estimation theory as a prelude to tracking the camera position as it evolves over time.

We proceed by [adding a map]({filename}/robotics-for-developers/5_multiple_markers/article.md) to operate on larger environments and fully realize the promise of SLAM.

<!-- [finishing touch]({filename}/robotics-for-developers/6_imu/article.md) -->

The [final article]({filename}/robotics-for-developers/6_imu/article.md) adds accelerometer and gyroscope data to make the localization more robust when there's little or no information from cameras.
