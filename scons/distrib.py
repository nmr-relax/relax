###############################################################################
#                                                                             #
# Copyright (C) 2006-2008,2011,2019 Edward d'Auvergne                         #
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

# Module docstring.
"""SCons targets for building the relax distribution packages."""

# Python module imports.
from os import getcwd, path, sep, system, waitpid, walk
from re import search
from subprocess import PIPE, Popen
import sys
from tarfile import TarFile
from zipfile import ZipFile

# relax module imports.
from version import version


# Version control directories to skip.
VERSION_CONTROL_DIRS = [
    r"\.git",
    r"\.hg",
    r"\.svn",
]

# Skip any '.sconsign' files, hidden files, byte-compiled '*.pyc' files, or binary objects '.o', '.os', 'obj', 'lib', and 'exp'.
BLACKLISTED_FILES = [
    r"\.sconsign",
    r"^\.",
    r"\.pyc$",
    r"\.o$",
    r"\.os$",
    r"\.obj$",
    r"\.lib$",
    r"\.exp$",
]

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
        print("\n\nSigning the distribution package " + repr(file) + ".\n")

        # Run the 'gpg' command.
        system("gpg --detach-sign --default-key " + key + " " + path.pardir + path.sep + file)

    # Final printout.
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
        print("\n\nCreating the package distribution " + repr(file) + ".\n")

        # Create the special Mac OS X DMG file and then stop execution.
        if dist_type == 'dmg':
            # Create the Mac OS X universal application.
            print("\n# Creating the Mac OS X universal application.\n\n")
            cmd = '%s setup.py py2app' % sys.executable
            print("%s\n" % cmd)
            pipe = Popen(cmd, shell=True, stdin=PIPE, close_fds=False)
            waitpid(pipe.pid, 0)

            # Create the dmg image.
            print("\n\n# Creating the DMG image.\n\n")
            cmd = 'hdiutil create -ov -fs HFS+ -volname "relax" -srcfolder dist/relax.app ../%s' % file
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

        # Find all files untracked by the VC and not ignored.
        untracked = []
        if path.isdir(getcwd() + path.sep + ".git"):
            cmd = "git ls-files --others --exclude-standard"
            pipe = Popen(cmd, shell=True, stdout=PIPE, close_fds=False)
            for file_name in pipe.stdout.readlines():
                untracked.append(file_name.strip())

        # Walk through the directories.
        for root, dirs, files in walk(getcwd()):
            # Skip the version control directories.
            skip = False
            for vc in VERSION_CONTROL_DIRS:
                if search(vc, root):
                    skip = True
            if skip:
                continue

            # Add the files in the current directory to the archive.
            for i in range(len(files)):
                # Skip all blacklisted files.
                skip = False
                for file_name in BLACKLISTED_FILES:
                    if search(file_name, files[i]):
                        skip = True

                # Create the file name (without the base directory).
                name = path.join(root, files[i])
                name = name[len(base):]

                # Skip all untracked files.
                if name in untracked:
                    skip = True

                # Nothing to do.
                if skip:
                    continue

                # The archive file name.
                arcname = 'relax-' + version + path.sep + name
                print(arcname)

                # Zip archives.
                if dist_type == 'zip':
                    archive.write(filename=name, arcname=arcname)

                # Tar archives.
                if dist_type == 'tar':
                    archive.add(name=name, arcname=arcname)

        # Close the archive.
        archive.close()

    # Final printout.
    print("\n\n\n")
