#! /usr/bin/env python

# Python module imports.
from os import listdir, system
from os.path import basename, splitext
from re import search


# Loop over all files in the current directory.
for file_name in listdir('.'):
    # Only work with *.agr file.
    if not search('.agr$', file_name):
        continue

    # The file root.
    file_root, ext = splitext(file_name)
    file_root = basename(file_root)

    # Convert to EPS then PDF.
    system("grace -hdevice PostScript -hardcopy -printfile %s.ps %s" % (file_root, file_name))
    system("ps2eps %s.ps" % file_root)
    system("grace -hdevice PNG -hardcopy -printfile %s.png %s" % (file_root, file_name))
