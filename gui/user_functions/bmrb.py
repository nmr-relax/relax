###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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

# Module docstring.
"""The BMRB user function GUI elements."""

# Python module imports.
import wx

# GUI module imports.
from base import UF_base, UF_page
from gui.paths import WIZARD_IMAGE_PATH
from gui.misc import gui_to_float, gui_to_int, gui_to_str, str_to_gui


# The container class.
class Bmrb(UF_base):
    """The container class for holding all GUI elements."""

    def citation(self):
        """The bmrb.citation user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=1000, size_y=800, name='bmrb.citation', uf_page=Citation_page)
        wizard.run()



class Citation_page(UF_page):
    """The bmrb.citation() user function page."""

    # Some class variables.
    height_desc = 140
    image_path = WIZARD_IMAGE_PATH + 'bmrb.png'
    uf_path = ['bmrb', 'citation']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The fields.
        self.element_string(key='cite_id', sizer=sizer, desc="The citation ID:", tooltip=self.uf._doc_args_dict['cite_id'])
        self.element_string_list_of_lists(key='authors', titles=["First name", "Last name", "First initial", "Middle initials"], sizer=sizer, desc="The author list:", tooltip=self.uf._doc_args_dict['authors'])
        self.element_string(key='doi', sizer=sizer, desc="The DOI number:", tooltip=self.uf._doc_args_dict['doi'])
        self.element_string(key='pubmed_id', sizer=sizer, desc="The Pubmed ID number:", tooltip=self.uf._doc_args_dict['pubmed_id'])
        self.element_string(key='full_citation', sizer=sizer, desc="The full citation:", tooltip=self.uf._doc_args_dict['full_citation'])
        self.element_string(key='title', sizer=sizer, desc="The title:", tooltip=self.uf._doc_args_dict['title'])
        self.element_string(key='status', sizer=sizer, desc="The status:", tooltip=self.uf._doc_args_dict['status'])
        self.element_string(key='type', sizer=sizer, desc="The type:", tooltip=self.uf._doc_args_dict['type'])
        self.element_string(key='journal_abbrev', sizer=sizer, desc="The journal abbreviation:", tooltip=self.uf._doc_args_dict['journal_abbrev'])
        self.element_string(key='journal_full', sizer=sizer, desc="The full journal name:", tooltip=self.uf._doc_args_dict['journal_full'])
        self.element_int(key='volume', sizer=sizer, desc="The volume:", tooltip=self.uf._doc_args_dict['volume'])
        self.element_int(key='issue', sizer=sizer, desc="The issue:", tooltip=self.uf._doc_args_dict['issue'])
        self.element_int(key='page_first', sizer=sizer, desc="The first page:", tooltip=self.uf._doc_args_dict['page_first'])
        self.element_int(key='page_last', sizer=sizer, desc="The last page:", tooltip=self.uf._doc_args_dict['page_last'])
        self.element_int(key='year', sizer=sizer, desc="The year:", tooltip=self.uf._doc_args_dict['year'])


    def on_execute(self):
        """Execute the user function."""

        # The data.
        cite_id = self.GetValue('cite_id')
        authors = self.GetValue('authors')
        doi = self.GetValue('doi')
        pubmed_id = self.GetValue('pubmed_id')
        full_citation = self.GetValue('full_citation')
        title = self.GetValue('title')
        status = self.GetValue('status')
        type = self.GetValue('type')
        journal_abbrev = self.GetValue('journal_abbrev')
        journal_full = self.GetValue('journal_full')
        volume = self.GetValue('volume')
        issue = self.GetValue('issue')
        page_first = self.GetValue('page_first')
        page_last = self.GetValue('page_last')
        year = self.GetValue('year')

        # Execute the user function.
        self.execute('bmrb.citation', cite_id=cite_id, authors=authors, doi=doi, pubmed_id=pubmed_id, full_citation=full_citation, title=title, status=status, type=type, journal_abbrev=journal_abbrev, journal_full=journal_full, volume=volume, issue=issue, page_first=page_first, page_last=page_last, year=year)
