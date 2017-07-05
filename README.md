Nico's blog
===========

```
git submodule update --init --recursive

sudo npm install -g browser-sync

echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf && sudo sysctl -p

make devserver

make stopserver

make publish
make github
```