#! /usr/bin/env python3
###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

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
