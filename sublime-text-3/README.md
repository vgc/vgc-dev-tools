# Sublime Text 3

Here is a step-by-step guide to configure Sublime Text 3 for VGC development.
Personally, I use [Qt Creator](../qtcreator/README.md) for C++ and CMake files,
and Sublime for most other languages (Python, VGC files, Qt stylesheets, etc.).

Nearly all Sublime configuration is done via text files (JSON or Python) located
in your
[Data Directory](https://sublime-text-unofficial-documentation.readthedocs.io/en/latest/basic_concepts.html?highlight=config#the-data-directory):

- Windows: `%APPDATA%\Sublime Text 3`
- OS X: `~/Library/Application Support/Sublime Text 3`
- Linux: `~/.config/sublime-text-3`

The paths given in this guide are relative to the Data Directory. Also, this
folder follows the same hierarchy as the Data Directory, so you can just
copy-paste this whole folder into your Data Directory. However, you may already
have your own preferences that you don't want to override, so you may prefer to
copy-paste only what you need. alternatively, you can fork this git repository
and customize it to your liking, so that next time you can just copy-paste the
whole folder to set up Sublime exactly the way you like.

## Get Sublime

Sublime is not free, but well worth the money. Just go to the
[official website](https://www.sublimetext.com/) where you can buy a license or
download a trial version. The trial version is not limited either in time or
functionality: you just get a little popup once in while asking you nicely to
buy a license if you're actually using it regularly.

## Extend Sublime with Packages

If you haven't done it already, install
[Package Control](https://packagecontrol.io/installation). This is by far the
most convenient way to install Sublime packages, which are used to extend the
functionality of Sublime. Once Package Control is installed, restart Sublime,
then you can install any new package via Shift+Ctrl+P (or Shift+Command+P on
MacOS) > install package > Package Name.

Here are the packages that I recommend:

- Wrap Plus: Provides better line-wrap than the built-in line-wrap feature.

## Preferences

Go to Preferences > Settings. This opens side by side the default settings
(left pane), and your custom settings (right pane). Just copy-paste whichever settings
you like from
[Packages/User/Preferences.sublime-settings](Packages/User/Preferences.sublime-settings)
into the right pane.

## CSS Syntax Highlighting for *.qss Files

Copy-paste the file
[Packages/User/CSS.sublime-settings](Packages/User/CSS.sublime-settings) into
your Data Directory. This makes sure that *.qss files are treated as CSS files.

## Keymap

When I copy-paste code, I like it to be automatically re-indented in case the
source indentation level differs from the destination indentation level. This
can be done by assigning the "paste_and_indent" command to "ctrl+v", see
[Packages/User/Default (Linux).sublime-keymap](Packages/User/Default (Linux).sublime-keymap)
