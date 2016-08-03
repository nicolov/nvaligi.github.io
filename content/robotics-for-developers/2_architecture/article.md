Title: Robotics for developers: architecting SLAM with ROS
Date: 2016-07-29
Category: computer-vision robotics
Slug: robotics-for-developers/architecture-with-ros
Summary: Introducing a mix of the computer science, physics, and computer vision that will be used for the project.

In the robotics community, the navigation problem we're building towards is commonly called **SLAM** (Simultaneous Localization and Mapping). SLAM refers to the task of building a map of an unknown environment while simultaneously localizing the robot position within it. In the case of visual-based SLAM, the map is a set of *landmarks*, recognizable features present on the scene that can be easily tracked as the robot moves.

SLAM is one of those pesky *chicken and egg problems*, since robot localization and map building go hand-in-hand: building a map needs an accurate position, but the localization itself needs a map. In the next post, we're going to see how taking a probabilistic approach helps solve this conundrum.[^slam]

A complete SLAM system is a pipeline with multiple stages:

- **Landmark extraction** consists in picking out significant features from the sensor data. In the case of cameras, you can imagine how identifying a black dot on a white wall could be a great feature that would be easy to use as landmark. In practice, this is done with computer vision tools called *feature extractors* that use local differences in image brightness to find interesting patches within an image.

- **Data association** means establishing correspondences between the same landmark observed in different camera frames, usually corresponding to multiple robot positions.

- **State estimation** combines the current landmark map with so-called *odometry* information from the robotic platform (for example wheel rotation for a ground robot) to update the estimate of *both* the map *and* the robot position. In the next few sections we'll see how this follows a fundamentally probabilistic approach.

While a general SLAM system is a rather complicated affair that must be tailored its application, our project will take a few shortcuts to make the core ideas clearer.

For starters, the extraction and association steps can be simplified by using man-made landmarks that can be tracked and identified easily and reliably. We're going to use **fiducial markers**, similar to the QR codes using for data sharing[^fiducial_slam]. The image below has an example of fiducial markers being used for robotics by Alphabet's Boston Dynamics:

![]({attach}boston_dynamics.jpg)

Their particular geometric shape takes care of the *extraction* problem (as it's easy to spot a black square with white borders in a natural scene), while the bits codified within the inner pattern make *landmark association* trivial.[^fiducials]

Thanks to the error correction built into the fiducial marker library, we can assume that extraction and association are 100% reliable. However, there's always going to be numerical errors in the exact position of the marker within the camera frame.

More generally, none of the sensor available for a robot could ever be perfect.
Cameras, lasers, GPS receivers, all suffer from uncertainties to a certain
degree. However, they still provide useful information that could and does help
localize the robot. To make sure that these uncertainties are handled
coherently, we formalize our localization problem in probabilistic terms, using
a **Bayesian approach**.[^bayes]

## The probabilistic approach

Two main factors make Bayesian probability very powerful within robotics:

- Any piece of information within the system is associated with a certain degree of *belief* in his true value, which is formalized as a **probability distribution**. Interpreting measurements as probabilities, rather than fixed values, is the magic sauce that allows for using multiple sources of information (for example, different kinds of sensors) in an optimal way.

- A powerful rule to *update* our beliefs over the world once new information is available from sensors. There are many good intuitive explanations of Bayes' rule around, so I won't repeat the core concept here. In the context of localization, Bayes rule allows us to recursively update our *prior beliefs* over the position of the robot, using the measurement from the camera.

In mathematical terms, we start by defining the *state* we want to estimate using sensor data. At this step of the project, we only care about the position of the camera and of the single marker. There's a lot of details involved in choosing appropriate representations for these physical quantities, but we'll defer them until they become interesting.

Now that we have a state and a rule to update it according to sensor
measurements, we can explicitly frame the localization problem as **Bayesian
inference**, i.e. finding the **posterior distribution** of the state
conditioned over all measurements from sensors.

While this may sound a bit too mathematical, we're going to adopt a great
software package that makes this kind of reasoning intuitive. I've decided to
use the GTSAM project from Georgia Tech due to its clean API and powerful
abstractions. In GTSAM, all the probabilistic information we have about the
system is encoded in a **factor graph**.[^fgraph] The figure below represents the factor
graph for the problem at hand:

<img src="{attach}fgraph_singlemarker.pdf" class="img-center" alt="Single marker factor graph" style="max-width: 400px"/>

The white circles represent the two pieces of the state: one for the marker pose
and one for the camera's. White circles are connected to black dots that encode
probabilistic information. We have two here. The one on the bottom represents
the information obtained from observing the marker in the image, and thus is
connected to both pieces of the state (since the position of the marker in the
image depends on both the camera and marker positions in the world).

The other black dot on the top left is only connected to the marker position. We
use it to encode our *prior knowledge* about the marker position in the world.
Prior knowledge is any information that we feed into the system before
considering the sensors. In this particular case, it's obvious that a marker
showing up in an image only tells us its *relative* position with respect to the
camera, and could not be used to distinguish if we're sitting in New York or in
Rome. That's why we add additional information (a **prior factor**) to solve this
ambiguity.

To recap:

- white circles are pieces of the *state*, the set of values we want to find out about the world (in our case the position of the camera and of the marker),
- since this information is unknown to us, we use a probability distribution to model its uncertainty,
- and use measurements from sensors (together with their own probability distributions) to update our estimate of the state,
- measurements are drawn as black dots connected to the pieces of the state they provide information about.

There's one missing piece to the puzzle: how to use Bayes' rule to merge all
these probability distributions and reach a consensus about what's the most
likely value for the state given all the measurements we have received. In
probability, this is called a **maximum a posteriori** (MAP) estimate. It turns
out that the factor graph can easily be converted to a *non-linear optimization
problem* that can be solved with a variety of techniques from the numerical
world. Solving for the minimum of this problem will yield the MAP estimate for the state: exactly what we were looking for!

During this "conversion" step, each factor (black dot) is interpreted as an
*error term* and added to the optimization. Obviously, the variables that appear
in the error term are the pieces of the state the factor is linked to in the
graph. Luckily, GTSAM takes care of this conversion for us and also has smart
heuristics to solve complex problems quicker than the dumb approach.


## Introduction to ROS

The most common framework for academic (and some industrial) robotic software development is the **Robot Operating System (ROS)**, an open-source project by the aptly-named Open Source Robotics Foundation (OSRF).

Just like web or desktop programming, a software framework makes your life easier by:

- offering proven patterns to kick-start new projects and mechanisms for code reuse,
- breeding a community that builds and shares code,
- providing facilities to reduce boilerplate and common headaches (looking at you, CMake)

In addition, ROS helps you integrate different software components potentially running on different hosts. This is done through a middleware for inter-process communication and serialization of strongly-typed messages (no JSON here..)

Beyond the plumbing, there's just an incredible amount of high-quality code that's been contributed over the years, ranging from sensor drivers, camera calibration, motion planning and control, to computer vision packages. Thanks to the common tooling and middleware, integrating most of these projects is a simple matter of writing short C++ or Python glue scripts.

## Architecture

The independent unit of computation in ROS is called a *node*, which is usually mapped to an OS process. Nodes communicate using TCP-based message passing orchestrated by out-of-band negotiations over XML-RPC. In pratice, we won't worry about these details, as they're taken care of by the *ROS client library*.

ROS client libraries abstract message-passing by introducing `Publisher` and `Subscriber` objects with convenient APIs. Messages are exchanged over a specific *topic*, such as `/camera/image`. All these conventions make it easy (and necessary) to decompose the project in a bunch of communicating processes.[^ros]

In the case of our project (at least in its initial iteration), the architecture will look like this:

<img src="{attach}architecture.pdf" class="img-center" style="max-width: 500px" />

When following these patterns, it's easy to swap the camera driver or the localization algorithm, and even run them on different machines (it's pretty common to run the drivers on the onboard computer, but use a stationary workhorse for the more intensive tasks). [^ros_arch]

## Next steps

In the next post, we are finally going to start laying down some code after introducing the computer vision principles behind visual navigation.

### Notes

[^slam]: There's plenty of more mathematically-oriented introductions to SLAM. I like [this](https://people.eecs.berkeley.edu/~pabbeel/cs287-fa09/readings/Durrant-Whyte_Bailey_SLAM-tutorial-I.pdf), [this](http://www.roboticsschool.ethz.ch/sfly-summerschool/programme/5.2-Chli-SLAM.pdf), and [this](https://github.com/correll/Introduction-to-Autonomous-Robots).

[^fiducial_slam]: In the next post, we will use datasets from [this project](https://bitbucket.org/adrlab/rcars/wiki/Home) that solves the same problem. The creators of the ArUco fiducial marker library have created [this](http://www.uco.es/investiga/grupos/ava/node/57) as an alternative that doesn't use SLAM techniques.

[^fiducials]: There are many implementations of fiducial markers. While the basic shape is mostly the same, there's been a lot of work in making the detection and extraction of data more reliable. We'll be using [this](https://april.eecs.umich.edu/wiki/AprilTags) type of marker.

[^ros]: Documentation for ROS is generally very good, especially the parts about the core packages. The core tutorial you want to go through to understand this is [here](http://wiki.ros.org/ROS/Tutorials/WritingPublisherSubscriber(c%2B%2B)).

[^ros_arch]: Communication between nodes happens through either TCP or UDP, but plugins for serial communication are also available.

[^bayes]: Most uses of probability in robotics take the Bayesian interpretation, as opposed to the frequentist. [This book](https://www.amazon.com/Probabilistic-Robotics-Intelligent-Autonomous-Agents/dp/0262201623) expands the localization subject with constant references to probabilistic concepts.

[^fgraph]: A more formal introduction to factor graphs is available in the [GTSAM tutorial](https://research.cc.gatech.edu/borg/sites/edu.borg/files/downloads/gtsam.pdf) and its [documentation](https://bitbucket.org/gtborg/gtsam/raw/25bf277cde12211d1c553b3fc6e59b3f942c79de/doc/math.pdf).
