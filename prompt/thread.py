###############################################################################
#                                                                             #
# Copyright (C) 2004-2005 Edward d'Auvergne                                   #
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

import sys

import help


class Threading:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for controlling threading of calculations."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def read(self, file="hosts", dir="~/.relax"):
        """Function for reading a file containing entries for each computer to run calculations on.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the file containing the host entries.

        dir:  The directory where the hosts file is located.


        Description
        ~~~~~~~~~~~

        Certain functions within relax are coded to handle threading.  This is achieved by running
        multiple instances of relax on different processes or computers for each thread.  The
        default behaviour is that the parent instance of relax will execute all the code, however if
        a hosts file is read or a hosts entry manually entered, then the threaded code will run on
        the specified hosts.  This function is for reading a hosts file which should contain an
        an entry for each computer on which to run calculations.

        For remote computers, a SSH connection will be attempted.  Public key authentication must be
        enabled to run calculations on remote machines so that thread can be created without asking
        for a password.  Details on how to do this are given below.


        The format of the hosts file is as follows.  Default values are specified by placing the
        character '-' in the corresponding column.  Columns can be separated by any whitespace
        character, and all columns must contain an entry.  Any lines beginning with a hash will be
        ignored.

        Column 1:  The host name or IP address of the computer on which to run a thread.

        Column 2:  The login name of the user on the remote machine.  The default is to use the same
        name as the current user.

        Column 3:  The full program path.  The default is to run 'relax'.  This only works if relax
        can be found in the environmental variable $PATH, as alias are not recognised.

        Column 4:  The working directory where thread specific files are stored.  The default is
        '~/.relax' where the tilde '~' symbol represents the user's home directory on the remote
        machine.

        Column 5:  The priority value for running the program.  The default is 15.  The remote
        instances of relax will be niced to this value.

        Column 6:  The number of CPU or CPU cores on the machine.  The default is 1.  A thread is
        started for each CPU.

        An example is:

        -------------------------------------------------------------------------------------------
        # Host          User name       Program path            Working directory    Priority  CPUs
        localhost       -               -                       -                    0         2
        192.168.0.10    dauvergne       /usr/local/bin/relax    -                    -         -
        192.168.0.11    edward          -                       -                    -         -
        -------------------------------------------------------------------------------------------

        In this case, two threads will be run on the parent computer which would be either a dual
        CPU system or a dual core 'Hyper threaded' Pentium processor.  These threads will have the
        highest level user priority of 0.  The other two machines will have single threads running
        with a low priority of 15.

        Once threading is enabled, to allow calculations to run on the parent machine a 'localhost'
        entry should be included.


        If the keyword argument 'dir' is set to None, the hosts file will be assumed to be in the
        current working directory.


        SSH Public Key Authentication
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        To enable SSH Public Key Authentication for the use of ssh, sftp, and scp without having to
        type a password, use the following steps.  This is essential for running a thread on a
        remote machine.

        If the files 'id_rsa' and 'id_rsa.pub' do not exist in the directory '~/.ssh', type:

        $ ssh-keygen -t rsa

        Press enter three times when asked for input.  This will generate the two identification
        files.  Then, to copy the public key into the 'authorized_keys' file on the remote machine,
        type:

        $ ssh zucchini "echo $(cat ~/.ssh/id_rsa.pub) >> ~/.ssh/authorized_keys"

        Make sure you replace 'zucchini' with the name or IP address of the remote machine.  To use
        DSA rather than RSA authentication, replace 'rsa' with 'dsa' in the above commands.
        Normally the sshd keyword StrictModes, which is found in the file '/etc/ssh/sshd_config', is
        set to 'yes' or, if unspecified, defaults to 'yes'.  In this case, public key authentication
        may fail as the permissions of the remote file '~/.ssh/authorized_keys' may be too
        permissive.  The file should only be read/write for the user, ie 600.  To remotely change
        the permissions, type:

        $ ssh zucchini "chmod 600 ~/.ssh/authorized_keys"

        One last keyword may need to be changed in the file '/etc/ssh/sshd_config'.  If the keyword
        PubkeyAuthentication is set to 'no', change this to 'yes'.  The default is yes, so if the
        keyword is missing or is commented out, nothing needs to be done.

        Public key authentication should now work.  To test, type:

        $ ssh zucchini

        This should securely login into the remote machine without asking for a password.  If a
        password prompt appears, check all the permissions on the directory '~/.ssh' and all files
        within or set the sshd_config keyword StrictModes to 'no'.

        $ ssh zucchini "chmod 700 ~/.ssh/"
        $ ssh zucchini "chmod 600 ~/.ssh/*"
        $ ssh zucchini "chmod 644 ~/.ssh/*.pub"

        Finally, if all else fails, make sure the three lines
        
        -----
        RSAAuthentication yes
        PubkeyAuthentication yes
        AuthorizedKeysFile      .ssh/authorized_keys
        -----

        of the file 'sshd_config' found within the directory '/etc/ssh/' are uncommented and not set
        to 'no' or the 'AuthorizedKeysFile' set to another file name.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "thread.read("
            text = text + "file=" + `file`
            text = text + ", dir=" + `dir` + ")"
            print text

        # The file name.
        if type(file) != str:
            raise RelaxStrError, ('file', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # Execute the functional code.
        self.__relax__.threading.read(file=file, dir=dir)
