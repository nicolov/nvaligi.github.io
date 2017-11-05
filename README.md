Nico's personal page
====================

Source code for my [personal page](https://nicolovaligi.com).

Publish
-------

    make publish
    make github

Write
-----

    git submodule update --init --recursive

    sudo npm install -g browser-sync

    echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p

    make devserver

    make stopserver
