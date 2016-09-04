Title: Robotics for developers 1/5: getting started
Date: 2016-07-28
Category: computer-vision robotics
Slug: robotics-for-developers/getting-started
Summary: This post is the introduction to a series on programming autonomous robots aimed at developers with no background in computer vision or robotics.

This post is the introduction to a series on **programming autonomous robots** aimed at developers with no background in computer vision or robotics.

I've noticed that drones, Arduinos, and virtual reality are raising awareness about the awesomeness of computers that interact with the physical world. On the other hand, roboticists definitely lag behind the web community when it comes to community building and marketing shiny things. There's a lot of great code to discover, but I feel that it doesn't get much love outside the academic circles.

This series is my attempt to share some of my knowledge while building up a visual navigation system, and refer readers to cool projects that could be used as plug-and-play components for more complex undertakings.

A look at the "full stack"
--------------------------

One of the most amazing parts of working on robotics is that the proverbial *full stack* really is *full!* A full collection of technologies, ranging from microcontrollers to CUDA GPUs enables more and more autonomous behaviors. Going from the bottom to the top of the stack, we have:

- *Actuator control*, i.e. sending precise impulses of electrical current to power the motors with the appropriate torque as requested by the higher layers [^actuator_control],

-  *Low-level control* systems to guarantee the physical stability of the platform. These systems run a fast (~200Hz) real-time control loop using high rate sensor data and very simple controller laws. An example of this is the attitude stabilization present on even the cheapest drones, that uses the gyroscope to stabilize pitch and roll of the vehicle.[^low_level_control]

- *Basic autonomous behaviors*, i.e. quick actions that don't need a lot of feedback from the environment. For example, taking off a drone or backing off after hitting a wall. Due to their simplicity, these behaviors can be scripted without the need for learning algorithms or statistical approaches.

- *Localization and place-awareness* required for long-term autonomous behavior and decision-making. There are dozens of navigation techniques, based on all kinds of sensors and tailored for different environments and precision/speed tradeoffs.

- *Fully autonomous behaviors* that use statistical techniques for path planning, complex interactions with an evolving environment, and an high level interface to the human user. For example, one solid objective would be autonomous inspection of an unknown building ([maybe maximizing exploration gain](https://github.com/ethz-asl/nbvplanner)).

## Next steps

The rest of the posts in this series will focus on the *localization* problem.

We're going to bring together all the software components needed to use a camera and Inertial Measurement Unit (IMU, think accelerometer in your phone) to provide the robot with decent location data. I'll make sure to leverage widely used platforms and patterns, drawing from both academia and research, so that this overview will give you a solid idea about the current state of the art.

I won't be diving in boring details such as package installation or network setup and will instead assume a good proficiency in software development on a linux environment. For practical reasons, we also won't talk about any specific hardware platform, but rather use recorded data sets provided by the community.

### Notes

[^actuator_control]: The most basic example would be converting a number from 0-100 to a modulated signal delivered through the [PWM hardware](https://www.arduino.cc/en/Tutorial/PWM) of a microcontroller. Additional power electronics will then use this signal to control power flowing from the battery.

[^low_level_control]: Most solutions eventually rely on some complex combination of a very simple idea, the proportional controller (PID). For a very cool state-of-the-art solution that uses GPUs to simulate physical behavior, [look here](http://spectrum.ieee.org/cars-that-think/transportation/self-driving/autonomous-mini-rally-car-teaches-itself-to-powerslide).
