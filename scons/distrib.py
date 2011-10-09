###############################################################################
#                                                                             #
# Copyright (C) 2006-2011 Edward d'Auvergne                                   #
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
from os import getcwd, path, sep, system, waitpid, walk
from re import search
from subprocess import PIPE, Popen
import sys
from tarfile import TarFile
from zipfile import ZipFile

# relax module imports.
from version import version


def gpg_sign(target, source, env):
    """Builder action for creating a GPG signature of the binary distribution file."""

    # Print out.
    print('')
    print("############################################")
    print("# GPG signing the binary distribution file #")
    print("############################################\n\n")

    # List of distribution files.
    type_list = [env['DIST_TYPE']]
    if type_list[0] == 'ALL':
        type_list = ['zip', 'tar']

    # GPG key.
    key = env['GPG_KEY']
    if key == None:
        sys.stderr.write("The GPG key needs to be supplied on the command line as key=xxxxx, where xxxxx is the name of your key.\n\n")
        return

    # Loop over the distribution files.
    for dist_type in type_list:
        # The file name.
        if dist_type == 'zip':
            file = env['DIST_FILE'] + '.zip'
        elif dist_type == 'tar':
            file = env['DIST_FILE'] + '.tar.bz2'
        elif dist_type == 'dmg':
            file = env['DIST_FILE'] + '.dmg'

        # Print out.
        print(("\n\nSigning the distribution package " + repr(file) + ".\n"))

        # Run the 'gpg' command.
        system("gpg --detach-sign --default-key " + key + " " + path.pardir + path.sep + file)

    # Final print out.
    print("\n\n\n")


def package(target, source, env):
    """Builder action for packaging the distribution archives."""

    # Print out.
    print('')
    print("#######################")
    print("# Packaging the files #")
    print("#######################")

    # List of distribution files.
    type_list = [env['DIST_TYPE']]
    if type_list[0] == 'ALL':
        type_list = ['zip', 'tar']

    # Loop over the distribution files.
    for dist_type in type_list:
        # The file name.
        if dist_type == 'zip':
            file = env['DIST_FILE'] + '.zip'
        elif dist_type == 'tar':
            file = env['DIST_FILE'] + '.tar.bz2'
        elif dist_type == 'dmg':
            file = env['DIST_FILE'] + '.dmg'

        # Print out.
        print(("\n\nCreating the package distribution " + repr(file) + ".\n"))

        # Create the special Mac OS X DMG file and then stop execution.
        if dist_type == 'dmg':
            # Create the Mac OS X universal application.
            print("\n# Creating the Mac OS X universal application.\n\n")
            cmd = 'python setup.py py2app'
            print("%s\n" % cmd)
            pipe = Popen(cmd, shell=True, stdin=PIPE, close_fds=False)
            waitpid(pipe.pid, 0)

            # Create the dmg image.
            print("\n\n# Creating the DMG image.\n\n")
            cmd = 'hdiutil create -fs HFS+ -volname "relax" -srcfolder dist/relax.app %s' % file
            print("%s\n" % cmd)
            pipe = Popen(cmd, shell=True, stdin=PIPE, close_fds=False)
            waitpid(pipe.pid, 0)

            # Stop executing.
            return

        # Open the Zip distribution file.
        if dist_type == 'zip':
            archive = ZipFile(path.pardir + path.sep + file, 'w', compression=8)

        # Open the Tar distribution file.
        elif dist_type == 'tar':
            if search('.bz2$', file):
                archive = TarFile.bz2open(path.pardir + path.sep + file, 'w')
            elif search('.gz$', file):
                archive = TarFile.gzopen(path.pardir + path.sep + file, 'w')
            else:
                archive = TarFile.open(path.pardir + path.sep + file, 'w')

        # Base directory.
        base = getcwd() + sep

        # Walk through the directories.
        for root, dirs, files in walk(getcwd()):
            # Skip the subversion directories.
            if search("\.svn", root):
                continue

            # Add the files in the current directory to the archive.
            for i in xrange(len(files)):
                # Skip any '.sconsign' files, hidden files, byte-compiled '*.pyc' files, or binary objects '.o', '.os', 'obj', 'lib', and 'exp'.
                if search("\.sconsign", files[i]) or search("^\.", files[i]) or search("\.pyc$", files[i]) or search("\.o$", files[i]) or search("\.os$", files[i]) or search("\.obj$", files[i]) or search("\.lib$", files[i]) or search("\.exp$", files[i]):
                    continue

                # Create the file name (without the base directory).
                name = path.join(root, files[i])
                name = name[len(base):]
                print(('relax-' + version + path.sep + name))

                # The archive file name.
                arcname = 'relax-' + version + path.sep + name

                # Zip archives.
                if dist_type == 'zip':
                    archive.write(filename=name, arcname=arcname)

                # Tar archives.
                if dist_type == 'tar':
                    archive.add(name=name, arcname=arcname)

        # Close the archive.
        archive.close()

    # Final print out.
    print("\n\n\n")
