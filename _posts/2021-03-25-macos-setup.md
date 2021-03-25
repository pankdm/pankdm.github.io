---
layout: post
title:  "Personal MacOS setup"
---

## Trackpad settings

`System Preferences -> Trackpad`:

* `Secondary click`: click in bottom right corner
* Enable `Tap to Click`
* Disable `Scroll Direction: Natural`

## Keyboard settings

`System Preferences -> Keyboard`:

* Maximum `Key Repeat`
* Maximum `Delay Until Repeat`
* Enable `Use F1, F2, etc as standard`


## CapsLock to switch languages

**After High Sierra:**

* `System Preferences -> Keyboard -> Input Sources`:
  * Enable `Use the CapsLock key to switch`

**Before High Sierra:**


Reference: [stackoverflow](http://apple.stackexchange.com/questions/256342/use-caps-lock-to-switch-to-and-from-languages-on-sierra)


1. Install Karabiner-elements: <https://github.com/tekezo/Karabiner-Elements>
2. Remap CapsLock to f19
3. `System Preferences -> Keyboard -> Key modifiers`: disable CapsLock
4. `System Preferences -> Keyboard -> Shortcuts -> Input Sources`:
press CapsLock to change languages


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

`.gitconfig`

```
git clone https://github.com/pankdm/configs.git
ln -s configs/.gitconfig ~/.gitconfig
```

`.bash_profile`

```bash
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi
```

To avoid confusion, consolidate everything in `.bashrc`.

* Reference: <https://apple.stackexchange.com/questions/51036/what-is-the-difference-between-bash-profile-and-bashrc>


`.bashrc`

```bash
export CLICOLOR=1 # enable colored `ls`
```


## Install brew

See <http://brew.sh>


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
mkdir -p ~/.config/powerline
cp -r ./powerline/powerline/config_files/ .config/powerline/
```

Enable powerline for bash by adding the following line to `~/.bashrc`:

```bash
POWERLINE_PATH=~/Library/Python/2.7/lib/python/site-packages/
source $POWERLINE_PATH/powerline/bindings/bash/powerline.sh
```

Customize powerline config. In `.config/powerline/config.json` switch to `default_leftonly` theme.
Then in `.config/powerline/themes/shell/default_leftonly.json` add time field:

```json
{
  "function": "powerline.segments.common.time.date",
  "args": {
    "istime": true,
    "format": "%X"
  }
},
```


Finally, install special symbols as fallback font. Reference:

* <https://powerline.readthedocs.io/en/latest/installation.html#fonts-installation>
* <https://gitlab.com/zerustech/font-fallbacks-tutorial>

## pankdm.github.io

Install jekyll and dependencies

```bash
gem install bundler jekyll redcarpet pygments.rb
```


## VSCode

* Multi-tab rows

```json
"workbench.editor.wrapTabs": true
```

**Before [1.53 version update](https://github.com/Microsoft/vscode/issues/70413#issuecomment-753870712):**


Install [Custom CSS Extension](https://marketplace.visualstudio.com/items?itemName=be5invis.vscode-custom-css)

Then reload the app:

```bash
sudo chown -R $(whoami) "/Applications/Visual Studio Code.app/Contents/MacOS/Electron"
```

Then `Cmd + Shift + P` -> `Reload Custom CSS` -> `Restart`


* Switch tabs with cmd-number:


```json
{ "key": "cmd+1","command": "workbench.action.openEditorAtIndex1" },
{ "key": "cmd+2","command": "workbench.action.openEditorAtIndex2" },
{ "key": "cmd+3","command": "workbench.action.openEditorAtIndex3" },
{ "key": "cmd+4","command": "workbench.action.openEditorAtIndex4" },
{ "key": "cmd+5","command": "workbench.action.openEditorAtIndex5" },
{ "key": "cmd+6","command": "workbench.action.openEditorAtIndex6" },
{ "key": "cmd+7","command": "workbench.action.openEditorAtIndex7" },
{ "key": "cmd+8","command": "workbench.action.openEditorAtIndex8" },
{ "key": "cmd+9","command": "workbench.action.openEditorAtIndex9" }
```

<https://stackoverflow.com/questions/39245966/vs-code-possible-to-switch-tabs-files-with-cmdnumbers>

## Iterm

Set keymaps:
 * `Cmd + Option + Left` -> Next Tab
 * `Cmd + Option + Right` -> Previous Tab
