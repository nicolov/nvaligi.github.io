Title: Robotics for developers 4/6: tracking the robot over time
Date: 2016-07-31
Category: computer-vision robotics
Slug: robotics-for-developers/tracking-over-time
Summary: Extending the SLAM system to track multiple positions of the robot.

In the previous post, we have set up a probabilistic model to determine the relative position between the onboard camera and an artificial marker placed on the scene. So far, so good. However, this approach considers each frame independently, wihout any notion of continuous motion of the robot.

This simplification is actually surprisingly fine in our case, since fiducial markers can easily be tracked frame-by-frame without issues (that's why we picked them in the first place, after all). However, a real life system will use natural features that need to be tracked continously, and thus needs to somehow remember its history. In the next section, we're going to have a look at the two main ways of doing it.

## Adding more frames

The most intuitive way to incorporate knowledge of past states in the system is to extend the state each time a new image is captured. The factor graph we had at the end of the last post:

<img src="{filename}../2_architecture/fgraph_singlemarker.pdf" class="img-center" alt="Single marker factor graph" style="max-width: 320px"/>

after 2 more frames would look like this instead:

<img src="{attach}fgraph_multicam.pdf" class="img-center" alt="Factor graph with multiple cameras" style="max-width: 300px"/>

The state element for the marker pose doesn't need to be duplicated, since we assume that it stands still. However, we consider that each new frame corresponds to a new camera position and thus duplicate the corresponding state element accordingly.

Besides the added camera poses and corresponding marker observations, we had to add a whole new sets on factors (on the right in the graph above). These factors encode the our knowledge that successive camera positions will be rather close to each other (since the robot moves with a relative low velocity). GTSAM offers a `BetweenFactor` that can be used to constrain the relative pose between two state element. On a ground robot, we could have used data from the wheel sensors to correlate two camera states. In this case, however, we have no such information and will postulate the camera is standing still. Since this is obviously incorrect, we're going to adopt an appropriate noise model so that the optimizer places little faith in this prediction.

In a later post, we're going to replace this rough approximation with information from the accelerometer.

## Smoothing vs filtering

It's obvious how this approach doesn't scale well at all. Since the state elements need to form a square matrix, the space complexity immediately jumps to $O(N^2)$, which is bad enough in itself. What's more, the algorithms needed for actually solving the problem run in $O(N^3)$, making this naive approach untenable for real applications. Since we're not discarding any information, this **smoothing** approach is optimal and is proven to recover the MAP estimate as expected.

In the following, we're basically going to ignore these computational considerations and go ahead with dumb smoothing. However, it's important to mention a whole different approach: **filtering**. An example is the well-known *Kalman filter*, a much faster algorithm that only keeps around one copy of the camera pose at all times. While in the smoothing case, information is spread out over a bigger graph which is only sparsely connected, filtering results in a very small, densely connected graph. [^why_filter]

The simplifications involved in filtering have consequences in accuracy and stability, as a lot of information is thrown away at each step (at least in the general case). As to why I haven't decided to use a Kalman filter for this series, I personally find filtering less intuitive to understand and more of a black art to tweak.

## Implementation

I'll admit straight away that the "improvement" in the current post does nothing but slow down the system as the state grows bigger and bigger frame after frame. In theory, it should also be slightly more robust when handling degenerate geometric conditions, since informations from neighboring frames can be used to constrain the marker position a bitter. I have not observed much difference in practice though. [^ambiguity]

 However, these changes to the factor graph structure will be useful when observing multiple markers in the same image. That being said, the only implementation difference is the addition of some book-keeping code:

- we only add the prior belief to the marker position once, at the first frame,

- since we're constantly adding new pieces to the state, the optimizer needs initial guesses for these new values. The obvious thing to do here is to initialize newly added states with the MAP obtained at the last step.

## Running time

As anticipated, the performance is now pathetic, but we can live with that for now knowing that GTSAM also implements more efficient algorithms that can be used with a few lines of code.[^isam] I've done some equally pathetic benchmarking, but the trend is clear:

<div>
    <a href="https://plot.ly/~nikoperugia/13/" target="_blank" title="Solve time [s] vs Frame number" style="display: block; text-align: center;"><img src="https://plot.ly/~nikoperugia/13.png" alt="Solve time [s] vs Frame number" style="max-width: 100%;width: 600px;"  width="600" onerror="this.onerror=null;this.src='https://plot.ly/404.png';" /></a>
    <script data-plotly="nikoperugia:13"  src="https://plot.ly/embed.js" async></script>
</div>


## Next steps

Next time, we'll build upon the work done here and introduce support for multiple markers visible in the same frame. This will again involve extensions to the state as we observe new markers, but the additional effect on performance will be limited as the total number of possible markers is low.

### Notes

[^why_filter]: This [interesting paper](https://www.doc.ic.ac.uk/~ajd/Publications/strasdat_etal_ivc2012.pdf) analyzes this issue and depth and presents the case both for and against filtering. It's a good read, together with this [related one](https://www.doc.ic.ac.uk/~ajd/Publications/strasdat_etal_icra2010.pdf).

[^ambiguity]: Under some conditions, pose recovery from fiducial markers can suffer from ambiguities. This problem manifests itself during the optimization problem. Since there is a second minimum point close to the global minimum, the optimizer may snap back and forth between one and the other.

[^isam]: In the smoothing world, there are two main ways to reduce the computational load of larger maps. One is to exploit the sparsity of the problem matrix and use specific algorithms with time complexity lower than $N^3$. Instead, GTSAM takes a graph-based approach and identifies which partitions of the factor graph need to be re-evaluated upon each new sensor measurement. [iSAM2](http://frc.ri.cmu.edu/~kaess/pub/Kaess12ijrr.pdf) has significant computational advantages compared to the naive approach. Little or no modifications are needed to the problem definition to take advantage of this better solver.
