Nico's personal page
====================

Source code for my [personal page](https://nicolovaligi.com).

Publish
-------

    make publish
    make github

Write
-----

    sudo npm install -g browser-sync

    echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p

    pipenv install
    pipenv shell

    make devserver

    make stopserver

    make github

System setup
------------

	brew install node ghostscript imagemagick@6 freetype
	ln -s /usr/local/Cellar/imagemagick@6/6.9.9-31/lib/libMagickWand-6.Q16.dylib /usr/local/lib/libMagickWand.dylib
	npm install -g browser-sync
