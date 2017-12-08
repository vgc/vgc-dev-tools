In this folder, you can find useful files to configure/extend Qt Creator.

# VGC Header and Source File wizard

Installation:

1. Copy vgc_h_cpp into:

    ~/.config/QtProject/qtcreator/templates/wizards/

    (create the parent folders if they do not exist)

2. Restart Qt Creator

Usage:

1. In Qt Creator, open an existing file in the same directory of the
   files you want to create

2. Ctrl+N > VGC > Header and Source

3. Specify Library and Name. Example: "geometry" and "curve"

4."Next" > "Finish".

This will create the files geometry/curve.h and geometry/curve.cpp with
all the standard VGC boileplate.

# How to create new JSON-based Wizards?

Create a copy of an existing wizard (e.g., vgc_h_cpp), for example:
my_wizard/file.h
my_wizard/file.cpp
my_wizard/wizard.json

Modify as needed, then restart Qt Creator. You may want to run Qt Creator with
the -customwizard-verbose argument to output error message, useful for
debugguing when you create the wizard.

Things to modify in wizard.json:

- id: should be of the form "L.WizardName".
  The letter determines the order of appearance
  (A make it appear first).

- category: using "A.VGC" is recommended for all
  VGC-related wizards.

- trDescription: "Some description."

- trDisplayName: "Some Display Name + Source"

- trDisplayCategory: "VGC"

You can use the following as more complex example for inspiration:
<qt-installation>/Tools/QtCreator/share/qtcreator/templates/wizards/classes/cpp/

Inside the {JS: ... } tags, any Javascript code can be called! Very useful.
For example, in vgc_h_cpp/wizard.json, we use the "toUpperCase()" standard
Javascript function.

Qt has extended Javascript with its own functions, such as "preferredSuffix()", or
"classToHeaderGuard". See the following Qt Creator source file for more inspiration:

[corejsextensions.h](https://github.com/qt-creator/qt-creator/blob/35690ab66e3c79bf2ff69a2b996da0c2584ee13b/src/plugins/coreplugin/corejsextensions.h)
[cpptoolsjsextension.h](https://github.com/qt-creator/qt-creator/blob/19d4d7014d39a04965e40e1b8cf9de94fefb9bff/src/plugins/cpptools/cpptoolsjsextension.h)

More documentation:
http://doc.qt.io/qtcreator/creator-project-wizards.html
http://doc.qt.io/qtcreator/creator-project-wizards-json.html
