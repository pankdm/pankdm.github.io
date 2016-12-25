---
layout: post
title:  "Personal MacOS setup"
---

## Trackpad settings

System Preferences -> Trackpad

* Secondary click by right corner
* Enable `Tap to Click`
* Disable `Scroll Direction: Natural`

## Configs

`.ssh/config`

```bash
Host dev # alias name
    HostName <full host name>
    User <user name>
```

`.vimrc`

```bash
git clone https://github.com/pankdm/configs.git
ln -s configs/.vimrc ~/.vimrc
```

`.bash_profile`

```bash
export CLICOLOR=1 # enable colored `ls`
```


## Install brew

See [http://brew.sh/](http://brew.sh/)


## Install mosh

```
brew install mosh
```

## Install powerline

Reference:

* <https://powerline.readthedocs.io/en/latest/installation.html>
* <http://khanh-ng.blogspot.com/2015/02/install-powerline-for-mac-os-x.html>

```bash
pip install --user git+git://github.com/powerline/powerline

# find installed path
pip show powerline-status

# it will be something like
# /Users/${USER}/Library/Python/2.7/lib/python/site-packages
# pip installation is missing scripts so we need to copy them manually
POWERLINE_PATH=~/Library/Python/2.7/lib/python/site-packages/

git clone https://github.com/powerline/powerline.git
cp -r powerline/powerline/ $POWERLINE_PATH/powerline
cp -r powerline/scripts/ $POWERLINE_PATH/scripts

# create directory with configs
mkdir ~/.config/powerline
cp -r ./powerline/powerline/config_files/ .config/powerline/
```

Enable powerline for bash by adding the following line to `~/.bash_profile`:

```bash
POWERLINE_PATH=~/Library/Python/2.7/lib/python/site-packages/
source $POWERLINE_PATH/powerline/bindings/bash/powerline.sh
```
