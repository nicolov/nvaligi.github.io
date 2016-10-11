Title: Reading list for Udacity self-driving car challenge #3
Date: 2016-10-12
Slug: reading-list-udacity-self-driving-challenge-3

As part of their [open-source self driving car](https://www.udacity.com/self-driving-car) project, Udacity has been releasing a series of challenges to encourage community participation. [Challenge #3](https://medium.com/udacity/challenge-3-image-based-localization-5d9cadcff9e7) seems interesting and fits right into a lot of current research in Deep Learning I was reading about.

### The challenge

> You will need to build a pipeline that can take a frame from our dashboard camera, process it, and compare it to a database of previous drives.

Given that testing will happen on individual frames, not on a sequence, conventional SLAM approaches will be of limited use. Instead, we'll have to focus on the **relocalization** and **place recognition** tasks. In literature, this is sometimes called the **kidnapped robot** problem.

I think it's most natural to lean towards a Deep Learning solution, since so many other perception subsystems already rely on it. However, I've also included a few references to *conventional* approaches with hand-crafted visual features and algorithms.

### Deep learning approaches

This is a list of **deep learning** based approaches, ordered by increasing sophistication:

<hr>

*Chen, Z., Lam, O., Jacobson, A., & Milford, M. (2013). Convolutional Neural Network-based Place Recognition*

This is the first attempt at using CNN-based features for place recognition, based on a pretrained Overfeat network. Unfortunately, the authors only evaluate a complete system that includes sequence matching and spatial consistency heuristics. It's thus hard to gauge just how well this specific network performs.

<hr>

*Sünderhauf, N., Shirazi, S., Dayoub, F., Upcroft, B., & Milford, M. (2015). On the performance of ConvNet features for place recognition*

This paper tackles the same problem and offers several interesting improvements:

- clean separation between feature extraction and matching;

- comparison of different ConvNets (AlexNet trained for either object recognition and on the *Places* dataset)

- different datasets with good mix of appearance changes (winter/summer), viewpoint changes, and both.

- algorithms that allow real-time operation by leveraging higher-level representations in ConvNets.

<hr>

*Niko, S., Shirazi, S., Jacobson, A., Dayoub, F., Pepperell, E., Upcroft, B., & Milford, M. (2015). Place Recognition with ConvNet Landmarks: Viewpoint-Robust, Condition-Robust, Training-Free.*

The key insight here is to couple CNN-based feature descriptors with a landmark extraction module that selects regions of the image that are most likely good landmarks. By using landmark regions instead of the full image, the system gains in robustness against view point changes. As described here, the pipeline is really slow since CNN inference runs once for each of the extracted landmarks (50-100/image). Also, this approach still has no notion of *metricity* (i.e. it only looks at similarity in the image space, not in the real world).

<hr>

*Kendall, A., Grimes, M., & Cipolla, R. (2015). PoseNet: A Convolutional Network for Real-Time 6-DOF Camera Relocalization*

This is the first **regressor** for the camera pose, as opposed to the relocalization approaches described above. Again, it heavily leans on transfer learning and leverages a pre-trained GoogLeNet for scene descriptors. Compared to conventional SLAM, this approach does not need a growing landmark map, but embeds knowledge within the trained network. Compared to previous DL works, it outputs a continuous pose rather than a choice between existing viewpoints.

The authors also present an interesting analysis of learnt features and note how the network even learns to infer knowledge from largely textureless regions that are not used in conventional descriptor-based SLAM.

### "Conventional" approaches

Here, I list non-DL approaches with open-source implementations. The body of research is much larger, but also more consolidated and mature.

<hr>

*Cummins, M., & Newman, P. (2008). FAB-MAP: Probabilistic Localization and Mapping in the Space of Appearance.*

This paper leverages a [bag of words](http://nicolovaligi.com/bag-of-words-loop-closure-visual-slam.html) representation and Bayesian techniques to solve place recognition. This approach is commonly used as a benchmark (including in some of the papers above), and there are open-source implementations available.

<hr>

*Mur-Artal, R., Montiel, J. M. M., & Tardos, J. D. (2015). ORB-SLAM: A Versatile and Accurate Monocular SLAM System*

ORB-SLAM is an open-source SLAM system that is very competitive in large-scale scenarios. Its *kidnapped robot* module is based on ORB (binary) features and a bag-of-words approach for whole-image description.

<hr>

*Shotton, J., Glocker, B., Zach, C., Izadi, S., Criminisi, A., & Fitzgibbon, A. (2013). Scene coordinate regression forests for camera relocalization in RGB-D images.*

This is probably the state of the art in non-DL relocalization techniques. Unlike most other approaches, it doesn't use local feature descriptors, but learns a probability didstribution for each pixel. Unfortunately, it scales poorly with workspace size and needs depth information that is usually not available in outdoor scenes.
