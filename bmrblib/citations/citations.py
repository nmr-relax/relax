#############################################################################
#                                                                           #
# The BMRB library.                                                         #
#                                                                           #
# Copyright (C) 2009-2013 Edward d'Auvergne                                 #
#                                                                           #
# This program is free software: you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation, either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                           #
#############################################################################

# Module docstring.
"""The citations saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#citations.
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory, TagCategoryFree


class CitationsSaveframe(BaseSaveframe):
    """The citations saveframe class."""

    # Class variables.
    label = 'citation'
    sf_label = 'citations'

    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.tag_categories.append(Citations(self))
        self.tag_categories.append(CitationsAuthor(self))



class Citations(TagCategoryFree):
    """Base class for the Citations tag category."""

    def __init__(self, sf):
        """Setup the Citations tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(Citations, self).__init__(sf)

        # Add the tag info.
        self.add(key='CitationID',                  tag_name='ID',                          var_name='count_str')
        self.add(key='CASAbstractCode',             tag_name='CAS_abstract_code',           var_name='cas_abstract_code')
        self.add(key='MEDLINEUICode',               tag_name='MEDLINE_UI_code',             var_name='medline_ui_code')
        self.add(key='DOI',                         tag_name='DOI',                         var_name='doi')
        self.add(key='PubMedID',                    tag_name='PubMed_ID',                   var_name='pubmed_id')
        self.add(key='FullCitation',                tag_name='Full_citation',               var_name='full_citation')
        self.add(key='Title',                       tag_name='Title',                       var_name='title')
        self.add(key='Status',                      tag_name='Status',                      var_name='status')
        self.add(key='Type',                        tag_name='Type',                        var_name='type')
        self.add(key='JournalAbbrev',               tag_name='Journal_abbrev',              var_name='journal_abbrev')
        self.add(key='JournalNameFull',             tag_name='Journal_name_full',           var_name='journal_full')
        self.add(key='JournalVolume',               tag_name='Journal_volume',              var_name='volume')
        self.add(key='JournalIssue',                tag_name='Journal_issue',               var_name='issue')
        self.add(key='JournalASTM',                 tag_name='Journal_ASTM',                var_name=None)
        self.add(key='JournalISSN',                 tag_name='Journal_ISSN',                var_name=None)
        self.add(key='JournalCSD',                  tag_name='Journal_CSD',                 var_name=None)
        self.add(key='BookTitle',                   tag_name='Book_title',                  var_name=None)
        self.add(key='BookChapterTitle',            tag_name='Book_chapter_title',          var_name=None)
        self.add(key='BookVolume',                  tag_name='Book_volume',                 var_name=None)
        self.add(key='BookSeries',                  tag_name='Book_series',                 var_name=None)
        self.add(key='BookPublisher',               tag_name='Book_publisher',              var_name=None)
        self.add(key='BookPublisherCity',           tag_name='Book_publisher_city',         var_name=None)
        self.add(key='BookISBN',                    tag_name='Book_ISBN',                   var_name=None)
        self.add(key='ConferenceTitle',             tag_name='Conference_title',            var_name=None)
        self.add(key='ConferenceSite',              tag_name='Conference_site',             var_name=None)
        self.add(key='ConferenceStateProvince',     tag_name='Conference_state_province',   var_name=None)
        self.add(key='ConferenceCountry',           tag_name='Conference_country',          var_name=None)
        self.add(key='ConferenceStartDate',         tag_name='Conference_start_date',       var_name=None)
        self.add(key='ConferenceEndDate',           tag_name='Conference_end_date',         var_name=None)
        self.add(key='ConferenceAbstractNumber',    tag_name='Conference_abstract_number',  var_name=None)
        self.add(key='ThesisInstitution',           tag_name='Thesis_institution',          var_name=None)
        self.add(key='ThesisInstitutionCity',       tag_name='Thesis_institution_city',     var_name=None)
        self.add(key='ThesisInstitutionCountry',    tag_name='Thesis_institution_country',  var_name=None)
        self.add(key='WWWURL',                      tag_name='WWW_URL',                     var_name=None)
        self.add(key='PageFirst',                   tag_name='Page_first',                  var_name='page_first')
        self.add(key='PageLast',                    tag_name='Page_last',                   var_name='page_last')
        self.add(key='Year',                        tag_name='Year',                        var_name='year')
        self.add(key='Details',                     tag_name='Details',                     var_name=None)



class CitationsAuthor(TagCategory):
    """Base class for the CitationsAuthor tag category."""

    def __init__(self, sf):
        """Setup the CitationsAuthor tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(CitationsAuthor, self).__init__(sf)

        # Add the tag info.
        self.add(key='Ordinal',         tag_name='Ordinal',         var_name='data_ids')
        self.add(key='GivenName',       tag_name='Given_name',      var_name='author_given_name')
        self.add(key='FamilyName',      tag_name='Family_name',     var_name='author_family_name')
        self.add(key='FirstInitial',    tag_name='First_initial',   var_name='author_first_init')
        self.add(key='MiddleInitials',  tag_name='Middle_initials', var_name='author_mid_init')
        self.add(key='FamilyTitle',     tag_name='Family_title',    var_name='author_family_title')
        self.add(key='SfID',            tag_name='Sf_ID',           var_name=None)
        self.add(key='EntryID',         tag_name='Entry_ID',        var_name=None)
        self.add(key='CitationID',      tag_name='Citation_ID',     var_name='count_str')
