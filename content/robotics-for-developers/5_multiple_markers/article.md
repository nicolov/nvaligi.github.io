Title: Robotics for developers 5/5: exploring a bigger world
Date: 2016-08-01
Category: computer-vision robotics
Slug: robotics-for-developers/exploring-bigger-world
Summary: Recognizing multiple markers makes the SLAM system more useful in larger environments.

In this post, we're going to finally realize the promise of SLAM and incrementally build a map of the environment. Until now, we have been bound to a single marker, so there wasn't much in the way of a map to talk about.

It turns out that the SLAM system with a map is great at exploring large environments, since the structure of the factor graph allows for on-line estimation of the relative pose between all markers. Even a single frame with two visible markers allows the optimizer to "learn" their relative pose, so that either can be used for localization. Any special role for the origin marker disappears, as any other marker can be used equally well for localization.

## Extending the state and the factor graph

Since the marker detector already identifies each marker using its inner bits, we can trivially extend the state whenever we observe a new marker. While looping over all detected markers, we also make sure to link the `MarkerFactor` to the correct marker state. The factor graph ends up looking something like this:

<img src="{attach}fgraph_multimarker.pdf" class="img-center" alt="Factor graph with multiple cameras" style="max-width: 400px"/>

In the example above, the camera only observes *marker 1* in the first frame, but both *marker 1* and *marker 2* in the second frame. The third and fourth images only see *marker 2*.

At this stage, the backend SLAM optimizer could be used for "real" visual SLAM by replacing the fiducial marker frontend with one based on natural image edges and features. In this case, one tricky issue would be handling **outliers**: mismatched associations between points that create bad edges in the factor graph and can cause the optimizer to fail.

## Missing markers

As introduced earlier, the marker map allows the SLAM system to continue to operate when the original marker disappears from the scene, as long as other markers are visible. The figure below plots the estimated camera position and compares the output from the marker detector and the one from the SLAM system. The little bars at the bottom are a reference to see which of the markers are visible.

<iframe width="600" height="500" frameborder="0" scrolling="no" src="https://plot.ly/~nikoperugia/15.embed"></iframe>

For the first few seconds, only *marker 1* is available, then *marker 2* also appears. The interesting part is around second 11.5, where *marker 1* exits the frame, but we can keep tracking using *marker 2*. The plain detector, on the other hand, expectedly bails out and doesn't output any data.

## Map-building performance

Let's have a look at how the optimizer "learns" the map, i.e. the relative poses between the markers. The following plot shows how the estimated relative $x$ position between *marker 1* and *marker 2* changes over time:

<iframe width="600" height="500" frameborder="0" scrolling="no" src="https://plot.ly/~nikoperugia/17.embed"></iframe>

Again, the bars at the bottom help us track when the markers are visible or not. Obviously, there's no data until we observe *marker 2* for the first time, around second 10. As more frames are captured, the estimate converges to around $0.5cm$ compared to the initial starting value of $1.5cm$. The actual value is probably very close to $0$, since the two markers are glued to the same table.

It's easy to explain the few bumps in the plot: during those periods only one of the markers was visible, and very little information was thus available for the optimizer to refine its estimate.

## Next steps

The complete SLAM system performs pretty well and quickly converges to a good estimate of the map. Before you get your hopes too high, remember that this is a simplified case using artificial markers. A real life system would use natural features or laser scan points, which are much messier and prone to failure.

Before concluding the series, we'll add support for accelerometer data, that will allow the system to operate even *without any marker*, even though just for a brief period of time.
