Title: Visual robot navigation: using multiple markers
Date: 2016-05-20
Category: computer-vision robotics
Slug: visual-navigation-multiple-markers
Summary: We improve the visual navigation by tracking multiple markers at the same time
Status: draft

In the [previous article](/visual-navigation-following-camera.html), we have
extended the basic fiducial marker algorithm by tracking multiple camera poses
over time. While easy, that step wasn't really useful in isolation, since
losing track of the "origin" marker meant that we couldn't localize the robot
at all.

In this article, we're going to throw multiple markers in the mix, building a
real map of the environment that we can use for large scale navigation of the
robot. As long as the detections of new markers take place while any of the
old ones are still visible, we can grow the map without bounds and explore
arbitrarily large environments.

The *factor graph* for this new setup will look something like this:

<img src="{filename}/images/slam/fgraph_multicam.png" alt="Factor graph for multiple markers" class="img-center"/>

## The code

The additional code is very minimal: we now loop over all detected markers,
add guesses for any newly detected ones, and add a measurement factor for
each. As expected, each of the `MarkerFactor`s are connected to the same (i.e.
current) camera pose:

```cpp
for (auto const &tag : msg->tags) {
    gtsam::Symbol s_marker('M', tag.id);

    if (!estimate_.exists(s_marker)) {
        // It's the first time we see this new marker: add an estimate
        // based on the detector pose
        auto init_pose = estimate_.at<gtsam::Pose3>(s_ic) * gmsgs_pose_to_gtsam(tag.pose);
        estimate_.insert(s_marker, init_pose);
    }

    auto corners = tag_to_gtsam_points(tag);
    graph_.push_back(MarkerFactor(corners, pixel_noise_, s_ic, s_marker, K_, tag_size_));
}
```

We also have code to publish a "map" of the environment, consisting of all
detected marker poses together with their ids:

```cpp
TagMap map;

auto tag_filter = [](const gtsam::Key& k) {
    return (k >= gtsam::Symbol('M', 0)) && (k < gtsam::Symbol('N', 0));
};
for (const auto& kv : estimate_.filter(tag_filter)) {
    TagMapElement elem;
    // The tag id was stored as the index in the node's gtsam::Symbol
    gtsam::Symbol s(kv.key);
    elem.id = s.index();
    auto this_tag_pose = estimate_.at<gtsam::Pose3>(s);
    elem.pose = gtsam_pose_to_gmsgs(this_tag_pose);
    map.map.push_back(elem);
}
pub_map_.publish(map);
```

## The problem

We run the simulator and notice that, when markers enter or leave the frame,
the position and attitude estimates "jump". The next figure plots the camera Z
position over time:

<img src="{filename}/images/slam/z_all_1e2.png" alt="Camera trajectory without motion model" class="img-center" />

We conjecture that the optimization does not find enough frames with both old
and new markers to converge on the world pose of the latter ones. This means
that their appearance into the frame with incorrect world poses will cause the
estimate to spike away from the true value. The next section explores ways of
solving this problem.

## Adding a motion model

To improve the situation, we can leverage physical intuition about the
problem. Looking at the factor graph, we notice that the camera poses are not
connected through each other by any factor. This means that the optimization
engine has no correlation information between them. However, we know that in
real life, successive camera positions will be very close together, as the
robot moves with a limited velocity.

One easy way to introduce such prior information emulates the approach one
could use for wheel odometry. We add a factor with the following measurement
function:

```
f(pA, pB) = pA - pB - pBetween
```

where `pA` and `pB` are two successive camera poses, and `pBetween` is zero.
The minus sign is intended in the Lie algebra of SE3. In GTSAM, this
measurement function is included as a `BetweenFactor`.

The code addition is thus very simple:

```cpp
graph_.push_back(
    gtsam::BetweenFactor<gtsam::Pose3>(s_prev_ic,
                                       s_ic,
                                       gtsam::Pose3(),
                                       motion_noise_));
```

`motion_noise_` is the error between the real camera movement and the zero-
velocity model we have introduced. Very low values will constrain the movement
so much that the marker observation factors will have no effect on the
trajectory.

By plotting the same data we've shown before, we can confirm that the estimates
are now far less jumpy and more representative of the actual camera motion:

<img src="{filename}/images/slam/z_all_1e4.png" alt="Camera trajectory with zero-velocity motion model" class="img-center" />

## More sophisticated models

The current zero-velocity model is obviously very rough, and we're forced to
set a rather large error on the `BetweenFactor` to have reasonable defaults.
In the next article, we are going to switch to a more sophisticated model
(constant velocity), with an eye to using accelerometer and gyroscope data to
provide a more robust estimate (that can also be useful when no camera is
visible in the frame).
