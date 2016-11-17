Title: Using (React) Bootstrap components in Reagent
Date: 2015-09-26
Slug: boostrap-components-reagent-clojurescript
Summary: A quick note on how to wrap React to easily add Bootstrap components to a Reagent/Clojurescript web application
Tags: frontend, clojurescript, react

## ClojureScript and Reagent

ClojureScript builds on the solid foundations of Clojure to make frontend web development straightforward and fun. Besides, functional concepts in CLJS are a very good match for React's vision of components and immutability.

If you want to use React as a view layer in ClojureScript, you will need either of two projects: OM and Reagent. While OM seems to be the better known of the two (among the others, used by CircleCI for their web-app), its API retains much of React's verbosity. For a more elaborate comparison, take a look [here](http://theatticlight.net/posts/Om-and-Reagent/). All things considered, I like **Reagent** better and decided it warranted some experimentation time.

## The problem

These days, Bootstrap components are the bread and butter of rapid web prototyping, and life's hard without them, even in Reagent. Unfortunately, while OM has its [own library](https://github.com/racehub/om-bootstrap) of components, no such convenience exists for Reagent.

On the other hand, we can easily wrap the [react-bootstrap](https://react-bootstrap.github.io/) project and have access to all the goodies.

## Using Bootstrap components

First, we add the CLJSJS dependency to the project. I'm using Leiningen, so it's just a matter of editing the `project.clj` file:

    (defproject demo-proj "0.1.0"
      :dependencies [[org.clojure/clojure "1.6.0"]
                     [org.clojure/clojurescript "0.0-3211"]
                     [reagent "0.5.0"]
                     [cljsjs/react-bootstrap "0.25.1-0"]]
      ...)

Going to the views files, we require the React Bootstrap namespace:

    (ns demo-project.views
        (:require [reagent.core :as reagent]
                  [cljsjs.react-bootstrap]))

We then use the magic `adapt-react-class` method ([reference](https://reagent-project.github.io/news/news050.html)) to convert a React component to a Reagent-flavoured one that can be used directly:

    (def Button (reagent/adapt-react-class (aget js/ReactBootstrap "Button")))

The `Button` component is now ready to use within the Hiccup templates:

    [:div
      [:h2 "A sample title"]
      [Button "with a button"]]

## Wrapping up
We have seen how to take advantage of the vast amount of community-contributed React components and use them whithin a Reagent application without much effort.