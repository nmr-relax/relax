#! /usr/bin/python
# That line was just so programs like gvim or emacs will understand that this is Python code!  Don't
# make this file executable.

###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


# Import statements.
from os import F_OK, access, getcwd, path, remove, rmdir, sep, system, walk
from shutil import copytree
import sys

# UNIX only functions from the os module.
try:
    from os import lstat, symlink
except ImportError:
    pass


def install(target, source, env):
    """relax installation function (a Builder action)."""

    # Print out.
    ############

    print('')
    print("####################")
    print("# Installing relax #")
    print("####################\n\n")
    print(("Installing the program relax into the directory " + repr(env['RELAX_PATH']) + "\n\n"))


    # Tests.
    ########

    # Test that the installation path exists.
    if not access(env['INSTALL_PATH'], F_OK):
        sys.stderr.write("Cannot install relax, the installation path " + repr(env['INSTALL_PATH']) + " does not exist.\n\n")
        return

    # Test if the binary directory already exists.
    if not access(env['BIN_PATH'], F_OK):
        sys.stderr.write("Cannot install relax, the directory " + repr(env['BIN_PATH']) + " does not exist.\n\n")
        return

    # Test if the relax installation directory already exists.
    if access(env['RELAX_PATH'], F_OK):
        sys.stderr.write("Cannot install relax, the directory " + repr(env['RELAX_PATH']) + " already exists.\n\n")
        return

    # Test if the symlink exists.
    if env['SYMLINK_FLAG']:
        try:
            lstat(env['SYMLINK'])
        except OSError:
            # OK, symlink doesn't exist.
            pass
        else:
            sys.stderr.write("Cannot install relax, the file " + repr(env['SYMLINK']) + " already exists.\n\n")
            return


    # Install.
    ##########

    # Copy the files (and create the directory).
    try:
        print(("\nCopying all files in " + repr(getcwd()) + " to " + repr(env['RELAX_PATH']) + "."))
        copytree(getcwd(), env['RELAX_PATH'])
    except OSError, message:
        # Failure message.
        sys.stderr.write("Cannot install relax, " + message.__doc__ + "\n")

        # You don't have the privilages to do this.
        if message.errno == 13:
            sys.stderr.write("Permission denied, cannot create the directory " + repr(env['RELAX_PATH']) + ".\n\n")

        # All other errors (print normal python error message).
        else:
            sys.stderr.write("OSError: [Errno " + repr(message.errno) + "] " + message.strerror + ": " + repr(message.filename) + "\n\n")

        # Quit the function.
        return

    # Create the symbolic link.
    if env['SYMLINK_FLAG']:
        print(("\nCreating the symbolic link from " + repr(env['RELAX_PATH'] + sep + 'relax') + " to " + repr(env['SYMLINK']) + "."))
        symlink(env['RELAX_PATH'] + sep + 'relax', env['SYMLINK'])


    # Byte compile.
    ###############

    # Run relax to create the *.pyc files.
    print("\nCreating the byte-compiled *.pyc files.")
    python_path = sys.prefix + path.sep + 'bin' + path.sep + 'python' + `sys.version_info[0]` + '.' + `sys.version_info[1]`
    cmd = "cd %s; %s -m compileall . ; %s -O -m compileall ." % (env['RELAX_PATH'], python_path, python_path)
    print(cmd)
    system(cmd)

    # Final print out.
    print("\n\n\n")


def uninstall(target, source, env):
    """relax deinstallation function (a Builder action)."""

    # Print out.
    ############

    print('')
    print("######################")
    print("# Uninstalling relax #")
    print("######################\n\n")
    print(("Uninstalling the program relax from the directory " + repr(env['INSTALL_PATH']) + "\n\n"))


    # Tests.
    ########

    # Test that the installation path exists.
    if not access(env['INSTALL_PATH'], F_OK):
        sys.stderr.write("Cannot uninstall relax, the installation path " + repr(env['INSTALL_PATH']) + " does not exist.\n\n")
        return

    # Test if the binary directory already exists.
    if not access(env['BIN_PATH'], F_OK):
        sys.stderr.write("Cannot uninstall relax, the directory " + repr(env['BIN_PATH']) + " does not exist.\n\n")
        return

    # Test if the relax installation directory exists.
    if not access(env['RELAX_PATH'], F_OK):
        sys.stderr.write("Cannot uninstall relax, the directory " + repr(env['RELAX_PATH']) + " does not exist.\n\n")
        return

    # Test if the symlink exists.
    if env['SYMLINK_FLAG']:
        try:
            lstat(env['SYMLINK'])
        except OSError:
            sys.stderr.write("Cannot uninstall relax, the file " + repr(env['SYMLINK']) + " does not exist.\n\n")
            return


    # Uninstall.
    ############

    # Remove the symbolic link.
    if env['SYMLINK_FLAG']:
        print(("\nRemoving the symbolic link " + repr(env['SYMLINK']) + "."))
        remove(env['SYMLINK'])

    # Remove the directory.
    print(("\nRemoving the entire directory " + repr(env['RELAX_PATH']) + ".\n"))
    for root, dirs, files in walk(env['RELAX_PATH'], topdown=False):
        for file in files:
            remove(path.join(root, file))
        for file in dirs:
            rmdir(path.join(root, file))
    rmdir(env['RELAX_PATH'])

    # Final print out.
    print("\n\n\n")
