###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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
"""The citations saveframe category.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#citations.
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory
from bmrblib.misc import translate
from bmrblib.pystarlib.SaveFrame import SaveFrame
from bmrblib.pystarlib.TagTable import TagTable


class CitationsSaveframe(BaseSaveframe):
    """The citations saveframe class."""

    # Saveframe variables.
    label = 'citations'


    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.datanodes = datanodes

        # The number of entities.
        self.citation_num = 0

        # Add the specific tag category objects.
        self.add_tag_categories()


    def add(self, citation_label='citation', authors=None, doi=None, pubmed_id=None, full_citation=None, title=None, status='published', type='journal', journal_abbrev=None, journal_full=None, volume=None, issue=None, page_first=None, page_last=None, year=None):
        """Add the citation information to the data nodes.

        @keyword citation_label:    A label to call the saveframe.
        @type citation_label:       str
        @keyword authors:           The list of authors.  Each author element is a list of four elements: the first name, last name, first initial, and middle initials.
        @type authors:              list of lists of str
        @keyword doi:               The DOI number, e.g. "10.1000/182".
        @type doi:                  None or str
        @keyword pubmed_id:         The identification code assigned to the publication by PubMed.
        @type pubmed_id:            None or int
        @keyword full_citation:     A full citation in a format similar to that used in a journal article by either cutting and pasting from another document or by typing. Please include author names, title, journal, page numbers, and year or equivalent information for the type of publication given.
        @type full_citation:        str
        @keyword title:             The title of the publication.
        @type title:                str
        @keyword status:            The publication status.  Can be one of in "preparation", "in press", "published", "retracted", or "submitted".
        @type status:               str
        @keyword type:              The publication type.  Can be one of "abstract", "BMRB only", "book", "book chapter", "internet", "journal", "personal communication", or "thesis".
        @type type:                 str
        @keyword journal_abbrev:    A standard journal abbreviation as defined by the Chemical Abstract Services for the journal where the data are or will be published.  If the data in the deposition are related to a J. Biomol. NMR paper, the value must be 'J. Biomol. NMR' to alert the BMRB annotators so that the deposition is properly processed.  If the depositor truly does not know the journal, a value of 'not known' or 'na' is acceptable.
        @type journal_abbrev:       str
        @keyword journal_full:      The full journal name.
        @type journal_full:         str
        @keyword volume:            The volume number.
        @type volume:               int
        @keyword issue:             The issue number.
        @type issue:                int
        @keyword page_first:        The first page number.
        @type page_first:           int
        @keyword page_last:         The last page number.
        @type page_last:            int
        @keyword year:              The publication year.
        @type year:                 int
        """

        # Place the args into the namespace.
        self.doi = translate(doi)
        self.pubmed_id = translate(pubmed_id)
        self.full_citation = full_citation
        self.title = translate(title)
        self.status = translate(status)
        self.type = translate(type)
        self.journal_abbrev = translate(journal_abbrev)
        self.journal_full = translate(journal_full)
        self.volume = translate(volume)
        self.issue = translate(issue)
        self.page_first = translate(page_first)
        self.page_last = translate(page_last)
        self.year = translate(year)

        # The author info.
        self.author_given_name = []
        self.author_family_name = []
        self.author_first_init = []
        self.author_mid_init = []
        self.author_family_title = []
        for i in range(len(authors)):
            self.author_given_name.append(authors[i][0])
            self.author_family_name.append(authors[i][1])
            self.author_first_init.append(authors[i][2])
            self.author_mid_init.append(authors[i][3])
            self.author_family_title.append(None)
        self.author_given_name = translate(self.author_given_name)
        self.author_family_name = translate(self.author_family_name)
        self.author_first_init = translate(self.author_first_init)
        self.author_mid_init = translate(self.author_mid_init)
        self.author_family_title = translate(self.author_family_title)
        self.generate_data_ids(len(authors))

        # Increment the number of entities.
        self.citation_num = self.citation_num + 1
        self.citation_id_num = [str(translate(self.citation_num))]

        # Initialise the save frame.
        self.frame = SaveFrame(title=citation_label)

        # Create the tag categories.
        self.citations.create()
        self.citations_author.create()

        # Add the saveframe to the data nodes.
        self.datanodes.append(self.frame)


    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.citations = Citations(self)
        self.citations_author = CitationsAuthor(self)



class Citations(TagCategory):
    """Base class for the Citations tag category."""

    # Class variables.
    label = 'citations'

    def create(self):
        """Create the Citations tag category."""

        # All the tags.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SfCategory']], tagvalues=[[self.label]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['CitationID']], tagvalues=[[str(self.sf.citation_num)]]))
        #self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['CASAbstractCode']], tagvalues=[[self.sf.cas_abstract_code]]))
        #self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['MEDLINEUICode']], tagvalues=[[self.sf.medline_ui_code]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['DOI']], tagvalues=[[self.sf.doi]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['PubMedID']], tagvalues=[[self.sf.pubmed_id]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['FullCitation']], tagvalues=[[self.sf.full_citation]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['Title']], tagvalues=[[self.sf.title]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['Status']], tagvalues=[[self.sf.status]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['Type']], tagvalues=[[self.sf.type]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['JournalAbbrev']], tagvalues=[[self.sf.journal_abbrev]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['JournalNameFull']], tagvalues=[[self.sf.journal_full]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['JournalVolume']], tagvalues=[[self.sf.volume]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['JournalIssue']], tagvalues=[[self.sf.issue]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['PageFirst']], tagvalues=[[self.sf.page_first]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['PageLast']], tagvalues=[[self.sf.page_last]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['Year']], tagvalues=[[self.sf.year]]))


    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Category label.
        if not tag_category_label:
            tag_category_label='Citation'

        # Execute the base class tag_setup() method.
        TagCategory.tag_setup(self, tag_category_label=tag_category_label, sep=sep)

        # Tag names for the citations.
        self.tag_names['SfCategory'] =                  'Sf_category'
        self.tag_names['CitationID'] =                  'ID'
        self.tag_names['CASAbstractCode'] =             'CAS_abstract_code'
        self.tag_names['MEDLINEUICode'] =               'MEDLINE_UI_code'
        self.tag_names['DOI'] =                         'DOI'
        self.tag_names['PubMedID'] =                    'PubMed_ID'
        self.tag_names['FullCitation'] =                'Full_citation'
        self.tag_names['Title'] =                       'Title'
        self.tag_names['Status'] =                      'Status'
        self.tag_names['Type'] =                        'Type'
        self.tag_names['JournalAbbrev'] =               'Journal_abbrev'
        self.tag_names['JournalNameFull'] =             'Journal_name_full'
        self.tag_names['JournalVolume'] =               'Journal_volume'
        self.tag_names['JournalIssue'] =                'Journal_issue'
        self.tag_names['JournalASTM'] =                 'Journal_ASTM'
        self.tag_names['JournalISSN'] =                 'Journal_ISSN'
        self.tag_names['JournalCSD'] =                  'Journal_CSD'
        self.tag_names['BookTitle'] =                   'Book_title'
        self.tag_names['BookChapterTitle'] =            'Book_chapter_title'
        self.tag_names['BookVolume'] =                  'Book_volume'
        self.tag_names['BookSeries'] =                  'Book_series'
        self.tag_names['BookPublisher'] =               'Book_publisher'
        self.tag_names['BookPublisherCity'] =           'Book_publisher_city'
        self.tag_names['BookISBN'] =                    'Book_ISBN'
        self.tag_names['ConferenceTitle'] =             'Conference_title'
        self.tag_names['ConferenceSite'] =              'Conference_site'
        self.tag_names['ConferenceStateProvince'] =     'Conference_state_province'
        self.tag_names['ConferenceCountry'] =           'Conference_country'
        self.tag_names['ConferenceStartDate'] =         'Conference_start_date'
        self.tag_names['ConferenceEndDate'] =           'Conference_end_date'
        self.tag_names['ConferenceAbstractNumber'] =    'Conference_abstract_number'
        self.tag_names['ThesisInstitution'] =           'Thesis_institution'
        self.tag_names['ThesisInstitutionCity'] =       'Thesis_institution_city'
        self.tag_names['ThesisInstitutionCountry'] =    'Thesis_institution_country'
        self.tag_names['WWWURL'] =                      'WWW_URL'
        self.tag_names['PageFirst'] =                   'Page_first'
        self.tag_names['PageLast'] =                    'Page_last'
        self.tag_names['Year'] =                        'Year'
        self.tag_names['Details'] =                     'Details'


class CitationsAuthor(TagCategory):
    """Base class for the CitationsAuthor tag category."""

    def create(self):
        """Create the Citations tag category."""

        # Keys and objects.
        info = [
            ['Ordinal',         'data_ids'],
            ['GivenName',       'author_given_name'],
            ['FamilyName',      'author_family_name'],
            ['FirstInitial',    'author_first_init'],
            ['MiddleInitials',  'author_mid_init'],
            ['FamilyTitle',     'author_family_title'],
            ['CitationID',      'citation_id_num']
        ]

        # Get the TabTable.
        table = self.create_tag_table(info)

        # Add the tagtable to the save frame.
        self.sf.frame.tagtables.append(table)


    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Category label.
        if not tag_category_label:
            tag_category_label='Citation_author'

        # Execute the base class tag_setup() method.
        TagCategory.tag_setup(self, tag_category_label=tag_category_label, sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['Ordinal'] =         'Ordinal'
        self.tag_names['GivenName'] =       'Given_name'
        self.tag_names['FamilyName'] =      'Family_name'
        self.tag_names['FirstInitial'] =    'First_initial'
        self.tag_names['MiddleInitials'] =  'Middle_initials'
        self.tag_names['FamilyTitle'] =     'Family_title'
        self.tag_names['SfID'] =            'Sf_ID'
        self.tag_names['EntryID'] =         'Entry_ID'
        self.tag_names['CitationID'] =      'Citation_ID'
