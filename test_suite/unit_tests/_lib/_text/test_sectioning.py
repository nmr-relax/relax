###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
from unittest import TestCase

# relax module imports.
from lib.text.sectioning import section, subsection, subsubsection, subsubtitle, subtitle, title
from relax_io import DummyFileObject


class Test_sectioning(TestCase):
    """Unit tests for the lib.text.sectioning relax module."""

    def test_section(self):
        """Test of the lib.text.sectioning.section() function."""

        # Write out the section.
        file = DummyFileObject()
        section(file=file, text='Test section')

        # Read the results.
        lines = file.readlines()
        print("Formatted section lines:  %s" % lines)

        # Check the title.
        real_lines = [
            '\n',
            '\n',
            'Test section\n',
            '============\n',
            '\n',
        ]
        self.assertEqual(len(lines), len(real_lines))
        for i in range(len(lines)):
            self.assertEqual(lines[i], real_lines[i])


    def test_subsection(self):
        """Test of the lib.text.sectioning.subsection() function."""

        # Write out the subsection.
        file = DummyFileObject()
        subsection(file=file, text='Test subsection')

        # Read the results.
        lines = file.readlines()
        print("Formatted subsection lines:  %s" % lines)

        # Check the title.
        real_lines = [
            '\n',
            'Test subsection\n',
            '---------------\n',
            '\n',
        ]
        self.assertEqual(len(lines), len(real_lines))
        for i in range(len(lines)):
            self.assertEqual(lines[i], real_lines[i])


    def test_subsubsection(self):
        """Test of the lib.text.sectioning.subsubsection() function."""

        # Write out the subsubsection.
        file = DummyFileObject()
        subsubsection(file=file, text='Test subsubsection')

        # Read the results.
        lines = file.readlines()
        print("Formatted subsubsection lines:  %s" % lines)

        # Check the title.
        real_lines = [
            '\n',
            'Test subsubsection\n',
            '~~~~~~~~~~~~~~~~~~\n',
            '\n',
        ]
        self.assertEqual(len(lines), len(real_lines))
        for i in range(len(lines)):
            self.assertEqual(lines[i], real_lines[i])


    def test_subsubtitle(self):
        """Test of the lib.text.sectioning.subsubtitle() function."""

        # Write out the subtitle.
        file = DummyFileObject()
        subsubtitle(file=file, text='Test subsubtitle')

        # Read the results.
        lines = file.readlines()
        print("Formatted subsubtitle lines:  %s" % lines)

        # Check the title.
        real_lines = [
            '\n',
            '~~~~~~~~~~~~~~~~~~~~\n',
            '~ Test subsubtitle ~\n',
            '~~~~~~~~~~~~~~~~~~~~\n',
            '\n',
        ]
        self.assertEqual(len(lines), len(real_lines))
        for i in range(len(lines)):
            self.assertEqual(lines[i], real_lines[i])


    def test_subtitle(self):
        """Test of the lib.text.sectioning.subtitle() function."""

        # Write out the subtitle.
        file = DummyFileObject()
        subtitle(file=file, text='Test subtitle')

        # Read the results.
        lines = file.readlines()
        print("Formatted subtitle lines:  %s" % lines)

        # Check the title.
        real_lines = [
            '\n',
            '-----------------\n',
            '- Test subtitle -\n',
            '-----------------\n',
            '\n',
        ]
        self.assertEqual(len(lines), len(real_lines))
        for i in range(len(lines)):
            self.assertEqual(lines[i], real_lines[i])


    def test_title(self):
        """Test of the lib.text.sectioning.title() function."""

        # Write out the title.
        file = DummyFileObject()
        title(file=file, text='Test title')

        # Read the results.
        lines = file.readlines()
        print("Formatted title lines:  %s" % lines)

        # Check the title.
        real_lines = [
            '\n',
            '\n',
            '==============\n',
            '= Test title =\n',
            '==============\n',
            '\n',
        ]
        self.assertEqual(len(lines), len(real_lines))
        for i in range(len(lines)):
            self.assertEqual(lines[i], real_lines[i])
