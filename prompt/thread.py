###############################################################################
#                                                                             #
# Copyright (C) 2004 Edward d'Auvergne                                        #
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
        an entry for each computer and each processor on which to run calculations.

        For remote computers, a SSH connection will be attempted.  Public key authentication must be
        enabled to run calculations on remote machines so that thread can be created without asking
        for a password.  View the ssh man page for setting up public key authentication.

        The format of the hosts file is as follows.  The first column is reserved for the host name
        or IP address of the computer on which to run a thread.  The second column is the login name
        of the user on the remote machine.  The default, specified by the character '-', is to use
        the same name as the current user.  The third is the full program path.  The default,
        specified by '-', is to run 'relax'.  This only works if relax can be found in the
        environmental variable $PATH, alias are not recognised.  The fourth column is the working
        directory where temporary files are stored.  The default, again specified by the character
        '-', is '~/.relax' where the tilde '~' symbol represents the home directory.  The fifth
        column is the priority value for running the program, where the default is 15.  Any lines
        beginning with a hash will be ignored.  An example is:

        -------------------------------------------------------------------------------------------
        # Host          User name       Program path            Working directory       Priority
        localhost       -               -                       -                       0
        localhost       -               -                       -                       0
        192.168.0.10    dauvergne       /usr/local/bin/relax    -                       -
        192.168.0.11    edward          -                       -                       -
        -------------------------------------------------------------------------------------------

        In this case, two threads will be run on the parent computer which would be either a dual
        CPU system or a dual core 'Hyper threaded' Pentium processor.  These threads will have the
        highest level user priority of 0.  The other two machines will have single threads running
        with a low priority of 15.

        Once threading is enabled, to allow calculations to run on the parent machine, at least one
        'localhost' entry must be supplied.


        If the keyword argument 'dir' is set to None, the hosts file will be assumed to be in the
        current working directory.


        SSH Public Key Authentication
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        To enable SSH Public Key Authentication to be able to use ssh, sftp, and scp from the parent
        machine to the hosts without having to type your password, use the following steps.

        If the files 'id_rsa' and 'id_rsa.pub' do not exist in the directory '~/.ssh', type:

        $ ssh-keygen -t rsa (Type [Enter] 3 times)

        Once the two files exist, type:

        (Make sure you replace 'zucchini' with the name of the machine you want to forward to).

        $ ssh zucchini "echo $(cat ~/.ssh/id_rsa.pub) >> ~/.ssh/authorized_keys"

        Finished. You can now type 'ssh zucchini' and login without typing your password.
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
        self.__relax__.generic.threading.read(file=file, dir=dir)
