###############################################################################
#                                                                             #
# Copyright (C) 2001-2014,2016-2017 Edward d'Auvergne                         #
# Copyright (C) 2008 Sebastien Morin                                          #
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
"""Module containing the introductory text container."""

# Dependencies.
import dep_check

# Python module imports.
if dep_check.ctypes_module:
    import ctypes
    if hasattr(ctypes, 'windll'):
        import ctypes.wintypes
else:
    ctypes = None
if dep_check.ctypes_structure_module:
    from ctypes import Structure
else:
    Structure = object
from os import environ, pathsep, waitpid
import platform
from re import search, sub
PIPE, Popen = None, None
if dep_check.subprocess_module:
    from subprocess import PIPE, Popen
import sys
from textwrap import wrap

# relax module imports.
from lib.compat import linux_distribution
from status import Status; status = Status()
from version import repo_head, repo_type, repo_url, version, version_full


def print_sys_info():
    """Print out the system information."""

    # Initialise the info box.
    info = Info_box()

    # Print all info.
    print(info.sys_info())



class Info_box(object):
    """A container storing information about relax."""

    # Class variable for storing the class instance.
    instance = None

    def __init__(self):
        """Create the program introduction text stings.

        This class generates a container with the following objects:
            - title:  The program title 'relax'
            - version:  For example 'repository commit' or '1.3.8'.
            - desc:  The short program description.
            - copyright:  A list of copyright statements.
            - licence:  Text pertaining to the licencing.
            - errors:  A list of import errors.
        """

        # Program name and version.
        self.title = "relax"
        self.version = version

        # The relax website.
        self.website = "http://www.nmr-relax.com"

        # Program description.
        self.desc = "Molecular dynamics by NMR data analysis"

        # Long description
        self.desc_long = "The program relax is designed for the study of the dynamics of proteins or other macromolecules though the analysis of experimental NMR data. It is a community driven project created by NMR spectroscopists for NMR spectroscopists. It supports exponential curve fitting for the calculation of the R1 and R2 relaxation rates, calculation of the NOE, reduced spectral density mapping, and the Lipari and Szabo model-free analysis."

        # Copyright printout.
        self.copyright_final_year = 2020
        self.copyright = []
        self.copyright.append("Copyright (C) 2001-2006 Edward d'Auvergne")
        self.copyright.append("Copyright (C) 2006-%s the relax development team" % self.copyright_final_year)
        self.copyright_short = "Copyright (C) 2001-%s the relax development team" % self.copyright_final_year
        self.copyright_latex = "Copyright \copyright\ 2001-%s the relax development team" % self.copyright_final_year

        # Program licence and help.
        self.licence = "This is free software which you are welcome to modify and redistribute under the conditions of the GNU General Public License (GPL), Version 3 or any later version published by the Free Software Foundation.  This program, including all modules, is licensed under the GPL and comes with absolutely no warranty.  For details type 'GPL' within the relax prompt."

        # ImportErrors, if any.
        self.errors = []
        if not dep_check.C_module_exp_fn:
            self.errors.append(dep_check.C_module_exp_fn_mesg)

        # References.
        self._setup_references()


    def __new__(self, *args, **kargs):
        """Replacement function for implementing the singleton design pattern."""

        # First initialisation.
        if self.instance is None:
            self.instance = object.__new__(self, *args, **kargs)

        # Already initialised, so return the instance.
        return self.instance


    def _setup_references(self):
        """Build a dictionary of all references useful for relax."""

        # Initialise the dictionary.
        self.bib = {}

        # Place the containers into the dictionary.
        self.bib['Bieri11'] = Bieri11()
        self.bib['Clore90'] = Clore90()
        self.bib['dAuvergne06'] = dAuvergne06()
        self.bib['dAuvergneGooley03'] = dAuvergneGooley03()
        self.bib['dAuvergneGooley06'] = dAuvergneGooley06()
        self.bib['dAuvergneGooley07'] = dAuvergneGooley07()
        self.bib['dAuvergneGooley08a'] = dAuvergneGooley08a()
        self.bib['dAuvergneGooley08b'] = dAuvergneGooley08b()
        self.bib['Delaglio95'] = Delaglio95()
        self.bib['GoddardKneller'] = GoddardKneller()
        self.bib['LipariSzabo82a'] = LipariSzabo82a()
        self.bib['LipariSzabo82b'] = LipariSzabo82b()


    def centre(self, string, width=100):
        """Format the string to be centred to a certain number of spaces.

        @param string:  The string to centre.
        @type string:   str
        @keyword width: The number of characters to centre to.
        @type width:    int
        @return:        The centred string with leading whitespace added.
        @rtype:         str
        """

        # Calculate the number of spaces needed.
        spaces = int((width - len(string)) / 2)

        # The new string.
        string = spaces * ' ' + string

        # Return the new string.
        return string


    def file_type(self, path):
        """Return a string representation of the file type.

        @param path:    The full path of the file to return information about.
        @type path:     str
        @return:        The single line file type information string.
        @rtype:         str
        """

        # Python 2.3 and earlier.
        if Popen == None:
            return ''

        # Test if the 'file' program is installed.
        pipe = Popen('file --help', shell=True, stdout=PIPE, stderr=PIPE, close_fds=False)
        err = pipe.stderr.readlines()
        if err:
            return ''

        # The command.
        cmd = "file -b '%s'" % path

        # Execute.
        pipe = Popen(cmd, shell=True, stdout=PIPE, close_fds=False)
        if not hasattr(ctypes, 'windll'):
            waitpid(pipe.pid, 0)

        # The STDOUT data.
        data = pipe.stdout.readlines()

        # Mac OS X 3-way binary.
        if data[0][:-1] == 'Mach-O universal binary with 3 architectures':
            # Arch.
            arch = [None, None, None]
            for i in range(3):
                row = data[i+1].split('\t')
                arch[i] = row[1][:-1]
            arch.sort()

            # The full file type printout.
            if arch == ['Mach-O 64-bit executable x86_64', 'Mach-O executable i386', 'Mach-O executable ppc']:
                file_type = '3-way exec (i386, ppc, x86_64)'
            elif arch == ['Mach-O 64-bit bundle x86_64', 'Mach-O bundle i386', 'Mach-O bundle ppc']:
                file_type = '3-way bundle (i386, ppc, x86_64)'
            elif arch == ['Mach-O 64-bit dynamically linked shared library x86_64', 'Mach-O dynamically linked shared library i386', 'Mach-O dynamically linked shared library ppc']:
                file_type = '3-way lib (i386, ppc, x86_64)'
            elif arch == ['Mach-O 64-bit object x86_64', 'Mach-O object i386', 'Mach-O object ppc']:
                file_type = '3-way obj (i386, ppc, x86_64)'
            else:
                file_type = '3-way %s' % arch

        # Mac OS X 2-way binary.
        elif data[0][:-1] == 'Mach-O universal binary with 2 architectures':
            # Arch.
            arch = [None, None]
            for i in range(2):
                row = data[i+1].split('\t')
                arch[i] = row[1][:-1]
            arch.sort()

            # The full file type printout.
            if arch == ['Mach-O executable i386', 'Mach-O executable ppc']:
                file_type = '2-way exec (i386, ppc)'
            elif arch == ['Mach-O bundle i386', 'Mach-O bundle ppc']:
                file_type = '2-way bundle (i386, ppc)'
            elif arch == ['Mach-O dynamically linked shared library i386', 'Mach-O dynamically linked shared library ppc']:
                file_type = '2-way lib (i386, ppc)'
            elif arch == ['Mach-O object i386', 'Mach-O object ppc']:
                file_type = '2-way obj (i386, ppc)'
            else:
                file_type = '2-way %s' % arch

        # Default to all info.
        else:
            file_type = data[0][:-1]
            if hasattr(file_type, 'decode'):
                file_type = file_type.decode()
            for i in range(1, len(data)):
                row = data[i].split('\t')
                arch[i] = row[1][:-1]
                file_type += " %s" % arch

        # Return a string value.
        if file_type == None:
            return ''
        return file_type


    def format_max_width(self, data):
        """Return the text formatting width for the given data.

        @param data:    The list of things to print out.
        @type data:     list
        @return:        The maximum width of the elements in the list.
        @rtype:         int
        """

        # Init.
        width = 0

        # Loop over the data.
        for i in range(len(data)):
            # The string representation size.
            size = len(str(data[i]))

            # Find the max size.
            if size > width:
                width = size

        # Return the max width.
        return width


    def intro_text(self):
        """Create the introductory string for STDOUT printing.

        This text is word-wrapped to a fixed width of 100 characters (or 80 on MS Windows).


        @return:    The introductory string.
        @rtype:     str
        """

        # Some new lines.
        intro_string = '\n\n\n'

        # Program name and version - subversion code.
        if version == 'repository commit':
            if repo_type == 'git':
                text = "%s %s" % (self.title, self.version)
                text2 = "%s" % repo_head
            else:
                text = "%s %s r%s" % (self.title, self.version, repo_head)
                text2 = "%s" % repo_url
            intro_string += self.centre(text, status.text_width) + '\n' + self.centre(text2, status.text_width) + '\n'
            if repo_type == 'git':
                for url in repo_url.split('\n'):
                    intro_string += self.centre(url, status.text_width) + '\n'
            intro_string += '\n'

        # Program name and version - official releases.
        else:
            text = "%s %s" % (self.title, self.version)
            intro_string = intro_string + self.centre(text, status.text_width) + '\n\n'

        # Program description.
        intro_string = intro_string + self.centre(self.desc, status.text_width) + '\n\n'

        # Copyright printout.
        for i in range(len(self.copyright)):
            intro_string = intro_string + self.centre(self.copyright[i], status.text_width) + '\n'
        intro_string = intro_string + '\n'

        # Program licence and help (wrapped).
        for line in wrap(self.licence, status.text_width):
            intro_string = intro_string + line + '\n'
        intro_string = intro_string + '\n'
 
        # Help message.
        help = "Assistance in using the relax prompt and scripting interface can be accessed by typing 'help' within the prompt."
        for line in wrap(help, status.text_width):
            intro_string = intro_string + line + '\n'

        # ImportErrors, if any.
        for i in range(len(self.errors)):
            intro_string = intro_string + '\n' + self.errors[i] + '\n'
        intro_string = intro_string + '\n'

        # The multi-processor message, if it exists.
        if hasattr(self, 'multi_processor_string'):
            for line in wrap('Processor fabric:  %s\n' % self.multi_processor_string, status.text_width):
                intro_string = intro_string + line + '\n'

        # Return the formatted text.
        return intro_string


    def package_info(self):
        """Return a string for printing to STDOUT with info from the Python packages used by relax.

        @return:            The info string.
        @rtype:             str
        """

        # Init.
        text = ''
        package = []
        status = []
        version = []
        path = []

        # Intro.
        text = text + ("\nPython packages and modules (most are optional):\n\n")

        # Header.
        package.append("Name")
        status.append("Installed")
        version.append("Version")
        path.append("Path")

        # minfx.
        package.append('minfx')
        status.append(True)
        if hasattr(dep_check.minfx, '__version__'):
            version.append(dep_check.minfx.__version__)
        else:
            version.append('Unknown')
        path.append(dep_check.minfx.__path__[0])

        # bmrblib.
        package.append('bmrblib')
        status.append(dep_check.bmrblib_module)
        try:
            if hasattr(dep_check.bmrblib, '__version__'):
                version.append(dep_check.bmrblib.__version__)
            else:
                version.append('Unknown')
        except:
            version.append('')
        try:
            path.append(dep_check.bmrblib.__path__[0])
        except:
            path.append('')

        # numpy.
        package.append('numpy')
        status.append(True)
        try:
            version.append(dep_check.numpy.version.version)
            path.append(dep_check.numpy.__path__[0])
        except:
            version.append('')
            path.append('')

        # scipy.
        package.append('scipy')
        status.append(dep_check.scipy_module)
        try:
            version.append(dep_check.scipy.version.version)
            path.append(dep_check.scipy.__path__[0])
        except:
            version.append('')
            path.append('')

        # wxPython.
        package.append('wxPython')
        status.append(dep_check.wx_module)
        try:
            version.append(dep_check.wx.version())
            path.append(dep_check.wx.__path__[0])
        except:
            version.append('')
            path.append('')

        # matplotlib.
        package.append('matplotlib')
        status.append(dep_check.matplotlib_module)
        try:
            version.append(dep_check.matplotlib.__version__)
            path.append(dep_check.matplotlib.__path__[0])
        except:
            version.append('')
            path.append('')

        # mpi4py.
        package.append('mpi4py')
        status.append(dep_check.mpi4py_module)
        try:
            version.append(dep_check.mpi4py.__version__)
            path.append(dep_check.mpi4py.__path__[0])

            # MPI version.
            try:
                import mpi4py.MPI
                vendor = mpi4py.MPI.get_vendor()
                version[-1] += (" (%s %s.%s.%s)" % (vendor[0], vendor[1][0], vendor[1][1], vendor[1][2]))
            except:
                pass

        except:
            version.append('')
            path.append('')

        # epydoc.
        package.append('epydoc')
        status.append(dep_check.epydoc_module)
        try:
            version.append(dep_check.epydoc.__version__)
            path.append(dep_check.epydoc.__path__[0])
        except:
            version.append('')
            path.append('')

        # optparse.
        package.append('optparse')
        status.append(True)
        try:
            version.append(dep_check.optparse.__version__)
            path.append(dep_check.optparse.__file__)
        except:
            version.append('')
            path.append('')

        # readline.
        package.append('readline')
        status.append(dep_check.readline_module)
        version.append('')
        try:
            path.append(dep_check.readline.__file__)
        except:
            path.append('')

        # profile.
        package.append('profile')
        status.append(dep_check.profile_module)
        version.append('')
        try:
            path.append(dep_check.profile.__file__)
        except:
            path.append('')

        # BZ2.
        package.append('bz2')
        status.append(dep_check.bz2_module)
        version.append('')
        try:
            path.append(dep_check.bz2.__file__)
        except:
            path.append('')

        # gzip.
        package.append('gzip')
        status.append(dep_check.gzip_module)
        version.append('')
        try:
            path.append(dep_check.gzip.__file__)
        except:
            path.append('')

        # IO.
        package.append('io')
        status.append(dep_check.io_module)
        version.append('')
        try:
            path.append(dep_check.io.__file__)
        except:
            path.append('')

        # XML.
        package.append('xml')
        status.append(dep_check.xml_module)
        if dep_check.xml_module:
            version.append("%s (%s)" % (dep_check.xml_version, dep_check.xml_type))
            path.append(dep_check.xml.__file__)
        else:
            version.append('')
            path.append('')

        # XML minidom.
        package.append('xml.dom.minidom')
        version.append('')
        try:
            import xml.dom.minidom
            status.append(True)
        except:
            status.append(False)
        try:
            path.append(xml.dom.minidom.__file__)
        except:
            path.append('')

        # Format the data.
        fmt_package = "%%-%ss" % (self.format_max_width(package) + 2)
        fmt_status = "%%-%ss" % (self.format_max_width(status) + 2)
        fmt_version = "%%-%ss" % (self.format_max_width(version) + 2)
        fmt_path = "%%-%ss" % (self.format_max_width(path))

        # Add the text.
        for i in range(len(package)):
            text += fmt_package % package[i]
            text += fmt_status % status[i]
            text += fmt_version % version[i]
            text += fmt_path % path[i]
            text += '\n'

        # Return the info string.
        return text


    def processor_name(self):
        """Return a string for the processor name.

        @return:    The processor name, in much more detail than platform.processor().
        @rtype:     str
        """

        # Python 2.3 and earlier.
        if Popen == None:
            return ""

        # No subprocess module.
        if not dep_check.subprocess_module:
            return ""

        # The system.
        system = platform.system()

        # Linux systems.
        if system == 'Linux':
            # The command to run.
            cmd = "cat /proc/cpuinfo"

            # Execute the command.
            pipe = Popen(cmd, shell=True, stdout=PIPE, close_fds=False)
            waitpid(pipe.pid, 0)

            # Get the STDOUT data.
            data = pipe.stdout.readlines()

            # Loop over the lines, returning the first model name with the leading "model name  :" text stripped.
            for line in data:
                # Decode Python 3 byte arrays.
                if hasattr(line, 'decode'):
                    line = line.decode()

                # Find the processor name.
                if search("model name", line):
                    # Convert the text.
                    name = sub(".*model name.*:", "", line, 1)
                    name = name.strip()

                    # Return the name.
                    return name

        # Windows systems.
        if system == 'Windows' or system == 'Microsoft':
            return platform.processor()

        # Mac OS X systems.
        if system == 'Darwin':
            # Add the 'sysctl' path to the environment (if needed).
            environ['PATH'] += pathsep + '/usr/sbin'

            # The command to run.
            cmd = "sysctl -n machdep.cpu.brand_string"

            # Execute the command in a fail safe way, return the result or nothing.
            try:
                # Execute.
                pipe = Popen(cmd, shell=True, stdout=PIPE, close_fds=False)
                waitpid(pipe.pid, 0)

                # Get the STDOUT data.
                data = pipe.stdout.readlines()

                # Decode Python 3 byte arrays.
                string = data[0]
                if hasattr(string, 'decode'):
                    string = string.decode()

                # Find the processor name.
                # Return the string.
                return string.strip()

            # Nothing.
            except:
                return ""

        # Unknown.
        return ""


    def ram_info(self, format="    %-25s%s\n"):
        """Return a string for printing to STDOUT with info from the Python packages used by relax.

        @keyword format:    The formatting string.
        @type format:       str
        @return:            The info string.
        @rtype:             str
        """

        # Python 2.3 and earlier.
        if Popen == None:
            return ''

        # Init.
        text = ''

        # The system.
        system = platform.system()

        # Unix and GNU/Linux systems.
        if system == 'Linux':
            pipe = Popen('free -m', shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)
            free_lines = pipe.stdout.readlines()
            if free_lines:
                # Extract the info.
                for line in free_lines:
                    # Split up the line.
                    row = line.split()

                    # The RAM size.
                    if row[0] == 'Mem:':
                        text += format % ("Total RAM size: ", row[1], "Mb")

                    # The swap size.
                    if row[0] == 'Swap:':
                        text += format % ("Total swap size: ", row[1], "Mb")

        # Windows systems (supported by ctypes.windll).
        if system == 'Windows' or system == 'Microsoft':
            # Initialise the memory info class.
            mem = MemoryStatusEx()

            # The RAM size.
            text += format % ("Total RAM size: ", mem.ullTotalPhys / 1024.**2, "Mb")

            # The swap size.
            text += format % ("Total swap size: ", mem.ullTotalVirtual / 1024.**2, "Mb")

        # Mac OS X systems.
        if system == 'Darwin':
            # Add the 'sysctl' path to the environment (if needed).
            environ['PATH'] += pathsep + '/usr/sbin'

            # The commands to run.
            cmd = "sysctl -n hw.physmem"
            cmd2 = "sysctl -n hw.memsize"

            # Execute the command in a fail safe way, return the result or nothing.
            try:
                # Execute.
                pipe = Popen(cmd, shell=True, stdout=PIPE, close_fds=False)
                waitpid(pipe.pid, 0)

                # Get the STDOUT data.
                data = pipe.stdout.readlines()

                # Execute.
                pipe = Popen(cmd2, shell=True, stdout=PIPE, close_fds=False)
                waitpid(pipe.pid, 0)

                # Get the STDOUT data.
                data2 = pipe.stdout.readlines()

                # Convert the values.
                ram = int(data[0].strip())
                total = int(data2[0].strip())
                swap = total - ram

                # The RAM size.
                text += format % ("Total RAM size: ", ram / 1024.**2, "Mb")

                # The swap size.
                text += format % ("Total swap size: ", swap / 1024.**2, "Mb")

            # Nothing.
            except:
                pass

        # Unknown.
        if not text:
            text += format % ("Total RAM size: ", "?", "Mb")
            text += format % ("Total swap size: ", "?", "Mb")

        # Return the info string.
        return text


    def relax_module_info(self):
        """Return a string with info about the relax modules.

        @return:            The info string.
        @rtype:             str
        """

        # Init.
        text = ''
        name = []
        status = []
        file_type = []
        path = []

        # Intro.
        text = text + ("\nrelax C modules:\n\n")

        # Header.
        name.append("Module")
        status.append("Compiled")
        file_type.append("File type")
        path.append("Path")

        # relaxation curve-fitting.
        name.append('target_functions.relax_fit')
        status.append(dep_check.C_module_exp_fn)
        if hasattr(dep_check, 'relax_fit'):
            file_type.append(self.file_type(dep_check.relax_fit.__file__))
            path.append(dep_check.relax_fit.__file__)
        else:
            file_type.append('')
            path.append('')

        # Format the data.
        fmt_name = "%%-%ss" % (self.format_max_width(name) + 2)
        fmt_status = "%%-%ss" % (self.format_max_width(status) + 2)
        fmt_file_type = "%%-%ss" % (self.format_max_width(file_type) + 2)
        fmt_path = "%%-%ss" % (self.format_max_width(path) + 2)

        # Add the text.
        for i in range(len(name)):
            text += fmt_name % name[i]
            text += fmt_status % status[i]
            text += fmt_file_type % file_type[i]
            text += fmt_path % path[i]
            text += '\n'
        
        # Return the info string.
        return text


    def sys_info(self):
        """Return a string for printing to STDOUT with info about the current relax instance.

        @return:    The info string.
        @rtype:     str
        """

        # Init.
        text = ''

        # Formatting string.
        format  = "    %-25s%s\n"
        format2 = "    %-25s%s %s\n"

        # Hardware info.
        text = text + ("\nHardware information:\n")
        if hasattr(platform, 'machine'):
            text = text + (format % ("Machine: ", platform.machine()))
        if hasattr(platform, 'processor'):
            text = text + (format % ("Processor: ", platform.processor()))
        text = text + (format % ("Processor name: ", self.processor_name()))
        text = text + (format % ("Endianness: ", sys.byteorder))
        text = text + self.ram_info(format=format2)

        # OS info.
        text = text + ("\nOperating system information:\n")
        if hasattr(platform, 'system'):
            text = text + (format % ("System: ", platform.system()))
        if hasattr(platform, 'release'):
            text = text + (format % ("Release: ", platform.release()))
        if hasattr(platform, 'version'):
            text = text + (format % ("Version: ", platform.version()))
        if hasattr(platform, 'win32_ver') and platform.win32_ver()[0]:
            text = text + (format % ("Win32 version: ", (platform.win32_ver()[0] + " " + platform.win32_ver()[1] + " " + platform.win32_ver()[2] + " " + platform.win32_ver()[3])))
        if linux_distribution()[0]:
            text = text + (format % ("GNU/Linux version: ", (linux_distribution()[0] + " " + linux_distribution()[1] + " " + linux_distribution()[2])))
        if hasattr(platform, 'mac_ver') and platform.mac_ver()[0]:
            text = text + (format % ("Mac version: ", (platform.mac_ver()[0] + " (" + platform.mac_ver()[1][0] + ", " + platform.mac_ver()[1][1] + ", " + platform.mac_ver()[1][2] + ") " + platform.mac_ver()[2])))
        if hasattr(platform, 'dist'):
            text = text + (format % ("Distribution: ", (platform.dist()[0] + " " + platform.dist()[1] + " " + platform.dist()[2])))
        if hasattr(platform, 'platform'):
            text = text + (format % ("Full platform string: ", (platform.platform())))
        if hasattr(ctypes, 'windll'):
            text = text + (format % ("Windows architecture: ", (self.win_arch())))

        # Python info.
        text = text + ("\nPython information:\n")
        if hasattr(platform, 'architecture'):
            text = text + (format % ("Architecture: ", (platform.architecture()[0] + " " + platform.architecture()[1])))
        if hasattr(platform, 'python_version'):
            text = text + (format % ("Python version: ", platform.python_version()))
        if hasattr(platform, 'python_branch'):
            text = text + (format % ("Python branch: ", platform.python_branch()))
        if hasattr(platform, 'python_build'):
            text = text + ((format[:-1]+', %s\n') % ("Python build: ", platform.python_build()[0], platform.python_build()[1]))
        if hasattr(platform, 'python_compiler'):
            text = text + (format % ("Python compiler: ", platform.python_compiler()))
        if hasattr(platform, 'libc_ver'):
            text = text + (format % ("Libc version: ", (platform.libc_ver()[0] + " " + platform.libc_ver()[1])))
        if hasattr(platform, 'python_implementation'):
            text = text + (format % ("Python implementation: ", platform.python_implementation()))
        if hasattr(platform, 'python_revision'):
            text = text + (format % ("Python revision: ", platform.python_revision()))
        if sys.executable:
            text = text + (format % ("Python executable: ", sys.executable))
        if hasattr(sys, 'flags'):
            text = text + (format % ("Python flags: ", sys.flags))
        if hasattr(sys, 'float_info'):
            text = text + (format % ("Python float info: ", sys.float_info))
        text = text + (format % ("Python module path: ", sys.path))

        # Python packages.
        text = text + self.package_info()

        # relax info:
        text = text + "\nrelax information:\n"
        text = text + (format % ("Version: ", version_full()))
        if hasattr(self, "multi_processor_string"):
            text += format % ("Processor fabric: ", self.multi_processor_string)

        # relax modules.
        text = text + self.relax_module_info()

        # End with an empty newline.
        text = text + ("\n")

        # Return the text.
        return text


    def win_arch(self):
        """Determine the MS Windows architecture.

        @return:    The architecture string.
        @rtype:     str
        """

        # 64-bit versions.
        if 'PROCESSOR_ARCHITEW6432' in environ:
            arch = environ['PROCESSOR_ARCHITEW6432']

        # Default 32-bit.
        else:
            arch = environ['PROCESSOR_ARCHITECTURE']

        # Return the architecture.
        return arch



class MemoryStatusEx(Structure):
    """Special object for obtaining hardware info in MS Windows."""

    if hasattr(ctypes, 'windll'):
        _fields_ = [
            ('dwLength', ctypes.wintypes.DWORD),
            ('dwMemoryLoad', ctypes.wintypes.DWORD),
            ('ullTotalPhys', ctypes.c_ulonglong),
            ('ullAvailPhys', ctypes.c_ulonglong),
            ('ullTotalPageFile', ctypes.c_ulonglong),
            ('ullAvailPageFile', ctypes.c_ulonglong),
            ('ullTotalVirtual', ctypes.c_ulonglong),
            ('ullAvailVirtual', ctypes.c_ulonglong),
            ('ullExtendedVirtual', ctypes.c_ulonglong),
        ]

    def __init__(self):
        """Set up the information and handle non MS Windows systems."""

        # Get the required info (for MS Windows only).
        if hasattr(ctypes, 'windll'):
            self.dwLength = ctypes.sizeof(self)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(self))



class Ref:
    """Reference base class."""

    # Initialise all class variables to None.
    type = None
    author = None
    author2 = None
    title = None
    status = None
    journal = None
    journal_full = None
    volume = None
    number = None
    doi = None
    pubmed_id = None
    url = None
    pages = None
    year = None


    def __getattr__(self, name):
        """Generate some variables on the fly.

        This is only called for objects not found in the class.

        @param name:            The name of the object.
        @type name:             str
        @raises AttributeError: If the object cannot be created.
        @returns:               The generated object.
        @rtype:                 anything
        """

        # Page numbers.
        if name in ['page_first', 'page_last']:
            # No page info.
            if not self.pages:
                return None

            # First split the page range.
            vals = self.pages.split('-')

            # Single page.
            if len(vals) == 1:
                return vals[0]

            # First page.
            if name == 'page_first':
                return vals[0]

            # Last page.
            if name == 'page_last':
                return vals[1]

        raise AttributeError(name)


    def cite_short(self, author=True, title=True, journal=True, volume=True, number=True, pages=True, year=True, doi=True, url=True, status=True):
        """Compile a short citation.
        
        The returned text will have the form of:

            - d'Auvergne, E.J. and Gooley, P.R. (2008). Optimisation of NMR dynamic models I. Minimisation algorithms and their performance within the model-free and Brownian rotational diffusion spaces. J. Biomol. NMR, 40(2), 107-119.


        @keyword author:    The author flag.
        @type author:       bool
        @keyword title:     The title flag.
        @type title:        bool
        @keyword journal:   The journal flag.
        @type journal:      bool
        @keyword volume:    The volume flag.
        @type volume:       bool
        @keyword number:    The number flag.
        @type number:       bool
        @keyword pages:     The pages flag.
        @type pages:        bool
        @keyword year:      The year flag.
        @type year:         bool
        @keyword doi:       The doi flag.
        @type doi:          bool
        @keyword url:       The url flag.
        @type url:          bool
        @keyword status:    The status flag.  This will only be shown if not 'published'.
        @type status:       bool
        @return:            The full citation.
        @rtype:             str
        """

        # Build the citation.
        cite = ''
        if author and self.author and hasattr(self, 'author'):
            cite = cite + self.author
        if year and self.year and hasattr(self, 'year'):
            cite = cite + ' (' + repr(self.year) + ').'
        if title and self.title and hasattr(self, 'title'):
            cite = cite + ' ' + self.title
        if journal and self.journal and hasattr(self, 'journal'):
            cite = cite + ' ' + self.journal + ','
        if volume and self.volume and hasattr(self, 'volume'):
            cite = cite + ' ' + self.volume
        if number and self.number and hasattr(self, 'number'):
            cite = cite + '(' + self.number + '),'
        if pages and self.pages and hasattr(self, 'pages'):
            cite = cite + ' ' + self.pages
        if doi and self.doi and hasattr(self, 'doi'):
            cite = cite + ' (http://dx.doi.org/'+self.doi + ')'
        if url and self.url and hasattr(self, 'url'):
            cite = cite + ' (' + self.url + ')'
        if status and hasattr(self, 'status') and self.status != 'published':
            cite = cite + ' (' + self.status + ')'

        # End.
        if cite[-1] != '.':
            cite = cite + '.'

        # Return the citation.
        return cite


    def cite_html(self, author=True, title=True, journal=True, volume=True, number=True, pages=True, year=True, doi=True, url=True, status=True):
        """Compile a citation for HTML display.

        @keyword author:    The author flag.
        @type author:       bool
        @keyword title:     The title flag.
        @type title:        bool
        @keyword journal:   The journal flag.
        @type journal:      bool
        @keyword volume:    The volume flag.
        @type volume:       bool
        @keyword number:    The number flag.
        @type number:       bool
        @keyword pages:     The pages flag.
        @type pages:        bool
        @keyword year:      The year flag.
        @type year:         bool
        @keyword doi:       The doi flag.
        @type doi:          bool
        @keyword url:       The url flag.
        @type url:          bool
        @keyword status:    The status flag.  This will only be shown if not 'published'.
        @type status:       bool
        @return:            The full citation.
        @rtype:             str
        """

        # Build the citation.
        cite = ''
        if author and hasattr(self, 'author') and self.author:
            cite = cite + self.author
        if year and hasattr(self, 'year') and self.year:
            cite = cite + ' (' + repr(self.year) + ').'
        if title and hasattr(self, 'title') and self.title:
            cite = cite + ' ' + self.title
        if journal and hasattr(self, 'journal') and self.journal:
            cite = cite + ' <em>' + self.journal + '</em>,'
        if volume and hasattr(self, 'volume') and self.volume:
            cite = cite + ' <strong>' + self.volume + '</strong>'
        if number and hasattr(self, 'number') and self.number:
            cite = cite + '(' + self.number + '),'
        if pages and hasattr(self, 'pages') and self.pages:
            cite = cite + ' ' + self.pages
        if doi and hasattr(self, 'doi') and self.doi:
            cite = cite + ' (<a href="http://dx.doi.org/%s">abstract</a>)' % self.doi
        if url and hasattr(self, 'url') and self.url:
            cite = cite + ' (<a href="%s">url</a>)' % self.url
        if status and hasattr(self, 'status') and self.status != 'published':
            cite = cite + ' (<i>%s</i>)' % self.status

        # End.
        if cite[-1] != '.':
            cite = cite + '.'

        # Return the citation.
        return cite



class Bieri11(Ref):
    """Bibliography container."""

    type           = "journal"
    author         = "Bieri, M., d'Auvergne, E. J. and Gooley, P. R."
    author2        = [["Michael", "Bieri", "M.", ""], ["Edward", "d'Auvergne", "E.", "J."], ["Paul", "Gooley", "P.", "R."]]
    title          = "relaxGUI: a new software for fast and simple NMR relaxation data analysis and calculation of ps-ns and micro-s motion of proteins"
    journal        = "J. Biomol. NMR"
    journal_full   = "Journal of Biomolecular NMR"
    abstract       = "Investigation of protein dynamics on the ps-ns and mus-ms timeframes provides detailed insight into the mechanisms of enzymes and the binding properties of proteins. Nuclear magnetic resonance (NMR) is an excellent tool for studying protein dynamics at atomic resolution. Analysis of relaxation data using model-free analysis can be a tedious and time consuming process, which requires good knowledge of scripting procedures. The software relaxGUI was developed for fast and simple model-free analysis and is fully integrated into the software package relax. It is written in Python and uses wxPython to build the graphical user interface (GUI) for maximum performance and multi-platform use. This software allows the analysis of NMR relaxation data with ease and the generation of publication quality graphs as well as color coded images of molecular structures. The interface is designed for simple data analysis and management. The software was tested and validated against the command line version of relax."
    authoraddress  = "Department of Biochemistry and Molecular Biology, University of Melbourne, Melbourne, Victoria 3010, Australia."
    doi            = "10.1007/s10858-011-9509-1"
    pubmed_id      = 21618018
    status         = "published"
    year           = 2011



class Clore90(Ref):
    """Bibliography container."""

    type           = "journal"
    author         = "Clore, G. M. and Szabo, A. and Bax, A. and Kay, L. E. and Driscoll, P. C. and Gronenborn, A. M."
    title          = "Deviations from the simple 2-parameter model-free approach to the interpretation of N-15 nuclear magnetic-relaxation of proteins"
    journal        = "J. Am. Chem. Soc."
    journal_full   = "Journal of the American Chemical Society"
    volume         = "112"
    number         = "12"
    pages          = "4989-4991"
    address        = "1155 16th St, NW, Washington, DC 20036"
    sourceid       = "ISI:A1990DH27700070"
    status         = "published"
    year           = 1990



class dAuvergne06(Ref):
    """Bibliography container."""

    type           = "thesis"
    author         = "d'Auvergne, E. J."
    author2        = [["Edward", "d'Auvergne", "E.", "J."]]
    title          = "Protein dynamics: a study of the model-free analysis of NMR relaxation data."
    school         = "Biochemistry and Molecular Biology, University of Melbourne."
    url            = "http://eprints.infodiv.unimelb.edu.au/archive/00002799/"
    status         = "published"
    year           = 2006



class dAuvergneGooley03(Ref):
    """Bibliography container."""

    type           = "journal"
    author         = "d'Auvergne, E. J. and Gooley, P. R."
    author2        = [["Edward", "d'Auvergne", "E.", "J."], ["Paul", "Gooley", "P.", "R."]]
    title          = "The use of model selection in the model-free analysis of protein dynamics."
    journal        = "J. Biomol. NMR"
    journal_full   = "Journal of Biomolecular NMR"
    volume         = "25"
    number         = "1"
    pages          = "25-39"
    abstract       = "Model-free analysis of NMR relaxation data, which is widely used for the study of protein dynamics, consists of the separation of the global rotational diffusion from internal motions relative to the diffusion frame and the description of these internal motions by amplitude and timescale. Five model-free models exist, each of which describes a different type of motion. Model-free analysis requires the selection of the model which best describes the dynamics of the NH bond. It will be demonstrated that the model selection technique currently used has two significant flaws, under-fitting, and not selecting a model when one ought to be selected. Under-fitting breaks the principle of parsimony causing bias in the final model-free results, visible as an overestimation of S2 and an underestimation of taue and Rex. As a consequence the protein falsely appears to be more rigid than it actually is. Model selection has been extensively developed in other fields. The techniques known as Akaike's Information Criteria (AIC), small sample size corrected AIC (AICc), Bayesian Information Criteria (BIC), bootstrap methods, and cross-validation will be compared to the currently used technique. To analyse the variety of techniques, synthetic noisy data covering all model-free motions was created. The data consists of two types of three-dimensional grid, the Rex grids covering single motions with chemical exchange [S2,taue,Rex], and the Double Motion grids covering two internal motions [S f 2,S s 2,tau s ]. The conclusion of the comparison is that for accurate model-free results, AIC model selection is essential. As the method neither under, nor over-fits, AIC is the best tool for applying Occam's razor and has the additional benefits of simplifying and speeding up model-free analysis."
    authoraddress  = "Department of Biochemistry and Molecular Biology, University of Melbourne, Melbourne, Victoria 3010, Australia."
    keywords       = "Amines ; Diffusion ; *Models, Molecular ; Motion ; Nuclear Magnetic Resonance, Biomolecular/*methods ; Proteins/*chemistry ; Research Support, Non-U.S. Gov't ; Rotation"
    doi            = "10.1023/A:1021902006114"
    pubmed_id      = 12566997
    status         = "published"
    year           = 2003



class dAuvergneGooley06(Ref):
    """Bibliography container."""

    type           = "journal"
    author         = "d'Auvergne, E. J. and Gooley, P. R."
    author2        = [["Edward", "d'Auvergne", "E.", "J."], ["Paul", "Gooley", "P.", "R."]]
    title          = "Model-free model elimination: A new step in the model-free dynamic analysis of NMR relaxation data."
    journal        = "J. Biomol. NMR"
    journal_full   = "Journal of Biomolecular NMR"
    volume         = "35"
    number         = "2"
    pages          = "117-135"
    abstract       = "Model-free analysis is a technique commonly used within the field of NMR spectroscopy to extract atomic resolution, interpretable dynamic information on multiple timescales from the R (1), R (2), and steady state NOE. Model-free approaches employ two disparate areas of data analysis, the discipline of mathematical optimisation, specifically the minimisation of a chi(2) function, and the statistical field of model selection. By searching through a large number of model-free minimisations, which were setup using synthetic relaxation data whereby the true underlying dynamics is known, certain model-free models have been identified to, at times, fail. This has been characterised as either the internal correlation times, tau( e ), tau( f ), or tau( s ), or the global correlation time parameter, local tau( m ), heading towards infinity, the result being that the final parameter values are far from the true values. In a number of cases the minimised chi(2) value of the failed model is significantly lower than that of all other models and, hence, will be the model which is chosen by model selection techniques. If these models are not removed prior to model selection the final model-free results could be far from the truth. By implementing a series of empirical rules involving inequalities these models can be specifically isolated and removed. Model-free analysis should therefore consist of three distinct steps: model-free minimisation, model-free model elimination, and finally model-free model selection. Failure has also been identified to affect the individual Monte Carlo simulations used within error analysis. Each simulation involves an independent randomised relaxation data set and model-free minimisation, thus simulations suffer from exactly the same types of failure as model-free models. Therefore, to prevent these outliers from causing a significant overestimation of the errors the failed Monte Carlo simulations need to be culled prior to calculating the parameter standard deviations."
    authoraddress  = "Department of Biochemistry and Molecular Biology, Bio21 Institute of Biotechnology and Molecular Science, University of Melbourne, Parkville, Victoria, 3010, Australia"
    doi            = "10.1007/s10858-006-9007-z"
    pubmed_id      = 16791734
    status         = "published"
    year           = 2006



class dAuvergneGooley07(Ref):
    """Bibliography container."""

    type           = "journal"
    author         = "d'Auvergne, E. J. and Gooley, P. R."
    author2        = [["Edward", "d'Auvergne", "E.", "J."], ["Paul", "Gooley", "P.", "R."]]
    title          = "Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm."
    journal        = "Mol. Biosys."
    journal_full   = "Molecular BioSystems"
    volume         = "3"
    number         = "7"
    pages          = "483-494"
    abstract       = "Model-free analysis of NMR relaxation data, which describes the motion of individual atoms, is a problem intricately linked to the Brownian rotational diffusion of the macromolecule. The diffusion tensor parameters strongly influence the optimisation of the various model-free models and the subsequent model selection between them. Finding the optimal model of the dynamics of the system among the numerous diffusion and model-free models is hence quite complex. Using set theory, the entirety of this global problem has been encapsulated by the universal set Ll, and its resolution mathematically formulated as the universal solution Ll. Ever since the original Lipari and Szabo papers the model-free dynamics of a molecule has most often been solved by initially estimating the diffusion tensor. The model-free models which depend on the diffusion parameter values are then optimised and the best model is chosen to represent the dynamics of the residue. Finally, the global model of all diffusion and model-free parameters is optimised. These steps are repeated until convergence. For simplicity this approach to Ll will be labelled the diffusion seeded model-free paradigm. Although this technique suffers from a number of problems many have been solved. All aspects of the diffusion seeded paradigm and its consequences, together with a few alternatives to the paradigm, will be reviewed through the use of set notation."
    authoraddress  = "Department of Biochemistry and Molecular Biology, Bio21 Institute of Biotechnology and Molecular Science, University of Melbourne, Parkville, Melbourne, Victoria 3010, Australia."
    keywords       = "Magnetic Resonance Spectroscopy/*methods ; *Models, Theoretical ; Proteins/chemistry ; Thermodynamics"
    doi            = "10.1039/b702202f"
    pubmed_id      = 17579774
    status         = "published"
    year           = 2007



class dAuvergneGooley08a(Ref):
    """Bibliography container."""

    type           = "journal"
    author         = "d'Auvergne, E. J. and Gooley, P. R."
    author2        = [["Edward", "d'Auvergne", "E.", "J."], ["Paul", "Gooley", "P.", "R."]]
    title          = "Optimisation of NMR dynamic models I. Minimisation algorithms and their performance within the model-free and Brownian rotational diffusion spaces."
    journal        = "J. Biomol. NMR"
    journal_full   = "Journal of Biomolecular NMR"
    volume         = "40"
    number         = "2"
    pages          = "107-119"
    abstract       = "The key to obtaining the model-free description of the dynamics of a macromolecule is the optimisation of the model-free and Brownian rotational diffusion parameters using the collected R (1), R (2) and steady-state NOE relaxation data. The problem of optimising the chi-squared value is often assumed to be trivial, however, the long chain of dependencies required for its calculation complicates the model-free chi-squared space. Convolutions are induced by the Lorentzian form of the spectral density functions, the linear recombinations of certain spectral density values to obtain the relaxation rates, the calculation of the NOE using the ratio of two of these rates, and finally the quadratic form of the chi-squared equation itself. Two major topological features of the model-free space complicate optimisation. The first is a long, shallow valley which commences at infinite correlation times and gradually approaches the minimum. The most severe convolution occurs for motions on two timescales in which the minimum is often located at the end of a long, deep, curved tunnel or multidimensional valley through the space. A large number of optimisation algorithms will be investigated and their performance compared to determine which techniques are suitable for use in model-free analysis. Local optimisation algorithms will be shown to be sufficient for minimisation not only within the model-free space but also for the minimisation of the Brownian rotational diffusion tensor. In addition the performance of the programs Modelfree and Dasha are investigated. A number of model-free optimisation failures were identified: the inability to slide along the limits, the singular matrix failure of the Levenberg-Marquardt minimisation algorithm, the low precision of both programs, and a bug in Modelfree. Significantly, the singular matrix failure of the Levenberg-Marquardt algorithm occurs when internal correlation times are undefined and is greatly amplified in model-free analysis by both the grid search and constraint algorithms. The program relax ( http://www.nmr-relax.com ) is also presented as a new software package designed for the analysis of macromolecular dynamics through the use of NMR relaxation data and which alleviates all of the problems inherent within model-free analysis."
    authoraddress  = "Department of NMR-based Structural Biology, Max Planck Institute for Biophysical Chemistry, Am Fassberg 11, D-37077, Goettingen, Germany"
    keywords       = "*Algorithms ; Cytochromes c2/chemistry ; Diffusion ; *Models, Molecular ; Nuclear Magnetic Resonance, Biomolecular/*methods ; Rhodobacter capsulatus/chemistry ; *Rotation"
    doi            = "10.1007/s10858-007-9214-2"
    pubmed_id      = 18085410
    status         = "published"
    year           = 2008



class dAuvergneGooley08b(Ref):
    """Bibliography container."""

    type           = "journal"
    author         = "d'Auvergne, E. J. and Gooley, P. R."
    author2        = [["Edward", "d'Auvergne", "E.", "J."], ["Paul", "Gooley", "P.", "R."]]
    title          = "Optimisation of NMR dynamic models II. A new methodology for the dual optimisation of the model-free parameters and the Brownian rotational diffusion tensor."
    journal        = "J. Biomol. NMR"
    journal_full   = "Journal of Biomolecular NMR"
    volume         = "40"
    number         = "2"
    pages          = "121-133"
    abstract       = "Finding the dynamics of an entire macromolecule is a complex problem as the model-free parameter values are intricately linked to the Brownian rotational diffusion of the molecule, mathematically through the autocorrelation function of the motion and statistically through model selection. The solution to this problem was formulated using set theory as an element of the universal set [formula: see text]-the union of all model-free spaces (d'Auvergne EJ and Gooley PR (2007) Mol. BioSyst. 3(7), 483-494). The current procedure commonly used to find the universal solution is to initially estimate the diffusion tensor parameters, to optimise the model-free parameters of numerous models, and then to choose the best model via model selection. The global model is then optimised and the procedure repeated until convergence. In this paper a new methodology is presented which takes a different approach to this diffusion seeded model-free paradigm. Rather than starting with the diffusion tensor this iterative protocol begins by optimising the model-free parameters in the absence of any global model parameters, selecting between all the model-free models, and finally optimising the diffusion tensor. The new model-free optimisation protocol will be validated using synthetic data from Schurr JM et al. (1994) J. Magn. Reson. B 105(3), 211-224 and the relaxation data of the bacteriorhodopsin (1-36)BR fragment from Orekhov VY (1999) J. Biomol. NMR 14(4), 345-356. To demonstrate the importance of this new procedure the NMR relaxation data of the Olfactory Marker Protein (OMP) of Gitti R et al. (2005) Biochem. 44(28), 9673-9679 is reanalysed. The result is that the dynamics for certain secondary structural elements is very different from those originally reported."
    authoraddress  = "Department of NMR-based Structural Biology, Max Planck Institute for Biophysical Chemistry, Am Fassberg 11, Goettingen, D-37077, Germany"
    keywords       = "Algorithms ; Amides/chemistry ; Bacteriorhodopsins/chemistry ; Crystallography, X-Ray ; Diffusion ; *Models, Molecular ; Nuclear Magnetic Resonance, Biomolecular/*methods ; Olfactory Marker Protein/chemistry ; Peptide Fragments/chemistry ; Protein Structure, Secondary ; *Rotation"
    language       = "eng"
    doi            = "10.1007/s10858-007-9213-3"
    pubmed_id      = 18085411
    status         = "published"
    year           = 2008



class Delaglio95(Ref):
    """Bibliography container."""

    type            = "journal"
    author          = "Delaglio, F., Grzesiek, S., Vuister, G.W., Zhu, G., Pfeifer, J. and Bax, A."
    author2         = [["Frank", "Delaglio", "F.", None], ["Stephan", "Grzesiek", "S.", None], ["Geerten", "Vuister", "G.", "W."], ["Guang", "Zhu", "G.", None], ["John", "Pfeifer", "J.", None], ["Ad", "Bax", "A.", None]]
    title           = "NMRPipe: a multidimensional spectral processing system based on UNIX pipes."
    journal         = "J. Biomol. NMR"
    journal_full    = "Journal of Biomolecular NMR"
    volume          = "6"
    number          = "3"
    pages           = "277-293"
    abstract        = "The NMRPipe system is a UNIX software environment of processing, graphics, and analysis tools designed to meet current routine and research-oriented multidimensional processing requirements, and to anticipate and accommodate future demands and developments. The system is based on UNIX pipes, which allow programs running simultaneously to exchange streams of data under user control. In an NMRPipe processing scheme, a stream of spectral data flows through a pipeline of processing programs, each of which performs one component of the overall scheme, such as Fourier transformation or linear prediction. Complete multidimensional processing schemes are constructed as simple UNIX shell scripts. The processing modules themselves maintain and exploit accurate records of data sizes, detection modes, and calibration information in all dimensions, so that schemes can be constructed without the need to explicitly define or anticipate data sizes or storage details of real and imaginary channels during processing. The asynchronous pipeline scheme provides other substantial advantages, including high flexibility, favorable processing speeds, choice of both all-in-memory and disk-bound processing, easy adaptation to different data formats, simpler software development and maintenance, and the ability to distribute processing tasks on multi-CPU computers and computer networks."
    authoraddress   = "Laboratory of Chemical Physics, National Institute of Diabetes and Digestive and Kidney Diseases, National Institutes of Health, Bethesda, MD 20892, USA."
    keywords        = "Magnetic Resonance Spectroscopy/*instrumentation ; *Software"
    language        = "eng"
    doi             = "10.1007/BF00197809"
    pubmed_id       = 8520220
    status         = "published"
    year            = 1995



class GoddardKneller(Ref):
    """Bibliography container."""

    author          = "Goddard, T.D. and Kneller, D.G."
    author2         = [["Tom", "Goddard", "T.", "D."], ["Donald", "Kneller", "D.", "G."]]
    journal         = "University of California, San Francisco."
    title           = "Sparky 3."
    status          = "unpublished"
    type            = "internet"



class LipariSzabo82a(Ref):
    """Bibliography container."""

    type           = "journal"
    author         = "Lipari, G. and Szabo, A."
    title          = "Model-free approach to the interpretation of nuclear magnetic-resonance relaxation in macromolecules I. Theory and range of validity"
    journal        = "J. Am. Chem. Soc."
    journal_full   = "Journal of the American Chemical Society"
    volume         = "104"
    number         = "17"
    pages          = "4546-4559"
    authoraddress  = "NIADDKD,Chem Phys Lab,Bethesda,MD 20205."
    sourceid       = "ISI:A1982PC82900009"
    status         = "published"
    year           = 1982



class LipariSzabo82b(Ref):
    """Bibliography container."""

    type           = "journal"
    author         = "Lipari, G. and Szabo, A."
    title          = "Model-free approach to the interpretation of nuclear magnetic-resonance relaxation in macromolecules II. Analysis of experimental results"
    journal        = "J. Am. Chem. Soc."
    journal_full   = "Journal of the American Chemical Society"
    volume         = "104"
    number         = "17"
    pages          = "4559-4570"
    abstract       = "For pt.I see ibid., vol.104, p.4546 (1982). In the preceding paper it has been shown that the unique dynamic information on fast internal motions in an NMR relaxation experiment on macromolecules in solution is specified by a generalized order parameter, S , and an effective correlation time, tau /sub e/. The authors now deal with the extraction and interpretation of this information. The procedure used to obtain S /sup 2/ and tau /sub e/ from experimental data by using a least-squares method and, in certain favorable circumstances, by using an analytical formula is described. A variety of experiments are then analyzed to yield information on the time scale and spatial restriction of internal motions of isoleucines in myoglobin, methionines in dihydrofolate reductase and myoglobin, a number of aliphatic residues in basic pancreatic trypsin inhibitor, and ethyl isocyanide bound to myoglobin, hemoglobin, and aliphatic side chains in three random-coil polymers. The numerical values of S /sup 2/ and tau /sub e / can be readily interpreted within the framework of a variety of models."
    authoraddress  = "NIADDKD,Chem Phys Lab,Bethesda,MD 20205."
    sourceid       = "ISI:A1982PC82900010"
    status         = "published"
    year           = 1982
