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
        self.cite_id = self.input_field(sizer, "The citation ID:", tooltip=self.uf._doc_args_dict['cite_id'])
        self.authors = self.element_string_list_of_lists(key='authors', titles=["First name", "Last name", "First initial", "Middle initials"], sizer=sizer, desc="The author list:", tooltip=self.uf._doc_args_dict['authors'])
        self.doi = self.input_field(sizer, "The DOI number:", tooltip=self.uf._doc_args_dict['doi'])
        self.pubmed_id = self.input_field(sizer, "The Pubmed ID number:", tooltip=self.uf._doc_args_dict['pubmed_id'])
        self.full_citation = self.input_field(sizer, "The full citation:", tooltip=self.uf._doc_args_dict['full_citation'])
        self.title = self.input_field(sizer, "The title:", tooltip=self.uf._doc_args_dict['title'])
        self.status = self.input_field(sizer, "The status:", tooltip=self.uf._doc_args_dict['status'])
        self.type = self.input_field(sizer, "The type:", tooltip=self.uf._doc_args_dict['type'])
        self.journal_abbrev = self.input_field(sizer, "The journal abbreviation:", tooltip=self.uf._doc_args_dict['journal_abbrev'])
        self.journal_full = self.input_field(sizer, "The full journal name:", tooltip=self.uf._doc_args_dict['journal_full'])
        self.volume = self.input_field(sizer, "The volume:", tooltip=self.uf._doc_args_dict['volume'])
        self.issue = self.input_field(sizer, "The issue:", tooltip=self.uf._doc_args_dict['issue'])
        self.page_first = self.input_field(sizer, "The first page:", tooltip=self.uf._doc_args_dict['page_first'])
        self.page_last = self.input_field(sizer, "The last page:", tooltip=self.uf._doc_args_dict['page_last'])
        self.year = self.input_field(sizer, "The year:", tooltip=self.uf._doc_args_dict['year'])


    def on_execute(self):
        """Execute the user function."""

        # The data.
        cite_id = gui_to_str(self.cite_id.GetValue())
        authors = self.GetValue('authors')
        doi = gui_to_str(self.doi.GetValue())
        pubmed_id = gui_to_str(self.pubmed_id.GetValue())
        full_citation = gui_to_str(self.full_citation.GetValue())
        title = gui_to_str(self.title.GetValue())
        status = gui_to_str(self.status.GetValue())
        type = gui_to_str(self.type.GetValue())
        journal_abbrev = gui_to_str(self.journal_abbrev.GetValue())
        journal_full = gui_to_str(self.journal_full.GetValue())
        volume = gui_to_int(self.volume.GetValue())
        issue = gui_to_int(self.issue.GetValue())
        page_first = gui_to_int(self.page_first.GetValue())
        page_last = gui_to_int(self.page_last.GetValue())
        year = gui_to_int(self.year.GetValue())

        # Execute the user function.
        self.execute('bmrb.citation', cite_id=cite_id, authors=authors, doi=doi, pubmed_id=pubmed_id, full_citation=full_citation, title=title, status=status, type=type, journal_abbrev=journal_abbrev, journal_full=journal_full, volume=volume, issue=issue, page_first=page_first, page_last=page_last, year=year)
