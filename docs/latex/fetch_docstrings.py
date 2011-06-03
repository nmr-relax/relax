#! /usr/bin/python

###############################################################################
#                                                                             #
# Copyright (C) 2005-2010 Edward d'Auvergne                                   #
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

# Python module imports.
from inspect import formatargspec, getargspec, getdoc
from re import match, search
from string import letters, lowercase, lstrip, punctuation, replace, rstrip, split, upper, whitespace
import sys

# Add the path to the relax base directory.
sys.path.append(sys.path[0])
sys.path[0] = '../..'

# Import the program relax.
from prompt.interpreter import Interpreter


class Fetch_docstrings:
    def __init__(self, file='docstring.tex'):
        """Fetch all the docstrings of the user functions and format them LaTeX style."""

        # Some dummy data structures.
        self.script_file = None
        self.intro_string = ''
        self.dummy_mode = 1

        # Global data structures.
        self.table_count = 1

        # Initialise the interpreter!
        interpreter = Interpreter(self)

        # Get the blacklisted objects.
        self.get_blacklist()

        # Open the LaTeX file.
        self.file = open(file, 'w')

        # Get the names of the data structures.
        names = sorted(interpreter._locals.keys())

        # Alphabetically sort the names of the data structures.
        for name in names:
            # Skip the name if it is in the blacklist.
            if name in self.blacklist:
                continue

            # Get the object.
            object = interpreter._locals[name]

            # Determine if the structure is user function containing class.
            if hasattr(object, '__relax_help__'):
                # Document the user class.
                self.doc_user_class(name, object)
                continue

            # Skip the object if there is no docstring.
            if not hasattr(object, '__doc__') or not object.__doc__:
                continue

            # Print the docstring.
            self.parse_docstring(name, object)

        # Close the LaTeX file.
        self.file.close()


    def break_functions(self, text):
        """Allow the function text to be broken nicely across lines.

        The '\' character will be added later by the latex_special_chars() method.
        """

        # Allow line breaks after the opening bracket.
        text = replace(text, "(", "(linebreak[0]")

        # Allow line breaks after periods (but not in numbers).
        for char in letters:
            text = replace(text, ".%s" % char, ".linebreak[0]%s" % char)

        # Allow line breaks after equal signs.
        text = replace(text, "=", "=linebreak[0]")

        # Return the modified text.
        return text


    def doc_user_class(self, parent_name, parent_object):
        """Document the user class."""

        # Get the names of the data structures.
        names = sorted(dir(parent_object))

        # Alphabetically sort the names of the data structures.
        for name in names:
            # Skip names begining with an underscore.
            if search('^_', name):
                continue

            # Get the object.
            object = getattr(parent_object, name)

            # Skip the object if there is no docstring.
            if not hasattr(object, '__doc__') or not object.__doc__:
                continue

            # Print the docstring.
            self.parse_docstring(parent_name + '.' + name, object)


    def get_blacklist(self):
        """Maintained list of objects in the interpreter namespace which should not be documented."""

        # Initialise the list.
        self.blacklist = []

        # Skip these.
        self.blacklist.append('pi')
        self.blacklist.append('script')


    def indexing(self, index, bold=0):
        """Function of inserting index marks into the text."""

        # End string.
        if bold:
            end_string = '|textbf}'
        else:
            end_string = '}'

        # Loop over the indices.
        for i in xrange(len(self.entries)):
            # Find triple word entries.
            if index+2 < len(self.words) and self.entries[i][2] == 3 and search(self.entries[i][0], self.words[index] + ' ' + self.words[index+1] + ' ' + self.words[index+2]):
                self.words[index] = self.words[index] + '\\index{' + self.entries[i][1] + end_string

            # Find double word entries.
            elif index+1 < len(self.words) and self.entries[i][2] == 2 and search(self.entries[i][0], self.words[index] + ' ' + self.words[index+1]):
                self.words[index] = self.words[index] + '\\index{' + self.entries[i][1] + end_string

            # Find single word entries.
            elif self.entries[i][2] == 1 and search(self.entries[i][0], self.words[index]):
                self.words[index] = self.words[index] + '\\index{' + self.entries[i][1] + end_string


    def index_entries(self):
        """Function for returning a data structure containing all words which should be indexed."""

        # Initialise.
        self.entries = []

        # The index entries (where to index and the index name).
        ########################################################

        self.entries.append(['AIC', 'model selection!AIC'])
        self.entries.append(['AICc', 'model selection!AICc'])
        self.entries.append(['angle', 'angles'])
        self.entries.append(['anisotropic', 'diffusion!anisotropic'])
        self.entries.append(['ANOVA', 'model selection!ANOVA'])
        self.entries.append(['asymmetric', 'diffusion!ellipsoid (asymmetric)'])
        self.entries.append(['axially symmetric', 'diffusion!spheroid (axially symmetric)'])

        self.entries.append(['BIC', 'model selection!BIC'])
        self.entries.append(['BFGS', 'minimisation techniques!BFGS'])
        self.entries.append(['bond length', 'bond length'])
        self.entries.append(['bootstrap', 'model selection!bootstrap'])
        self.entries.append(['bound', 'parameter!bounds'])
        self.entries.append(['Brownian', 'diffusion!Brownian'])
        self.entries.append(['bzip2', 'compression!bzip2'])

        self.entries.append(['cauchy', 'minimisation techniques!Cauchy point'])
        self.entries.append(['CG-Steihaug', 'minimisation techniques!CG-Steihaug'])
        self.entries.append(['chemical exchange', 'chemical exchange'])
        self.entries.append(['chi-squared', 'chi-squared'])
        self.entries.append(['compression', 'compression'])
        self.entries.append(['conjugate gradient', 'minimisation techniques!conjugate gradient'])
        self.entries.append(['constraint', 'constraint'])
        self.entries.append(['copy', 'copy'])
        self.entries.append(['correlation time', 'correlation time'])
        self.entries.append(['cross-validation', 'model selection!cross-validation'])

        self.entries.append(['dasha', 'software!Dasha'])
        self.entries.append(['Dasha', 'software!Dasha'])
        self.entries.append(['delete', 'delete'])
        self.entries.append(['diffusion tensor', 'diffusion!tensor'])
        self.entries.append(['display', 'display'])
        self.entries.append(['dogleg', 'minimisation techniques!dogleg'])

        self.entries.append(['eigenvalue', 'eigenvalues'])
        self.entries.append(['elimination', 'model elimination'])
        self.entries.append(['ellipsoid', 'diffusion!ellipsoid (asymmetric)'])
        self.entries.append(['Euler angle', 'Euler angles'])
        self.entries.append(['exact trust region', 'minimisation techniques!exact trust region'])

        self.entries.append(['Fletcher-Reeves', 'minimisation techniques!Fletcher-Reeves'])
        self.entries.append(['floating point', 'floating point number'])

        self.entries.append(['grace', 'software!Grace'])
        self.entries.append(['Grace', 'software!Grace'])
        self.entries.append(['gzip', 'compression!gzip'])

        self.entries.append(['Hestenes-Stiefel', 'minimisation techniques!Hestenes-Stiefel'])
        self.entries.append(['hypothesis testing', 'model selection!hypothesis testing'])

        self.entries.append(['isotropic', 'diffusion!sphere (isotropic)'])

        self.entries.append(['Levenberg-Marquardt', 'minimisation techniques!Levenberg-Marquardt'])
        self.entries.append(['limit', 'parameter!limit'])

        self.entries.append(['map', 'map'])
        self.entries.append(['method of [Mm]ultipliers', 'minimisation techniques!Method of Multipliers'])
        self.entries.append(['minimise', 'minimisation'])
        self.entries.append(['minimisation', 'minimisation'])
        self.entries.append(['model elimination', 'model elimination'])
        self.entries.append(['modelfree4', 'software!Modelfree'])
        self.entries.append(['Modelfree4', 'software!Modelfree'])
        self.entries.append(['modelling', 'modelling'])
        self.entries.append(['molecule', 'molecule'])
        self.entries.append(['molmol', 'software!MOLMOL'])
        self.entries.append(['Molmol', 'software!MOLMOL'])

        self.entries.append(['opendx', 'software!OpenDX'])
        self.entries.append(['OpenDX', 'software!OpenDX'])
        self.entries.append(['optimise', 'optimise'])
        self.entries.append(['order parameter', 'order parameter'])

        self.entries.append(['newton', 'minimisation techniques!Newton'])
        self.entries.append(['newton-CG', 'minimisation techniques!Newton conjugate gradient'])
        self.entries.append(['NMR', 'NMR'])

        self.entries.append(['PDB', 'PDB'])
        self.entries.append(['Polak-Ribi.*re', 'minimisation techniques!Polak-Ribiere@Polak-Ribi\`ere'])
        self.entries.append(['Polak-Ribi.*re +', 'minimisation techniques!Polak-Ribiere@Polak-Ribi\`ere +'])
        self.entries.append(['plot', 'plot'])
        self.entries.append(['python', 'Python'])

        self.entries.append(['read', 'read'])
        self.entries.append(['regular expression', 'regular expression'])
        self.entries.append(['relaxation', 'relaxation'])
        self.entries.append(['rotation', 'rotation'])

        self.entries.append(['sequence', 'sequence'])
        self.entries.append(['script', 'scripting!script file'])
        self.entries.append(['scripting', 'scripting'])
        self.entries.append(['simplex', 'minimisation techniques!simplex'])
        self.entries.append(['sphere', 'diffusion!sphere (isotropic)'])
        self.entries.append(['spheroid', 'diffusion!spheroid (axially symmetric)'])
        self.entries.append(['sparky', 'software!Sparky'])
        self.entries.append(['Sparky', 'software!Sparky'])
        self.entries.append(['steepest descent', 'minimisation techniques!steepest descent'])

        self.entries.append(['tar', 'tar'])

        self.entries.append(['uncompressed', 'compression!uncompressed'])

        self.entries.append(['write', 'write'])

        self.entries.append(['xeasy', 'software!XEasy'])
        self.entries.append(['Xeasy', 'software!XEasy'])
        self.entries.append(['XEasy', 'software!XEasy'])

        # Modifications.
        for i in xrange(len(self.entries)):
            # Count the number of words.
            self.entries[i].append(len(split(self.entries[i][0], ' ')))

            # Accept capitalisation.
            if search(self.entries[i][0][0], lowercase):
                self.entries[i][0] = '[' + upper(self.entries[i][0][0]) + self.entries[i][0][0] + ']' + self.entries[i][0][1:]

            # Add a carrot to the start of the match string.
            self.entries[i][0] = '^' + self.entries[i][0]

            # Reverse the subarray in prepartion for sorting.
            self.entries[i].reverse()

        # Reverse sort by word count.
        self.entries.sort(reverse=1)
        for i in xrange(len(self.entries)):
            self.entries[i].reverse()


    def keywords(self):
        """Change the keyword label to bold sans serif font."""

        # Initialise.
        string = ''

        # Loop until the end of the verbatim section.
        while True:
            # End of the keywords section (go to the next line then break).
            if self.i+1 > len(self.docstring_lines) or (self.docstring_lines[self.i] == '' and self.docstring_lines[self.i+1] == ''):
                self.i = self.i + 1
                break

            # Empty line.
            if self.docstring_lines[self.i] == '':
                string = string + ' \n '

            # Continuation of an example.
            else:
                string = string + self.docstring_lines[self.i] + ' '

            # Increment the line counter.
            self.i = self.i + 1

        # Add the sting to the verbatim section.
        self.section.append(string)
        self.section_type.append('keywords')


    def latex_formatting(self, string):
        """Function for handling LaTeX maths environments."""

        # Angstrom.
        string = self.safe_replacement(string, 'Angstroms', '\AA')
        string = self.safe_replacement(string, 'Angstrom', '\AA')

        # Pi.
        string = self.safe_replacement(string, 'pi', '$\pi$')

        # Less than.
        string = replace(string, ' < ', ' $<$ ')

        # Less than or equal.
        string = replace(string, ' <= ', ' $\le$ ')

        # Much less than.
        string = replace(string, ' << ', ' $<<$ ')

        # Greater than.
        string = replace(string, ' > ', ' $>$ ')

        # Greater than or equal.
        string = replace(string, ' >= ', ' $\ge$ ')

        # Much greater than.
        string = replace(string, ' >> ', ' $>>$ ')

        # 1st, 2nd, etc.
        string = replace(string, '1st', '1$^\mathrm{st}$')
        string = replace(string, '2nd', '2$^\mathrm{nd}$')
        string = replace(string, '3rd', '3$^\mathrm{rd}$')
        string = replace(string, '4th', '4$^\mathrm{th}$')
        string = replace(string, '5th', '5$^\mathrm{th}$')
        string = replace(string, '6th', '6$^\mathrm{th}$')
        string = replace(string, '7th', '7$^\mathrm{th}$')
        string = replace(string, '8th', '8$^\mathrm{th}$')
        string = replace(string, '9th', '9$^\mathrm{th}$')
        string = replace(string, '0th', '0$^\mathrm{th}$')
        string = replace(string, '1th', '1$^\mathrm{th}$')
        string = replace(string, '2th', '2$^\mathrm{th}$')
        string = replace(string, '3th', '3$^\mathrm{th}$')


        # Relaxation data.
        ##################

        # R1 and R2.
        string = self.safe_replacement(string, 'R1', 'R$_1$')
        string = self.safe_replacement(string, 'R2', 'R$_2$')


        # Model-free parameters.
        ########################

        # S2f, S2s, S2, te, ts, tf, tm, Rex, r.
        string = self.safe_replacement(string, 'S2f', '$S^2_f$')
        string = self.safe_replacement(string, 'S2s', '$S^2_s$')
        string = self.safe_replacement(string, 'S2', '$S^2$')
        string = self.safe_replacement(string, 'te', '$\\tau_e$')
        string = self.safe_replacement(string, 'ts', '$\\tau_s$')
        string = self.safe_replacement(string, 'tf', '$\\tau_f$')
        string = self.safe_replacement(string, 'tm', '$\\tau_m$')
        string = self.safe_replacement(string, 'Rex', '$R_{ex}$')
        string = self.safe_replacement(string, 'r', '$r$')
        string = self.safe_replacement(string, '<r>', '$<$$r$$>$')


        # Spectral densities.
        #####################

        # J(w), J(0), J(wX), J(wH).
        string = replace(string, 'J(w)', '$J(\omega)$')
        string = replace(string, 'J(0)', '$J(0)$')
        string = replace(string, 'J(wX)', '$J(\omega_X)$')
        string = replace(string, 'J(wH)', '$J(\omega_H)$')


        # Diffusion tensor parameters.
        ##############################

        # Diso, Da, Dr, Dx, Dy, Dz, Dpar, Dper, Dratio.
        string = self.safe_replacement(string, 'Diso', '$\Diff_{iso}$')
        string = self.safe_replacement(string, 'Da', '$\Diff_a$')
        string = self.safe_replacement(string, 'Dr', '$\Diff_r$')
        string = self.safe_replacement(string, 'R', '$\mathfrak{R}$')
        string = self.safe_replacement(string, 'Dx', '$\Diff_x$')
        string = self.safe_replacement(string, 'Dy', '$\Diff_y$')
        string = self.safe_replacement(string, 'Dz', '$\Diff_z$')
        string = self.safe_replacement(string, 'Dpar', '$\Diff_\Par$')
        string = self.safe_replacement(string, 'Dper', '$\Diff_\Per$')
        string = self.safe_replacement(string, 'Dratio', '$\Diff_{ratio}$')


        # Angles.
        #########

        # alpha, beta, gamma, theta, phi.
        string = self.safe_replacement(string, 'alpha', '$\\alpha$')
        string = self.safe_replacement(string, 'beta', '$\\beta$')
        string = self.safe_replacement(string, 'gamma', '$\\gamma$')
        string = self.safe_replacement(string, 'theta', '$\\theta$')
        string = self.safe_replacement(string, 'phi', '$\\phi$')


        # Direction cosines.
        ####################

        # delta_x, delta_y, delta_z.
        string = self.safe_replacement(string, 'dx', '$\\delta_x$')
        string = self.safe_replacement(string, 'dy', '$\\delta_y$')
        string = self.safe_replacement(string, 'dz', '$\\delta_z$')


        # Indices.
        ##########

        # i, j, k, l, m, n, x, y, z, A, b, u.
        string = self.safe_replacement(string, 'i', '$i$')
        string = self.safe_replacement(string, 'j', '$j$')
        string = self.safe_replacement(string, 'k', '$k$')
        string = self.safe_replacement(string, 'l', '$l$')
        string = self.safe_replacement(string, 'm', '$m$')
        string = self.safe_replacement(string, 'n', '$n$')
        string = self.safe_replacement(string, 'x', '$x$')
        string = self.safe_replacement(string, 'y', '$y$')
        string = self.safe_replacement(string, 'z', '$z$')
        string = self.safe_replacement(string, 'b', '$b$')
        string = self.safe_replacement(string, 'u', '$u$')


        # Misc.
        #######

        # tau.
        string = self.safe_replacement(string, 'tau', '$\\tau$')

        # Polak-Ribi\`ere.
        string = self.safe_replacement(string, 'Polak-Ribiere', 'Polak-Ribi\`ere')


        # Return the new text.
        return string


    def latex_quotes(self, string):
        """Function for changing the quotes for LaTeX processing."""

        # Initialise.
        new_string = ''
        in_quote = 0

        # Loop over the characters.
        for i in xrange(len(string)):
            # Find the quote marks.
            if search('\'', string[i]):
                # Swap the opening ' with `.
                if not in_quote and (i == 0 or not search('[a-z]', string[i-1])):
                    new_string = new_string + '`'
                    in_quote = 1
                    continue

                # Just exited the quote
                else:
                    in_quote = 0

            # Append the character.
            new_string = new_string + string[i]

        return new_string


    def latex_special_chars(self, string):
        """Function for handling LaTeX special characters."""

        # Damned backslashes.
        string = replace(string, '\\', 'This is a backslash to be replaced at the end of this functioN')

        # List of special characters (prefix a backslash).
        for char in "#$%&_{}":
            string = replace(string, char, '\\'+char)

        # Doubly special characters (prefix a backslash and postfix '{}').
        for char in "^~":
            string = replace(string, char, '\\'+char+'{}')

        # Damned backslashes!
        string = replace(string, 'This is a backslash to be replaced at the end of this functioN', '$\\backslash$')

        # Add a backslash to where it really should be.
        string = replace(string, 'linebreak[0]', '\linebreak[0]')

        # Return the new text.
        return string


    def lists(self):
        """Function for creating LaTeX lists."""

        # Initialise.
        string = lstrip(self.docstring_lines[self.i])

        # Determine the element spacing.
        j = self.i
        while True:
            # Walk to the next line.
            j = j + 1

            # No more lines.
            if len(self.docstring_lines) <= j:
                list_spacing = 0
                break

            # Find the empty line.
            if len(self.docstring_lines[j]) == 0:
                # No more lines.
                if len(self.docstring_lines) <= j+1:
                    list_spacing = 0

                # Determine if the next line is an element of the list.
                elif search('^ ', self.docstring_lines[j+1]):
                    list_spacing = 1

                # or not.
                else:
                    list_spacing = 0

                # All done.
                break

        # Non-spaced list.
        if not list_spacing:
            # New line character.
            string = string + ' \n '

            # Loop until the end of the list.
            while True:
                # Increment the line counter.
                self.i = self.i + 1

                # End of a non-spaced list.
                if self.i >= len(self.docstring_lines) or len(self.docstring_lines[self.i]) == 0:
                    break

                # Add the next line.
                string = string + lstrip(self.docstring_lines[self.i]) + ' \n '

        # Spaced list.
        else:
            # Loop until the end of the list.
            while True:
                # Increment the line counter.
                self.i = self.i + 1

                # No more lines.
                if self.i >= len(self.docstring_lines):
                    break

                # Empty line.
                if len(self.docstring_lines[self.i]) == 0:
                    # New line character.
                    string = string + ' \n '

                    # Go to the next line.
                    continue

                # End of the list.
                if self.i >= len(self.docstring_lines) or not search('^ ', (self.docstring_lines[self.i])):
                    break

                # Add the next line.
                string = string + ' ' + lstrip(self.docstring_lines[self.i])

        # Walk back one line.
        self.i = self.i - 1

        # Add the sting to the list section.
        self.section.append(string)
        self.section_type.append('list')


    def num_to_text(self, num):
        """Convert the number to text.
        @param num: The number to convert.
        @type num:  int
        @return:    The number in the format of 'First', 'Second', 'Third', etc.
        @rtype:     str
        """

        # The list.
        list = ['First',
                'Second',
                'Third',
                'Fourth',
                'Fifth',
                'Sixth',
                'Seventh',
                'Eighth',
                'Ninth',
                'Tenth',
                'Eleventh',
                'Twelfth'
        ]

        # Convert.
        return list[num-1]


    def paragraph(self):
        """Function for extracting the paragraphs from the docstring."""

        # Initialise.
        string = self.docstring_lines[self.i]

        # Loop until the end of the paragraph.
        while True:
            # Increment the line counter.
            self.i = self.i + 1

            # No more lines.
            if self.i >= len(self.docstring_lines):
                break

            # Empty line.
            if len(self.docstring_lines[self.i]) == 0:
                break

            # Start of table.
            if search('^___', self.docstring_lines[self.i]):
                break

            # Start of list.
            if search('^ ', self.docstring_lines[self.i]):
                break

            # Add the next line.
            string = string + ' ' + self.docstring_lines[self.i]

        # Walk back one line.
        self.i = self.i - 1

        # Add the sting to the verbatim section.
        self.section.append(string)
        self.section_type.append('paragraph')


    def parse_docstring(self, function, object):
        """Function for creating the LaTeX file."""

        # Initialise.
        #############

        # Print the function name to sys.stdout
        sys.stdout.write("User function: %s().\n" % function)

        # Get the docstring.
        docstring = getdoc(object)

        # Split the docstring by newline characters.
        self.docstring_lines = split(docstring, "\n")

        # The section and section_type arrays.
        self.section = []
        self.section_type = []


        # Function name.
        ################

        self.section.append(function)
        self.section_type.append('subsection')


        # Synopsis.
        ###########

        # Heading.
        self.section.append('Synopsis')
        self.section_type.append('subsubsection')

        # The synopsis.
        self.section.append(self.docstring_lines[0])
        self.section_type.append('paragraph')


        # Arguments.
        ############

        # Heading.
        self.section.append('Defaults')
        self.section_type.append('subsubsection')

        # Get the arguments.
        args, varargs, varkw, defaults = getargspec(object)

        # Format the arguments.
        arguments = formatargspec(args, varargs, varkw, defaults)

        # The string.
        self.section.append(arguments)
        self.section_type.append('arguments')


        # First level parsing - sectioning.
        ###################################

        # Loop over the lines.
        self.i = 1     # Skip the first two lines (synopsis and blank line).
        while True:
            # Increment the line number.
            self.i = self.i + 1

            # End.
            if self.i >= len(self.docstring_lines):
                break

            # Strip any whitespace from the end of the line (including newline characters).
            self.docstring_lines[self.i] = rstrip(self.docstring_lines[self.i])

            # Skip the out of section empty lines.
            if self.docstring_lines[self.i] == '':
                continue

            # Find the docstring sections.
            if self.i+1 < len(self.docstring_lines) and search('^~~~', self.docstring_lines[self.i+1]):
                # Title.
                self.section_title = self.docstring_lines[self.i]
                self.section.append(self.docstring_lines[self.i])
                self.section_type.append('subsubsection')

                # Skip the title line, tilde line, and first blank line.
                self.i = self.i + 2
                continue

            # Format the 'Keyword Arguements' section.
            if search('^Keyword ', self.section_title):
                self.keywords()

            # Verbatim section.
            elif search('---', self.docstring_lines[self.i]):
                self.verbatim()

            # relax> or '$ ...' example lines.
            elif search('^relax>', self.docstring_lines[self.i]) or search('^\$ ', self.docstring_lines[self.i]):
                self.relax_examples()

            # Tables.
            elif search('^___', self.docstring_lines[self.i]):
                self.tables()

            # Lists.
            elif search('^ ', self.docstring_lines[self.i]):
                self.lists()

            # Normal paragraphs.
            else:
                self.paragraph()



        # Low level parse - formatting.
        ###############################

        # Get the words to index.
        self.index_entries()

        # Loop over the sections.
        for i in xrange(len(self.section)):
            # The section type alias.
            st = self.section_type[i]

            # Allow breaking and translate to LaTeX quotation marks.
            if st == 'arguments' or st == 'example':
                self.section[i] = self.break_functions(self.section[i])
                self.section[i] = self.latex_quotes(self.section[i])

            # Handle the special LaTeX characters.
            if not st == 'verbatim':
                self.section[i] = self.latex_special_chars(self.section[i])

            # LaTeX formatting.
            if not st == 'arguments' and not st == 'verbatim' and not st == 'example' and not st == 'subsection':
                self.section[i] = self.latex_formatting(self.section[i])

            # Word by word formatting.
            if not st == 'arguments' and not st == 'verbatim' and not st == 'example':
                # Split the string.
                self.words = split(self.section[i], ' ')

                # Initialise.
                self.in_quote = 0

                # Loop over the words one by one.
                for j in xrange(len(self.words)):
                    # Indexing.
                    if st == 'subsection' or st == 'subsubsection':
                        self.indexing(j, bold=1)
                    else:
                        self.indexing(j, bold=0)

                    # Quotes.
                    self.quotes(j)

                    # Recreate the section string.
                    if j == 0:
                        self.section[i] = self.words[j]
                    else:
                        self.section[i] = self.section[i] + ' ' + self.words[j]


        # Write to file.
        ################

        # List of tables to be formatted using longtable.
        longtable = {"molmol.write": [3],
                     "pymol.write": [2]
        }

        # Some whitespace.
        self.file.write(" \n\n\n")

        # Add a spaced out rule.
        self.file.write(" \\vspace{20pt}\n")
        self.file.write(" \\rule{\columnwidth}{2pt}\n")
        self.file.write(" \\vspace{-30pt}\n")

        # Loop over the data.
        table_sub_count = 1
        for i in xrange(len(self.section)):
            # The section type alias.
            st = self.section_type[i]

            # Subsection.
            if st == 'subsection':
                # Store the user function name.
                user_fn = self.section[i] + '()'

                # Allow for hyphenation.
                user_fn = replace(user_fn, '.', '\-.')
                user_fn = replace(user_fn, '\_', '\-\_')

                # Write out the new subsection.
                self.file.write(" \n\n \\subsection{" + user_fn + "}")

                # Reset the sub table count.
                table_sub_count = 1

            # Subsubsection.
            elif st == 'subsubsection':
                self.file.write(" \n \\subsubsection{" + self.section[i] + "}")

            # Defaults.
            elif st == 'arguments':
                self.file.write("\\begin{flushleft}\n")
                self.file.write("\\textsf{\\textbf{" + self.latex_special_chars(self.break_functions(function)) + "}" + self.section[i] + "}\n")
                self.file.write("\\end{flushleft}\n")

            # Keywords.
            elif st == 'keywords':
                # Split the lines
                lines = split(self.section[i], '\n')

                # Loop over the lines.
                for line in lines:
                    # Split the line.
                    line_elements = split(line, ':')

                    # Don't know what to do with this!
                    if len(line_elements) > 2:
                        sys.stderr.write("Keyword failure in: " + repr(line) + " \n ")
                        sys.exit()

                    # Format the keyword.
                    self.file.write("\\keyword{" + line_elements[0] + ":}" + line_elements[1] + " \n\n ")


            # Verbatim.
            elif st == 'verbatim':
                self.file.write("{\\footnotesize \\begin{verbatim} \n " + self.section[i] + "\\end{verbatim}}")

            # Example.
            elif st == 'example':
                self.file.write("\\example{" + self.section[i] + "}")

            # Tables.
            elif st == 'table':
                # Add a reference.
                self.file.write("(see table~\\ref{table%s}) \n " % self.table_count)

                # Split the lines
                lines = split(self.section[i], '\n')

                # Long table.
                if function in longtable.keys() and table_sub_count in longtable[function]:
                    # Start the longtable environment centred and add the caption and toprule.
                    self.file.write("\\onecolumn\n ")
                    self.file.write("\\begin{center}\n ")
                    self.file.write("\\begin{longtable}{" + (int(lines[0]))*"l" + "}\n\n ")
                    self.file.write("\\caption{%s table for the %s user function.}\n\n " % (self.num_to_text(table_sub_count), user_fn))
                    self.file.write("\\\\\n \\toprule \n ")

                    # Generate the LaTeX headings.
                    elements = split(lines[1], 'SEPARATOR')
                    self.file.write(elements[0])
                    for j in range(1, len(elements)):
                        self.file.write('&' + elements[j])
                    self.file.write(" \\\\\n ")

                    # Add the midrule and bottomrule.
                    self.file.write("\\midrule\n ")
                    self.file.write("\\endhead\n\n ")
                    self.file.write("\\bottomrule\n ")
                    self.file.write("\\endfoot\n\n ")

                    # Label.
                    self.file.write("\\label{table%s}\n\n " % self.table_count)

                    # Loop over the main table lines.
                    for line in lines[2:-1]:
                        # Split columns.
                        elements = split(line, 'SEPARATOR')

                        # Write the columns.
                        self.file.write(elements[0])
                        for j in range(1, len(elements)):
                            self.file.write('&' + elements[j])
                        self.file.write(" \\\\\n ")

                    # Terminate.
                    self.file.write("\\end{longtable}\n ")
                    self.file.write("\\end{center}\n ")
                    self.file.write("\\twocolumn\n ")

                # Normal table.
                else:
                    # Start the centred table.
                    self.file.write("\\begin{table*}\n ")
                    self.file.write("\\begin{scriptsize}\n ")
                    self.file.write("\\begin{center}\n ")

                    # A caption.
                    self.file.write("\\caption{%s table for the %s user function.}\n " % (self.num_to_text(table_sub_count), user_fn))

                    # Start the tabular environment and add the toprule.
                    self.file.write("\\begin{tabular}{" + (int(lines[0]))*"l" + "}\n ")
                    self.file.write("\\toprule\n ")

                    # Generate the LaTeX headings.
                    elements = split(lines[1], 'SEPARATOR')
                    self.file.write(elements[0])
                    for j in range(1, len(elements)):
                        self.file.write('&' + elements[j])
                    self.file.write(" \\\\\n ")

                    # Add the midrule.
                    self.file.write("\\midrule\n ")

                    # Loop over the main table lines.
                    for line in lines[2:-1]:
                        # Split columns.
                        elements = split(line, 'SEPARATOR')

                        # Write the columns.
                        self.file.write(elements[0])
                        for j in range(1, len(elements)):
                            self.file.write('&' + elements[j])
                        self.file.write(" \\\\\n ")

                    # Terminate.
                    self.file.write("\\bottomrule\n ")
                    self.file.write("\\label{table%s}\n " % self.table_count)
                    self.file.write("\\end{tabular}\n ")
                    self.file.write("\\end{center}\n ")
                    self.file.write("\\end{scriptsize}\n ")
                    self.file.write("\\end{table*}\n ")

                # Increment the table counters.
                self.table_count = self.table_count + 1
                table_sub_count = table_sub_count + 1

            # Lists.
            elif st == 'list':
                # Split the lines
                lines = split(self.section[i], '\n')

                # Dump an empty last line.
                if len(lines[-1]) == 0:
                    lines = lines[:-1]

                # Determine the type of list.
                elements = split(lines[0], ':')

                # Badly formatted list.
                if len(elements) > 2:
                    sys.stderr.write("Error: Badly formatted list element.\n")
                    sys.stderr.write("The element is: " + repr(lines[i]) + "\n")
                    sys.exit()

                # Plain list.
                if len(elements) == 1:
                    list_type = 0

                # Formatted list.
                else:
                    list_type = 1

                # Start the list.
                if list_type == 1:
                    self.file.write("\\begin{description} \n ")
                else:
                    self.file.write("\\begin{itemize} \n ")

                # Loop over the lines.
                for j in xrange(len(lines)):
                    # Plain list.
                    if list_type == 0:
                        self.file.write("\\item[] " + lstrip(lines[j]) + ' \n ')

                    # Description.
                    else:
                        # Get the description.
                        elements = split(lines[j], ':')

                        # End of list.
                        if len(elements) != 2:
                            continue

                        # Format the element.
                        self.file.write("\\item[" + lstrip(elements[0]) + " --]" + elements[1] + ' \n ')

                # End of the list.
                if list_type == 1:
                    self.file.write("\\end{description} \n ")
                else:
                    self.file.write("\\end{itemize} \n ")

            # No special formatting.
            else:
                self.file.write(self.section[i] + ' \n ')

            # Add two newlines.
            self.file.write(" \n\n ")


    def quotes(self, index):
        """Function for placing quotes within the quote environment."""

        # Split the word by '.
        elements = split(self.words[index], "'")

        # Single word quote.
        if len(elements) == 3:
            self.words[index] = elements[0] + '\quotecmd{' + elements[1] + '}' + elements[2]

        # Weird quote.
        elif len(elements) > 3:
            sys.stderr.write('Unknown quote: ' + repr(self.words[index]))
            sys.exit()

        # Multiword quote.
        if len(elements) == 2:
            # Start of the quote.
            if not self.in_quote and not search('[a-z]$', elements[0]):
                self.words[index] = elements[0] + '\quotecmd{' + elements[1]
                self.in_quote = 1

            # End of the quote.
            elif self.in_quote:
                self.words[index] = elements[0] + '}' + elements[1]
                self.in_quote = 0


    def relax_examples(self):
        """Use typewriter font for relax examples."""

        # Initialise.
        string = self.docstring_lines[self.i]

        # Loop until the end of the example.
        while True:
            # Increment the line counter.
            self.i = self.i + 1

            # End of the example (jump back one line).
            if self.i >= len(self.docstring_lines) or self.docstring_lines[self.i] == '' or search('^relax>', self.docstring_lines[self.i]) or search('^\$ ', self.docstring_lines[self.i]):
                self.i = self.i - 1
                break

            # Add the line to the example.
            string = string + ' ' + lstrip(self.docstring_lines[self.i])

        # Allow functions to be broken across lines nicely.
        string = self.break_functions(string)

        # Add the sting to the verbatim section.
        self.section.append(string)
        self.section_type.append('example')


    def safe_replacement(self, string, text, latex):
        """Only replace in safe places within the text."""

        # Combos (if only RE could be used!)

        # A number out the front.
        string = replace(string,    '0'+text,           '0'+latex)
        string = replace(string,    '1'+text,           '1'+latex)
        string = replace(string,    '2'+text,           '2'+latex)
        string = replace(string,    '3'+text,           '3'+latex)
        string = replace(string,    '4'+text,           '4'+latex)
        string = replace(string,    '5'+text,           '5'+latex)
        string = replace(string,    '6'+text,           '6'+latex)
        string = replace(string,    '7'+text,           '7'+latex)
        string = replace(string,    '8'+text,           '8'+latex)
        string = replace(string,    '9'+text,           '9'+latex)

        # In a sentence.
        string = replace(string,    ' '+text+',',       ' '+latex+',')
        string = replace(string,    ' '+text+'.',       ' '+latex+'.')
        string = replace(string,    ' '+text+' ',       ' '+latex+' ')
        string = replace(string,    ' '+text+';',       ' '+latex+';')
        string = replace(string,    ' '+text+':',       ' '+latex+':')

        # In lists [].
        string = replace(string,    '['+text+']',       '['+latex+']')
        string = replace(string,    '['+text+' ',       '['+latex+' ')
        string = replace(string,    '['+text+',',       '['+latex+',')
        string = replace(string,    '['+text+';',       '['+latex+';')
        string = replace(string,    ' '+text+']',       ' '+latex+']')

        # In lists ().
        string = replace(string,    '('+text+')',       '('+latex+')')
        string = replace(string,    '('+text+' ',       '('+latex+' ')
        string = replace(string,    '('+text+',',       '('+latex+',')
        string = replace(string,    '('+text+';',       '('+latex+';')
        string = replace(string,    ' '+text+')',       ' '+latex+')')

        # In lists {}.
        string = replace(string,    '{'+text+' ',       '{'+latex+' ')
        string = replace(string,    '{'+text+',',       '{'+latex+',')
        string = replace(string,    '{'+text+';',       '{'+latex+';')
        string = replace(string,    ' '+text+'\\',      ' '+latex+'\\')

        # Quoted.
        string = replace(string,    '`'+text+'\'',      '`'+latex+'\'')
        string = replace(string,    '`'+text+' ',       '`'+latex+' ')
        string = replace(string,    '`'+text+',',       '`'+latex+',')
        string = replace(string,    '`'+text+'.',       '`'+latex+'.')
        string = replace(string,    '`'+text+';',       '`'+latex+';')
        string = replace(string,    ' '+text+'\'',      ' '+latex+'\'')

        # End of the line.
        substring = replace(string[-len(text)-1:],    ' '+text,      ' '+latex)
        string = string[0:-len(text)-1] + substring

        substring = replace(string[-len(text)-1:],    '.'+text,      '.'+latex)
        string = string[0:-len(text)-1] + substring

        string = replace(string,    ' '+text+'\n',      ' '+latex+'\n')
        string = replace(string,    '.'+text+'\n',      '.'+latex+'\n')

        # Maths
        string = replace(string,    ' '+text+'\^',      ' '+latex+'\^')
        string = replace(string,    '('+text+'\^',      '('+latex+'\^')
        string = replace(string,    '\n'+text+'\^',     '\n'+latex+'\^')

        # At the start of the line.
        if search('^'+text+'['+punctuation+']', string) or search('^'+text+'['+whitespace+']', string) or search('\n'+text+'['+punctuation+']', string) or search('\n'+text+'['+whitespace+']', string):
            string = replace(string,    text+' ',           latex+' ')
            string = replace(string,    text+',',           latex+',')
            string = replace(string,    text+'.',           latex+'.')
            string = replace(string,    text+';',           latex+';')
            string = replace(string,    text+']',           latex+']')
            string = replace(string,    text+')',           latex+')')
            string = replace(string,    text+'^',           latex+'^')
            string = replace(string,    text+'\\',          latex+'\\')
            string = replace(string,    text+'\'',          latex+'\'')
            string = replace(string,    text+'\n',          latex+'\n')


        # Return the string.
        return string


    def tables(self):
        """Function for creating LaTeX tables."""

        # Increment the line counter.
        self.i = self.i + 1

        # Count the number of columns.
        num_col = len(split(self.docstring_lines[self.i], '|'))
        string = repr(num_col-2) + ' \n '

        # Not really a table!
        if num_col == 1:
            sys.stderr.write('Not a table!')
            sys.exit()

        # Shift to the next line.
        self.i = self.i + 1

        # Get the headings.
        headings = split(self.docstring_lines[self.i], '|')
        headings = headings[1:-1]
        for j in xrange(len(headings)):
            headings[j] = lstrip(rstrip(headings[j]))

        # Generate the LaTeX headings.
        string = string + headings[0]
        for j in range(1, len(headings)):
            string = string + " SEPARATOR " + headings[j]
        string = string + ' \n '

        # Skip three lines.
        self.i = self.i + 3

        # Go through the table.
        while True:
            # End of the table (go to the next line then break).
            if self.i >= len(self.docstring_lines) or search('^\\|_', self.docstring_lines[self.i]):
                self.i = self.i + 1
                break

            # Split the columns.
            columns = split(self.docstring_lines[self.i], '|')

            # Create the formatted tabular line.
            if len(columns) > 1:
                string = string + lstrip(rstrip(columns[1]))
                for j in range(2, len(columns)-1):
                    string = string + " SEPARATOR " + lstrip(rstrip(columns[j]))
                string = string + ' \n '
            else:
                string = string + columns[0] + ' \n '

            # Increment the line counter.
            self.i = self.i + 1

        # Add the sting to the table section.
        self.section.append(string)
        self.section_type.append('table')


    def verbatim(self):
        """Function for extracting the verbatim docstring section."""

        # Initialise.
        string = ''

        # Loop until the end of the verbatim section.
        while True:
            # Increment the line counter.
            self.i = self.i + 1

            # End of Verbatim (go to the next line then break).
            if self.i >= len(self.docstring_lines) or search('---', self.docstring_lines[self.i]):
                self.i = self.i + 1
                break

            # Add the next line.
            string = string + self.docstring_lines[self.i] + ' \n '

        # Add the sting to the verbatim section.
        self.section.append(string)
        self.section_type.append('verbatim')
