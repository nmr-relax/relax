###############################################################################
#                                                                             #
# Copyright (C) 2005-2013 Edward d'Auvergne                                   #
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
"""User function definition conversion to LaTeX for the relax manual."""

# Python module imports.
from os import sep
from os.path import dirname
from re import search
from string import ascii_letters, ascii_lowercase, punctuation, whitespace
import sys

# Add the path to the relax base directory.
sys.path.append(sys.path[0])
sys.path[0] = '../..'

# relax module imports.
from graphics import fetch_icon
import user_functions
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.data import Uf_tables; uf_tables = Uf_tables()


# Set up the user functions.
user_functions.initialise()


class Fetch_docstrings:
    def __init__(self, file='docstring.tex'):
        """Fetch all the docstrings of the user functions and format them LaTeX style."""

        # Initialise some variables.
        self.in_quote = False
        self.table_count = 1
        self.uf_table_labels = []
        self.path = dirname(file)

        # Set up the words to index.
        self.index_entries()

        # Open the LaTeX file.
        self.file = open(file, 'w')

        # Loop over the user functions.
        uf_names = []
        for self.uf_name, self.uf in uf_info.uf_loop():
            # Add to the list.
            uf_names.append(self.uf_name)
            # The user function class.
            self.uf_class = None
            if search('\.', self.uf_name):
                # Split up the name.
                class_name, uf_name = self.uf_name.split('.')

                # Get the user function class data object.
                self.uf_class = uf_info.get_class(class_name)

            # Reset the table count for each user function.
            self.uf_table_count = 1

            # Printout.
            sys.stdout.write("User function: %s().\n" % self.uf_name)

            # Build and write out the various sections, as needed.
            self.build_uf()
            self.build_synopsis()
            self.build_arg_defaults()
            self.build_kargs()
            self.build_description()

        # Close the LaTeX file.
        self.file.close()

        # Create the relax lstlisting definition.
        self.script_definitions(uf_names)


    def break_functions(self, text):
        """Allow the function text to be broken nicely across lines.

        The '\' character will be added later by the latex_special_chars() method.
        """

        # Allow line breaks after the opening bracket.
        text = text.replace("(", "(\linebreak[0]")

        # Allow line breaks after periods (but not in numbers).
        for char in ascii_letters:
            text = text.replace(".%s" % char, ".\linebreak[0]%s" % char)

        # Allow line breaks after equal signs.
        text = text.replace("=", "=\linebreak[0]")

        # Remove the backslash to prevent is processing.
        text = text.replace("\linebreak", "linebreak")

        # Return the modified text.
        return text


    def build_arg_defaults(self):
        """Create the user function argument default section."""

        # The section heading.
        self.file.write("\subsubsection{Defaults}\n\n")

        # Initialise the text. 
        text = "("

        # The keyword args.
        for i in range(len(self.uf.kargs)):
            # Comma separation.
            if i >= 1:
                text += ", "

            # Add the arg.
            text += "%s=%s" % (self.uf.kargs[i]['name'], repr(self.uf.kargs[i]['default']))

        # The end.
        text += ")"

        # LaTeX formatting.
        text = self.break_functions(text)
        text = self.latex_quotes(text)
        text = self.latex_special_chars(text)

        # Write to file.
        self.file.write("\\begin{flushleft}\n")
        self.file.write("\\textsf{\\textbf{%s}%s}\n" % (self.latex_special_chars(self.break_functions(self.uf_name)), text))
        self.file.write("\\end{flushleft}\n\n\n")


    def build_description(self):
        """Create the user function argument default section."""

        # Loop over the sections.
        for i in range(len(self.uf.desc)):
            # Alias the description.
            desc = self.uf.desc[i]

            # The section heading.
            self.file.write("\subsubsection{%s}\n\n" % desc.get_title())

            # Loop over the documentation elements.
            for type, element in desc.element_loop():
                # A paragraph.
                if type == 'paragraph':
                    self.write_paragraph(element)

                # Verbatim text.
                elif type == 'verbatim':
                    self.write_verbatim(element)

                # A list.
                elif type == 'list':
                    self.write_list(element)

                # An itemised list.
                elif type == 'item list':
                    self.write_item_list(element)

                # A table.
                elif type == 'table':
                    self.write_table(element)

                # A prompt example.
                elif type == 'prompt':
                    self.write_prompt_example(element)



    def build_kargs(self):
        """Create the user function keyword argument section."""

        # No keyword args, so do nothing.
        if not len(self.uf.kargs):
            return

        # The section heading.
        self.file.write("\subsubsection{Keyword arguments}\n\n")

        # The keyword args.
        for i in range(len(self.uf.kargs)):
            # LaTeX formatting.
            arg = self.latex_special_chars(self.uf.kargs[i]['name'])
            text = self.latex_special_chars(self.uf.kargs[i]['desc'])
            text = self.latex_formatting(text)
            text = self.word_formatting(text, bold=False)

            # Write to file.
            self.file.write("\\hspace{3 mm}\\keyword{%s:}  %s\n\n" % (arg, text))

        # Empty line to end with.
        self.file.write("\n")


    def build_synopsis(self):
        """Create the user function synopsis."""

        # The section heading.
        self.file.write("\subsubsection{Synposis}\n\n")

        # The text.
        text = self.uf.title

        # LaTeX formatting.
        text = self.latex_special_chars(text)
        text = self.latex_formatting(text)
        text = self.word_formatting(text, bold=False)

        # Write to file.
        self.file.write(text + '\n\n\n')


    def build_uf(self):
        """Create the user function sectioning."""

        # Some whitespace.
        self.file.write("\n\n")

        # Start a new column for each user function and add a rule to the top.
        self.file.write("\\pagebreak[4]\n")
        self.file.write("\\rule{\columnwidth}{1pt}\n")

        # The title (with less spacing).
        self.file.write("\\vspace{-20pt}\n")
        self.uf_name_latex = self.uf_name

        # LaTeX formatting.
        self.uf_name_latex = self.latex_special_chars(self.uf_name_latex)
        self.uf_name_latex = self.word_formatting(self.uf_name_latex, bold=True)

        # Allow for hyphenation.
        self.uf_name_latex = self.uf_name_latex.replace('.', '\-.')
        self.uf_name_latex = self.uf_name_latex.replace('\_', '\-\_')

        # Write out the title (with label).
        self.file.write("\subsection{%s} \label{uf: %s}\n" % (self.uf_name_latex, self.uf_name))

        # Add the user function class icon.
        if self.uf_class:
            icon = fetch_icon(self.uf_class.gui_icon, size='128x128', format=None)
            if icon:
                self.file.write("\includegraphics[bb=0 0 18 18]{%s} \hfill " % icon)
            else:
                self.file.write("\hfill ")

        # Add the user function icon.
        icon = fetch_icon(self.uf.gui_icon, size='128x128', format=None)
        if icon:
            self.file.write("\includegraphics[bb=0 0 18 18]{%s}\n" % icon)
        else:
            self.file.write("\n")

        # End.
        self.file.write("\n")


    def indexing(self, index, bold=False):
        """Insert index marks into the text, word by word.
        
        @param index:   The index of the word in the self.words data structure.
        @type index:    int
        @keyword bold:  A flag which if True will cause the index entries to be in bold font.
        @type bold:     bool
        """

        # End string.
        if bold:
            end_string = '|textbf}'
        else:
            end_string = '}'

        # Loop over the indices.
        for i in range(len(self.entries)):
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
        for i in range(len(self.entries)):
            # Count the number of words.
            self.entries[i].append(len(self.entries[i][0].split(' ')))

            # Accept capitalisation.
            if search(self.entries[i][0][0], ascii_lowercase):
                self.entries[i][0] = '[' + self.entries[i][0][0].upper() + self.entries[i][0][0] + ']' + self.entries[i][0][1:]

            # Add a carrot to the start of the match string.
            self.entries[i][0] = '^' + self.entries[i][0]

            # Reverse the subarray in prepartion for sorting.
            self.entries[i].reverse()

        # Reverse sort by word count.
        self.entries.sort(reverse=1)
        for i in range(len(self.entries)):
            self.entries[i].reverse()


    def latex_formatting(self, string):
        """Function for handling LaTeX maths environments."""

        # Angstrom.
        string = self.safe_replacement(string, 'Angstroms', '\AA')
        string = self.safe_replacement(string, 'Angstrom', '\AA')

        # Pi.
        string = self.safe_replacement(string, 'pi', '$\pi$')

        # Less than.
        string = string.replace(' < ', ' $<$ ')

        # Less than or equal.
        string = string.replace(' <= ', ' $\le$ ')

        # Much less than.
        string = string.replace(' << ', ' $<<$ ')

        # Greater than.
        string = string.replace(' > ', ' $>$ ')

        # Greater than or equal.
        string = string.replace(' >= ', ' $\ge$ ')

        # Much greater than.
        string = string.replace(' >> ', ' $>>$ ')

        # 1st, 2nd, etc.
        string = string.replace('1st', '1$^\mathrm{st}$')
        string = string.replace('2nd', '2$^\mathrm{nd}$')
        string = string.replace('3rd', '3$^\mathrm{rd}$')
        string = string.replace('4th', '4$^\mathrm{th}$')
        string = string.replace('5th', '5$^\mathrm{th}$')
        string = string.replace('6th', '6$^\mathrm{th}$')
        string = string.replace('7th', '7$^\mathrm{th}$')
        string = string.replace('8th', '8$^\mathrm{th}$')
        string = string.replace('9th', '9$^\mathrm{th}$')
        string = string.replace('0th', '0$^\mathrm{th}$')
        string = string.replace('1th', '1$^\mathrm{th}$')
        string = string.replace('2th', '2$^\mathrm{th}$')
        string = string.replace('3th', '3$^\mathrm{th}$')


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
        string = string.replace('J(w)', '$J(\omega)$')
        string = string.replace('J(0)', '$J(0)$')
        string = string.replace('J(wX)', '$J(\omega_X)$')
        string = string.replace('J(wH)', '$J(\omega_H)$')


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
        for i in range(len(string)):
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
        string = string.replace('\\', 'This is a backslash to be replaced at the end of this functioN')

        # List of special characters (prefix a backslash).
        for char in "#$%&_{}":
            string = string.replace(char, '\\'+char)

        # Doubly special characters (prefix a backslash and postfix '{}').
        for char in "^~":
            string = string.replace(char, '\\'+char+'{}')

        # Damned backslashes!
        string = string.replace('This is a backslash to be replaced at the end of this functioN', '$\\backslash$')

        # Add a backslash to where it really should be.
        string = string.replace('linebreak[0]', '\linebreak[0]')

        # Return the new text.
        return string


    def quotes(self, index):
        """Function for placing quotes within the quote environment."""

        # Split the word by '.
        elements = self.words[index].split("'")

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


    def safe_replacement(self, string, text, latex):
        """Only replace in safe places within the text."""

        # Combos (if only RE could be used!)

        # A number out the front.
        string = string.replace('0'+text,           '0'+latex)
        string = string.replace('1'+text,           '1'+latex)
        string = string.replace('2'+text,           '2'+latex)
        string = string.replace('3'+text,           '3'+latex)
        string = string.replace('4'+text,           '4'+latex)
        string = string.replace('5'+text,           '5'+latex)
        string = string.replace('6'+text,           '6'+latex)
        string = string.replace('7'+text,           '7'+latex)
        string = string.replace('8'+text,           '8'+latex)
        string = string.replace('9'+text,           '9'+latex)

        # In a sentence.
        string = string.replace(' '+text+',',       ' '+latex+',')
        string = string.replace(' '+text+'.',       ' '+latex+'.')
        string = string.replace(' '+text+' ',       ' '+latex+' ')
        string = string.replace(' '+text+';',       ' '+latex+';')
        string = string.replace(' '+text+':',       ' '+latex+':')

        # In lists [].
        string = string.replace('['+text+']',       '['+latex+']')
        string = string.replace('['+text+' ',       '['+latex+' ')
        string = string.replace('['+text+',',       '['+latex+',')
        string = string.replace('['+text+';',       '['+latex+';')
        string = string.replace(' '+text+']',       ' '+latex+']')

        # In lists ().
        string = string.replace('('+text+')',       '('+latex+')')
        string = string.replace('('+text+' ',       '('+latex+' ')
        string = string.replace('('+text+',',       '('+latex+',')
        string = string.replace('('+text+';',       '('+latex+';')
        string = string.replace(' '+text+')',       ' '+latex+')')

        # In lists {}.
        string = string.replace('{'+text+' ',       '{'+latex+' ')
        string = string.replace('{'+text+',',       '{'+latex+',')
        string = string.replace('{'+text+';',       '{'+latex+';')
        string = string.replace(' '+text+'\\',      ' '+latex+'\\')

        # Quoted.
        string = string.replace('`'+text+'\'',      '`'+latex+'\'')
        string = string.replace('`'+text+' ',       '`'+latex+' ')
        string = string.replace('`'+text+',',       '`'+latex+',')
        string = string.replace('`'+text+'.',       '`'+latex+'.')
        string = string.replace('`'+text+';',       '`'+latex+';')
        string = string.replace(' '+text+'\'',      ' '+latex+'\'')

        # End of the line.
        substring = string[-len(text)-1:].replace(' '+text,      ' '+latex)
        string = string[0:-len(text)-1] + substring

        substring = string[-len(text)-1:].replace('.'+text,      '.'+latex)
        string = string[0:-len(text)-1] + substring

        string = string.replace(' '+text+'\n',      ' '+latex+'\n')
        string = string.replace('.'+text+'\n',      '.'+latex+'\n')

        # Maths
        string = string.replace(' '+text+'\^',      ' '+latex+'\^')
        string = string.replace('('+text+'\^',      '('+latex+'\^')
        string = string.replace('\n'+text+'\^',     '\n'+latex+'\^')

        # At the start of the line.
        if search('^'+text+'['+punctuation+']', string) or search('^'+text+'['+whitespace+']', string) or search('\n'+text+'['+punctuation+']', string) or search('\n'+text+'['+whitespace+']', string):
            string = string.replace(text+' ',           latex+' ')
            string = string.replace(text+',',           latex+',')
            string = string.replace(text+'.',           latex+'.')
            string = string.replace(text+';',           latex+';')
            string = string.replace(text+']',           latex+']')
            string = string.replace(text+')',           latex+')')
            string = string.replace(text+'^',           latex+'^')
            string = string.replace(text+'\\',          latex+'\\')
            string = string.replace(text+'\'',          latex+'\'')
            string = string.replace(text+'\n',          latex+'\n')


        # Return the string.
        return string


    def script_definitions(self, uf_names):
        """Create a LaTeX file defining the relax language syntax for the listings package.

        @param uf_names:    The list of all user function names.
        @type uf_names:     list of str
        """

        # Open the file.
        file = open(self.path + sep + 'script_definition.tex', 'w')

        # Python keywords.
        py_keywords = [
            'and',
            'assert',
            'break',
            'continue',
            'del',
            'else',
            'exec',
            'global',
            'if',
            'in',
            'is',
            'for',
            'not',
            'or',
            'pass',
            'print',
            'raise',
            'return',
            'while',
            'yield'
        ]
        py_keywords2 = [
            'as',
            'from',
            'import',
        ]
        py_keywords3 = [
            'class',
            'def',
        ]

        # The relax language.
        file.write("\lstdefinelanguage{relax}{\n")

        # Allow the user function '.' character to be part of the keywords.
        file.write("    alsoletter={.},\n")

        # Output the first set of Python keywords.
        file.write("    morekeywords={")
        for name in py_keywords:
            file.write("%s," % name)
        file.write("},\n")

        # Output the second set of Python keywords.
        file.write("    morekeywords=[2]{")
        for name in py_keywords2:
            file.write("%s," % name)
        file.write("},\n")

        # Output the third set of Python keywords.
        file.write("    morekeywords=[3]{")
        for name in py_keywords3:
            file.write("%s," % name)
        file.write("},\n")

        # Output the relax user functions as keywords.
        file.write("    morekeywords=[4]{")
        for name in uf_names:
            file.write("%s," % name)
        file.write("},\n")

        # The rest of the definition.
        file.write("    moreprocnamekeys={def,class},\n")
        file.write("    sensitive=true,\n")
        file.write("    morecomment=[l]{\#},\n")
        file.write("    morestring=[b]',\n")
        file.write("    morestring=[b]\",\n")
        file.write("    morestring=[b]\"\"\",\n")
        file.write("}\n")

        # Close the file.
        file.close()


    def tabular_wrapping(self, table, max_char=100):
        """Determine if column wrapping should occur.

        @param table:       The table.
        @type table:        list of lists of str
        @keyword max_char:  The maximum number of characters a column is allowed before wrapping is applied.
        @type max_char:     int
        @return:            The list of flags for wrapping columns.
        @rtype:             list of bool
        """

        # The column widths.
        num_cols = len(table[0])
        widths = [0] * num_cols
        for i in range(len(table)):
            for j in range(num_cols):
                # The element is larger than the previous.
                if len(table[i][j]) > widths[j]:
                    widths[j] = len(table[i][j])

        # The wrapping.
        wrap = []
        for i in range(len(widths)):
            if widths[i] > max_char:
                wrap.append(True)
            else:
                wrap.append(False)

        # Return the result.
        return wrap


    def word_formatting(self, text, bold=False):
        """Format the text, word by word.

        @param text:    The text to format.
        @type text:     str
        @keyword bold:  A flag for the indexing which if True will cause index entries to be in bold font.
        @type bold:     bool
        @return:        The formatted text.
        @rtype:         str
        """

        # Initialise.
        new_text = ''

        # Split the string.
        self.words = text.split(' ')

        # Loop over the words one by one.
        for i in range(len(self.words)):
            # Indexing.
            self.indexing(i, bold=bold)

            # Quotes.
            self.quotes(i)

            # Recreate the string.
            if i == 0:
                new_text = self.words[i]
            else:
                new_text += ' ' + self.words[i]

        # Return the text.
        return new_text


    def write_item_list(self, item_list):
        """Format and write out an itemised list.

        @param item_list:   The list of items and description lists.
        @type item_list:    list of list of str
        """

        # Loop over the elements.
        latex_lines = []
        items = False
        for i in range(len(item_list)):
            # LaTeX formatting of the item.
            item = item_list[i][0]
            if item == None:
                item = ''
            if item != '':
                items = True
                item = self.latex_special_chars(item)
                item = self.latex_formatting(item)
                item = self.word_formatting(item)

            # LaTeX formatting of the description.
            desc = self.latex_special_chars(item_list[i][1])
            desc = self.latex_formatting(desc)
            desc = self.word_formatting(desc)

            # Write to file.
            if item != '':
                latex_lines.append("\\item[%s --] %s\n" % (item, desc))
            else:
                latex_lines.append("\\item[]%s\n" % desc)

        # Start the environment.
        if not items:
            self.file.write("\\begin{itemize}\n")
        else:
            self.file.write("\\begin{description}\n")

        # Add the lines.
        for line in latex_lines:
            self.file.write(line)

        # End the environment.
        if not items:
            self.file.write("\\end{itemize}\n\n")
        else:
            self.file.write("\\end{description}\n\n")


    def write_list(self, list):
        """Format and write out a list.

        @param list:    The list.
        @type list:     list of str
        """

        # Start the environment.
        self.file.write("\\begin{itemize}\n")

        # Loop over the elements.
        for item in list:
            # LaTeX formatting.
            item = self.latex_special_chars(item)
            item = self.latex_formatting(item)
            item = self.word_formatting(item)

            # Write to file.
            self.file.write("\\item[]%s\n" % item)

        # End the environment.
        self.file.write("\\end{itemize}\n\n")


    def write_paragraph(self, text):
        """Format and write out the paragraph.

        @param text:    The single line of text to convert into a LaTeX paragraph.
        @type text:     str
        """

        # LaTeX formatting.
        text = self.latex_special_chars(text)
        text = self.latex_formatting(text)
        text = self.word_formatting(text)

        # Write to file.
        self.file.write(text + "\n\n")


    def write_prompt_example(self, list):
        """Format and write out the prompt UI examples.

        @param list:    The list of prompt UI examples.
        @type list:     list of str
        """

        # Loop over the examples.
        for text in list:
            # LaTeX formatting.
            text = self.break_functions(text)
            text = self.latex_quotes(text)
            text = self.latex_special_chars(text)

            # Write to file.
            self.file.write("\\smallexample{%s}\n\n" % text)

        # An extra newline.
        self.file.write("\n")


    def write_table(self, label):
        """Format and write out a table.

        @param label:   The unique table label.
        @type label:    list of lists of str
        """

        # Get the table.
        table = uf_tables.get_table(label)

        # Add a reference.
        self.file.write("Please see Table~\\ref{%s} on page~\\pageref{%s}.\n\n" % (label, label))

        # The table already exists, so skip creating it a second time.
        if label in self.uf_table_labels:
            return
        else:
            self.uf_table_labels.append(label)

        # Determine the table wrapping.
        col_wrap = self.tabular_wrapping(table.cells)
        wrap = sum(col_wrap)

        # The number of rows and columns.
        num_rows = len(table.cells)
        num_cols = len(table.headings)

        # Start the centred table.
        if table.longtable:
            # A longtable.
            self.file.write("\\onecolumn\n")
            self.file.write("\\begin{scriptsize}\n")
            self.file.write("\\begin{center}\n")
            self.file.write("\\begin{longtable}{%s}\n" % ("l"*num_cols))
        else:
            # Normal tables.
            self.file.write("\\begin{table*}\n")
            self.file.write("\\begin{scriptsize}\n")
            self.file.write("\\begin{center}\n")

        # A caption.
        self.file.write("\\caption[%s]{%s}\n" % (table.caption_short, table.caption))

        # The formatting.
        if table.longtable:
            # Start the longtable environment and add the toprule.
            self.file.write("\\\\\n")
            self.file.write("\\toprule\n")
        else:
            # Start the tabular environment and add the toprule.
            if wrap:
                self.file.write("\\begin{tabularx}{\\textwidth}{")
            else:
                self.file.write("\\begin{tabular}{")
            for i in range(num_cols):
                if col_wrap[i]:
                    text = "X"
                else:
                    text = "l"
                self.file.write(text)
            self.file.write("}\n")
            self.file.write("\\\\[-5pt]\n")
            self.file.write("\\toprule\n")

        # Generate the LaTeX headings.
        for j in range(num_cols):
            # Column separator.
            if j > 0:
                self.file.write(' & ')

            # The cell contents.
            cell = table.headings[j]
            cell = self.latex_special_chars(cell)
            cell = self.latex_formatting(cell)

            # Write the cell contents.
            self.file.write(cell)

        # End of the header line.
        self.file.write(" \\\\\n")

        # The central formatting.
        if table.longtable:
            self.file.write("\\midrule\n")
            self.file.write("\\endhead\n\n")
            self.file.write("\\bottomrule\n")
            self.file.write("\\endfoot\n")
        else:
            # Add the midrule.
            self.file.write("\\midrule\n")

        # The label for longtables.
        if table.longtable:
            self.file.write("\\label{%s}\n" % label)

        # Loop over the main table lines.
        for i in range(num_rows):
            # Loop over the columns.
            for j in range(num_cols):
                # Column separator.
                if j > 0:
                    self.file.write(' & ')

                # The cell contents.
                cell = table.cells[i][j]
                cell = self.latex_special_chars(cell)
                cell = self.latex_formatting(cell)

                # Write the cell contents.
                self.file.write(cell)

            # End of the line.
            self.file.write(" \\\\\n")

        # Terminate.
        if table.longtable:
            self.file.write("\\end{longtable}\n")
            self.file.write("\\end{center}\n")
            self.file.write("\\end{scriptsize}\n")
            self.file.write("\\twocolumn\n")
        else:
            self.file.write("\\bottomrule\n")
            self.file.write("\\\\[-5pt]\n")
            self.file.write("\\label{%s}\n" % label)
            if wrap:
                self.file.write("\\end{tabularx}\n")
            else:
                self.file.write("\\end{tabular}\n")
            self.file.write("\\end{center}\n")
            self.file.write("\\end{scriptsize}\n")
            self.file.write("\\end{table*}\n")

        # Increment the table counts.
        self.table_count += 1
        self.uf_table_count += 1

        # A some newlines.
        self.file.write("\n\n")


    def write_verbatim(self, text):
        """Format and write out the verbatim text.

        @param text:    The text to write out in a LaTeX verbatim environment.
        @type text:     str
        """

        # Write to file.
        self.file.write("{\\footnotesize \\begin{verbatim}\n")
        self.file.write(text)
        self.file.write("\n\\end{verbatim}}\n\n")
