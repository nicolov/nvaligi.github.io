Title: Practical, declarative authentication with Angular.JS and ui-router
Date: 2015-05-10
Tags: frontend, angularJS
Slug: pratical-authentication-angularjs-uirouter
Summary: I describe my favorite Angular.JS authentication pattern which is both simple and flexible, thanks to ui-router's built-in functionality. Say goodbye to boilerplate code in the controllers!

Authentication is one of the core elements of a Single Page Application, but this doesn't mean that all Angular sites implement it correctly. I've seen many examples of overly convoluted solutions that don't take advantage of the capabilities of `ui-router`. In this piece, I'll show how to use the `resolve`s and parent states to set up authentication requirements in a declarative way.

## Don't do this..

A solution I've seen bandied around is to handle the authentication in the controllers, like this:

    if (!$rootScope.isAuthenticated) {
        $state.go('login');
    }

While seemingly innoucous, this code causes the page to flicker for a moment while the browser is redirected. Besides, the snippet must be replicated in each controller, violating every DRY tenet known to man.

## or this..

A wise man once said that `ui-router` nested states are a powerful tool to organize your application's states. You could create a global *abstract* state and tag it to highlight the fact that it requires authentication.

    .state('private', {
      abstract: true,
      // ...
      data: {
        requireLogin: true
      }
    })

Then you go on and define all other states as children of `private`, so that they inherit the tag:

    .state('private.dashboard', {
        parent: 'private'
        // ...
    })

The missing piece is to intercept all route changes and check if the user is allowed to reach a specific state. If not, the browser is redirected to the login page instead.

    $rootScope.$on('$stateChangeStart', function (event, toState) {
        var requireLogin = toState.data.requireLogin;

        if (requireLogin && !$rootScope.currentUser) {
          event.preventDefault();
          $state.go('login');
        }
    });

This second solution is more refined than the first, as the interceptor prevents the controller from loading, thus getting rid of the flicker. It still isn't very elegant though, as the user model must be stored in some global state (here `$rootScope`) and I don't really like using interceptors when they're not needed.

## This is way better!

We finally come to the more elegant and flexible solution. I suggest using nested states in conjunction with another of `ui-router`'s powerful features, `resolve`. Using `resolve` unifies the authentication check with the server call, and provides a nice injectable for all controllers that need access to the user model.

When one or more promises are passed in the `resolve` property of a state, `ui-router` will wait for (*all of*) them to be resolved before carrying out the state change. Luckily for us, we can handle a failing promise and redirect to a the login state directly from the `resolve` function, like this:

    .state('private', {
        abstract: true,
        resolve: {
            profile: function(Profile, $log, $state) {
                return Profile.me().then(function(me) {
                    return me;
                }, function() {
                    $state.go('login', {redirect: $state.toState.name});
                });
            }
        }
    })

We now turn to the implementation of the `Profile` service, that contains the methods to authenticate the user and the user model itself. In this example, we expect the server to return an HTTP 401 error when accessing the `/profile` endpoint without proper authentication. In this case, the rejection of the promise will be passed along to the `resolve` function that will redirect the user to the login page.

This is a simple implementation of the factory with [https://github.com/platanus/angular-restmod](angular-restmod):

    angular
    .module('app')
    .factory('Profile') {
        return restmod.single('/profile').mix({
            $extend: {
                Model: {
                    me: function() {
                        var Profile = this;
                        return Profile.$search().$asPromise()
                    }
                }
            }
        });
    }

By using this pattern, the controllers of all the children states will have access to the `profile` injectable. As expected, the user won't be able to reach them until the server responds without errors to the `/profile` REST call.

## Conclusions

We have compared three different approaches to architect authentication in Angular. The third approach is cleaner and more strongly declarative thanks to `ui-router`'s features.

What's been missing in this discussion is a description of how to implement the login view and store the credentials obtained from the server. In the simplest case of cookie-based authentication, the browser would take care of these issues. In the more modern case of token-based auth, however, it's the developer's job to keep track of the tokens and send them to the server with each request.