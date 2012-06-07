###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""The bmrb user function definitions."""

# Python module imports.
import wx

# relax module imports.
from graphics import WIZARD_IMAGE_PATH
from generic_fns import bmrb, exp_info, pipes
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('bmrb')
uf_class.title = "Class for interfacing with the BMRB (http://www.bmrb.wisc.edu/)."
uf_class.menu_text = "&bmrb"
uf_class.gui_icon = "relax.bmrb"

# The bmrb.citation user function.
uf = uf_info.add_uf('bmrb.citation')
uf.title = "Specify a citation to be added the BMRB data file."
uf.title_short = "Add a citation."
uf.add_keyarg(
    name = "cite_id",
    py_type = "str",
    desc_short = "citation ID",
    desc = "The citation ID string."
)
uf.add_keyarg(
    name = "authors",
    py_type = "str_list_of_lists",
    desc_short = "author list",
    desc = "The list of authors.  Each author element is a list of four elements (the first name, last name, first initial, and middle initials).",
    list_titles = ["First name", "Last name", "First initial", "Middle initials"]
)
uf.add_keyarg(
    name = "doi",
    py_type = "str",
    desc_short = "DOI number",
    desc = "The DOI number, e.g. '10.1000/182'.",
    can_be_none = True
)
uf.add_keyarg(
    name = "pubmed_id",
    py_type = "str",
    desc_short = "Pubmed ID number",
    desc = "The identification code assigned to the publication by PubMed.",
    can_be_none = True
)
uf.add_keyarg(
    name = "full_citation",
    py_type = "str",
    desc_short = "full citation",
    desc = "The full citation as given in a reference list."
)
uf.add_keyarg(
    name = "title",
    py_type = "str",
    desc_short = "publication title",
    desc = "The title of the publication."
)
uf.add_keyarg(
    name = "status",
    default = "published",
    py_type = "str",
    desc_short = "publication status",
    desc = "The status of the publication.  This can be a value such as 'published', 'submitted', etc."
)
uf.add_keyarg(
    name = "type",
    default = "journal",
    py_type = "str",
    desc_short = "publication type",
    desc = "The type of publication, for example 'journal'."
)
uf.add_keyarg(
    name = "journal_abbrev",
    py_type = "str",
    desc_short = "journal abbreviation",
    desc = "The standard journal abbreviation.",
    can_be_none = True
)
uf.add_keyarg(
    name = "journal_full",
    py_type = "str",
    desc_short = "full journal name",
    desc = "The full journal name.",
    can_be_none = True
)
uf.add_keyarg(
    name = "volume",
    py_type = "int",
    desc_short = "volume",
    desc = "The volume number.",
    can_be_none = True
)
uf.add_keyarg(
    name = "issue",
    py_type = "int",
    desc_short = "issue",
    desc = "The issue number.",
    can_be_none = True
)
uf.add_keyarg(
    name = "page_first",
    py_type = "int",
    desc_short = "first page number",
    desc = "The first page number.",
    can_be_none = True
)
uf.add_keyarg(
    name = "page_last",
    py_type = "int",
    desc_short = "last page number",
    desc = "The last page number.",
    can_be_none = True
)
uf.add_keyarg(
    name = "year",
    py_type = "int",
    desc_short = "publication year",
    desc = "The publication year."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The full_citation should be in a format similar to that used in a journal article by either cutting and pasting from another document or by typing. Please include author names, title, journal, page numbers, and year or equivalent information for the type of publication given.")
uf.desc[-1].add_paragraph("The journal status can only be one of:")
uf.desc[-1].add_list_element("'preparation',")
uf.desc[-1].add_list_element("'in press',")
uf.desc[-1].add_list_element("'published',")
uf.desc[-1].add_list_element("'retracted',")
uf.desc[-1].add_list_element("'submitted'.")
uf.desc[-1].add_paragraph("The citation type can only be one of:")
uf.desc[-1].add_list_element("'abstract',")
uf.desc[-1].add_list_element("'BMRB only',")
uf.desc[-1].add_list_element("'book',")
uf.desc[-1].add_list_element("'book chapter',")
uf.desc[-1].add_list_element("'internet',")
uf.desc[-1].add_list_element("'journal',")
uf.desc[-1].add_list_element("'personal communication',")
uf.desc[-1].add_list_element("'thesis'.")
uf.desc[-1].add_paragraph("The standard journal abbreviation is that defined by the Chemical Abstract Services for the journal where the data are or will be published.  If the data in the deposition are related to a J. Biomol. NMR paper, the value must be 'J. Biomol. NMR' to alert the BMRB annotators so that the deposition is properly processed.  If the depositor truly does not know the journal, a value of 'not known' or 'na' is acceptable.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To add the citation \"d'Auvergne E. J., Gooley P. R. (2007). Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm. Mol. Biosyst., 3(7), 483-494.\", type:")
uf.desc[-1].add_prompt("relax> bmrb.citation(authors=[[\"Edward\", \"d'Auvergne\", \"E.\", \"J.\"], [\"Paul\", \"Gooley\", \"P.\", \"R.\"]], doi=\"10.1039/b702202f\", pubmed_id=\"17579774\", full_citation=\"d'Auvergne E. J., Gooley P. R. (2007). Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm. Mol. Biosyst., 3(7), 483-494.\", title=\"Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm.\", status=\"published\", type=\"journal\", journal_abbrev=\"Mol. Biosyst.\", journal_full=\"Molecular Biosystems\", volume=3, issue=7, page_first=483, page_last=498, year=2007)")
uf.backend = exp_info.citation
uf.menu_text = "&citation"
uf.gui_icon = "oxygen.actions.documentation"
uf.wizard_size = (1000, 800)
uf.wizard_image = WIZARD_IMAGE_PATH + 'bmrb.png'


# The bmrb.display user function.
uf = uf_info.add_uf('bmrb.display')
uf.title = "Display the BMRB data in NMR-STAR format."
uf.title_short = "Display the BMRB data."
uf.display = True
uf.add_keyarg(
    name = "version",
    default = "3.1",
    py_type = "str",
    desc_short = "NMR-STAR dictionary version",
    desc = "The version of the BMRB NMR-STAR format to display.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "2.1",
        "3.0",
        "3.1"
    ],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will print the BMRB NMR-STAR formatted data to STDOUT.")
uf.backend = bmrb.display
uf.menu_text = "&display"
uf.gui_icon = "oxygen.actions.document-preview"
uf.wizard_size = (700, 500)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'bmrb.png'


# The bmrb.read user function.
uf = uf_info.add_uf('bmrb.read')
uf.title = "Read BMRB files in the NMR-STAR format."
uf.title_short = "Reading of BMRB files."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the BMRB NMR-STAR formatted file to read.",
    wiz_filesel_style = wx.FD_OPEN
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory where the file is located.",
    can_be_none = True
)
uf.add_keyarg(
    name = "version",
    py_type = "str",
    desc_short = "NMR-STAR dictionary version",
    desc = "The version of the BMRB NMR-STAR format to read.  This is not necessary as the version is normally auto-detected.",
    can_be_none = True
)
uf.add_keyarg(
    name = "sample_conditions",
    py_type = "str",
    desc_short = "sample conditions label",
    desc = "The sample conditions label in the NMR-STAR file to restrict loading to.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will allow most of the data from a BMRB NMR-STAR formatted file to be loaded into the relax data store.  Note that a data pipe should be created for storing the data, and that currently only model-free data pipes can be used.  Also, only one sample condition can be read per relax data pipe.  Therefore if one of the sample conditions is not specified and multiple conditions exist in the NMR-STAR file, an error will be raised.")
uf.backend = bmrb.read
uf.menu_text = "&read"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'bmrb.png'


# The bmrb.script user function.
uf = uf_info.add_uf('bmrb.script')
uf.title = "Specify the scripts used in the analysis."
uf.title_short = "Analysis scripts."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "script file",
    desc = "The name of the script file.",
    wiz_filesel_style = wx.FD_OPEN
)
uf.add_keyarg(
    name = "dir",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory where the file is located.",
    can_be_none = True
)
uf.add_keyarg(
    name = "analysis_type",
    py_type = "str",
    desc_short = "analysis type",
    desc = "The type of analysis performed.",
    wiz_element_type = "combo",
    wiz_combo_choices = pipes.PIPE_DESC_LIST,
    wiz_combo_data = pipes.VALID_TYPES
)
uf.add_keyarg(
    name = "model_selection",
    py_type = "str",
    desc_short = "model selection",
    desc = "The model selection technique used, if relevant.  For example 'AIC' model selection.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "AIC - Akaike's Information Criteria.",
        "AICc - Small sample size corrected AIC.",
        "BIC - Bayesian or Schwarz Information Criteria.",
        "Bootstrap - Bootstrap model selection.",
        "CV - Single-item-out cross-validation.",
        "Expect - The expected overall discrepancy (the true values of the parameters are required).",
        "Farrow - Old model-free method by Farrow et al., 1994.",
        "Palmer - Old model-free method by Mandel et al., 1995.",
        "Overall - The realised overall discrepancy (the true values of the parameters are required)."
    ],
    wiz_combo_data = ["AIC", "AICc", "BIC", "BIC", "Bootstrap", "CV", "Expect", "Farrow", "Palmer", "Overall"],
    wiz_read_only = False,
    can_be_none = True
)
uf.add_keyarg(
    name = "engine",
    default = "relax",
    py_type = "str",
    desc_short = "software engine",
    desc = "The software engine used in the analysis.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["relax", "modelfree4", "dasha", "curvefit"],
    wiz_read_only = False
)
uf.add_keyarg(
    name = "model_elim",
    default = False,
    py_type = "bool",
    desc_short = "model elimination flag",
    desc = "A model-free specific flag specifying if model elimination was performed."
)
uf.add_keyarg(
    name = "universal_solution",
    default = False,
    py_type = "bool",
    desc_short = "universal solution flag",
    desc = "A model-free specific flag specifying if the universal solution was sought after."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This user function allows scripts used in the analysis to be included in the BMRB deposition.  The following addition information may need to be specified with the script.")
uf.desc[-1].add_paragraph("The analysis type must be set.  Allowable values include all the data pipe types used in relax, ie:")
uf.desc[-1].add_item_list_element("'frame order'", "The Frame Order theories,")
uf.desc[-1].add_item_list_element("'jw'", "Reduced spectral density mapping,")
uf.desc[-1].add_item_list_element("'mf'", "Model-free analysis,")
uf.desc[-1].add_item_list_element("'N-state'", "N-state model of domain motions,")
uf.desc[-1].add_item_list_element("'noe'", "Steady state NOE calculation,")
uf.desc[-1].add_item_list_element("'relax_fit'", "Relaxation curve fitting,")
uf.desc[-1].add_paragraph("The model selection technique only needs to be set if the script selects between different mathematical models.  This can be anything, but the following are recommended:")
uf.desc[-1].add_item_list_element("'AIC'", "Akaike's Information Criteria.")
uf.desc[-1].add_item_list_element("'AICc'", "Small sample size corrected AIC.")
uf.desc[-1].add_item_list_element("'BIC'", "Bayesian or Schwarz Information Criteria.")
uf.desc[-1].add_item_list_element("'Bootstrap'", "Bootstrap model selection.")
uf.desc[-1].add_item_list_element("'CV'", "Single-item-out cross-validation.")
uf.desc[-1].add_item_list_element("'Expect'", "The expected overall discrepancy (the true values of the parameters are required).")
uf.desc[-1].add_item_list_element("'Farrow'", "Old model-free method by Farrow et al., 1994.")
uf.desc[-1].add_item_list_element("'Palmer'", "Old model-free method by Mandel et al., 1995.")
uf.desc[-1].add_item_list_element("'Overall'", "The realised overall discrepancy (the true values of the parameters are required).")
uf.desc[-1].add_paragraph("The engine is the software used in the calculation, optimisation, etc.  This can be anything, but those recognised by relax (automatic program info, citations, etc. added) include:")
uf.desc[-1].add_item_list_element("'relax'", "hence relax was used for the full analysis.")
uf.desc[-1].add_item_list_element("'modelfree4'", "Art Palmer's Modelfree4 program was used for optimising the model-free parameter values.")
uf.desc[-1].add_item_list_element("'dasha'", "The Dasha program was used for optimising the model-free parameter values.")
uf.desc[-1].add_item_list_element("'curvefit'", "Art Palmer's curvefit program was used to determine the R1 or R2 values.")
uf.desc[-1].add_paragraph("The model_elim flag is model-free specific and should be set if the methods from \"d'Auvergne, E. J. and Gooley, P. R. (2006). Model-free model elimination: A new step in the model-free dynamic analysis of NMR relaxation data. J. Biomol. NMR, 35(2), 117-135.\" were used.  This should be set to True for the full_analysis.py script.")
uf.desc[-1].add_paragraph("The universal_solution flag is model-free specific and should be set if the methods from \"d'Auvergne E. J., Gooley P. R. (2007). Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm. Mol. Biosyst., 3(7), 483-494.\" were used.  This should be set to True for the full_analysis.py script.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("For BMRB deposition, to specify that the full_analysis.py script was used, type one of:")
uf.desc[-1].add_prompt("relax> bmrb.script('full_analysis.py', 'model-free', 'AIC', 'relax', True, True)")
uf.desc[-1].add_prompt("relax> bmrb.script(file='full_analysis.py', dir=None, analysis_type='model-free', model_selection='AIC', engine='relax', model_elim=True, universal_solution=True)")
uf.backend = exp_info.script
uf.menu_text = "&script"
uf.gui_icon = "oxygen.mimetypes.application-x-desktop"
uf.wizard_size = (1000, 800)
uf.wizard_image = WIZARD_IMAGE_PATH + 'bmrb.png'


# The bmrb.software user function.
uf = uf_info.add_uf('bmrb.software')
uf.title = "Specify the software used in the analysis."
uf.title_short = "Analysis software."
uf.add_keyarg(
    name = "name",
    py_type = "str",
    desc_short = "program name",
    desc = "The name of the software program utilised."
)
uf.add_keyarg(
    name = "version",
    py_type = "str",
    desc_short = "version",
    desc = "The version of the software, if applicable.",
    can_be_none = True
)
uf.add_keyarg(
    name = "url",
    py_type = "str",
    desc_short = "URL",
    desc = "The web address of the software.",
    can_be_none = True
)
uf.add_keyarg(
    name = "vendor_name",
    py_type = "str",
    desc_short = "vendor name",
    desc = "The name of the company or person behind the program.",
    can_be_none = True
)
uf.add_keyarg(
    name = "cite_ids",
    py_type = "str_list",
    desc_short = "citation ID numbers",
    desc = "A list of the BMRB citation ID numbers.",
    can_be_none = True
)
uf.add_keyarg(
    name = "tasks",
    py_type = "str_list",
    desc_short = "tasks",
    desc = "A list of all the tasks performed by the software.",
    wiz_element_type = "combo_list",
    wiz_combo_choices = [
        'chemical shift assignment',
        'chemical shift calculation',
        'collection',
        'data analysis',
        'geometry optimization',
        'peak picking',
        'processing',
        'refinement',
        'structure solution'
    ],
    wiz_read_only = False,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This user function allows the software used in the analysis to be specified in full detail.")
uf.desc[-1].add_paragraph("For the tasks list, this should be a python list of strings (eg. ['spectral processing']).  Although not restricted to these, the values suggested by the BMRB are:")
uf.desc[-1].add_list_element("'chemical shift assignment',")
uf.desc[-1].add_list_element("'chemical shift calculation',")
uf.desc[-1].add_list_element("'collection',")
uf.desc[-1].add_list_element("'data analysis',")
uf.desc[-1].add_list_element("'geometry optimization',")
uf.desc[-1].add_list_element("'peak picking',")
uf.desc[-1].add_list_element("'processing',")
uf.desc[-1].add_list_element("'refinement',")
uf.desc[-1].add_list_element("'structure solution'")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("For BMRB deposition, to say that Sparky was used in the analysis, type:")
uf.desc[-1].add_prompt("relax> cite_id = bmrb.citation(authors=[[\"Tom\", \"Goddard\", \"T.\", \"D.\"], [\"D\", \"Kneller\", \"D.\", \"G.\"]], title=\"Goddard, T. D. and Kneller, D. G., SPARKY 3, University of California, San Francisco.\"")
uf.desc[-1].add_prompt("relax> bmrb.software(\"Sparky\", version=\"3.110\", url=\"http://www.cgl.ucsf.edu/home/sparky/\", vendor_name=\"Goddard, T. D.\", cite_ids=[cite_id], tasks=[\"spectral analysis\"])")
uf.backend = exp_info.software
uf.menu_text = "soft&ware"
uf.gui_icon = "oxygen.apps.utilities-terminal"
uf.wizard_size = (900, 800)
uf.wizard_image = WIZARD_IMAGE_PATH + 'bmrb.png'


# The bmrb.software_select user function.
uf = uf_info.add_uf('bmrb.software_select')
uf.title = "Select the software used in the analysis."
uf.title_short = "Utilised software selection."
uf.add_keyarg(
    name = "name",
    py_type = "str",
    desc_short = "program name",
    desc = "The name of the software program utilised.",
    wiz_element_type = "combo",
    wiz_combo_choices = ['NMRPipe', 'Sparky'],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "version",
    py_type = "str",
    desc_short = "version",
    desc = "The version of the software, if applicable.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Rather than specifying all the information directly, this user function allows the software packaged used in the analysis to be selected by name.  The programs currently supported are:")
uf.desc[-1].add_item_list_element("'NMRPipe'", "http://spin.niddk.nih.gov/NMRPipe/")
uf.desc[-1].add_item_list_element("'Sparky'", "http://www.cgl.ucsf.edu/home/sparky/")
uf.desc[-1].add_paragraph("More can be added if all relevant information (program name, description, website, original citation, purpose, etc.) is emailed to relax-users@gna.org.")
uf.desc[-1].add_paragraph("Note that relax is automatically added to the BMRB file.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("For BMRB deposition, to say that both NMRPipe and Sparky were used prior to relax, type:")
uf.desc[-1].add_prompt("relax> bmrb.software_select('NMRPipe')")
uf.desc[-1].add_prompt("relax> bmrb.software_select('Sparky', version='3.113')")
uf.backend = exp_info.software_select
uf.menu_text = "software_se&lect"
uf.gui_icon = "oxygen.apps.utilities-terminal"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'bmrb.png'


# The bmrb.thiol_state user function.
uf = uf_info.add_uf('bmrb.thiol_state')
uf.title = "Select the thiol state of the system."
uf.title_short = "Thiol state selection."
uf.add_keyarg(
    name = "state",
    py_type = "str",
    desc_short = "thiol state",
    desc = "The thiol state.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        'all disulfide bound',
        'all free',
        'all other bound',
        'disulfide and other bound',
        'free and disulfide bound',
        'free and other bound',
        'free disulfide and other bound',
        'not available',
        'not present',
        'not reported',
        'unknown'
    ],
    wiz_read_only = False
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The thiol state can be any text, thought the BMRB suggests the following:")
uf.desc[-1].add_list_element("'all disulfide bound',")
uf.desc[-1].add_list_element("'all free',")
uf.desc[-1].add_list_element("'all other bound',")
uf.desc[-1].add_list_element("'disulfide and other bound',")
uf.desc[-1].add_list_element("'free and disulfide bound',")
uf.desc[-1].add_list_element("'free and other bound',")
uf.desc[-1].add_list_element("'free disulfide and other bound',")
uf.desc[-1].add_list_element("'not available',")
uf.desc[-1].add_list_element("'not present',")
uf.desc[-1].add_list_element("'not reported',")
uf.desc[-1].add_list_element("'unknown'.")
uf.desc[-1].add_paragraph("Alternatively the pure states 'reduced' or 'oxidised' could be specified.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("For BMRB deposition, to say that the protein studied is in the oxidised state, tyype one of:")
uf.desc[-1].add_prompt("relax> bmrb.thiol_state('oxidised')")
uf.desc[-1].add_prompt("relax> bmrb.thiol_state(state='oxidised')")
uf.backend = exp_info.thiol_state
uf.menu_text = "&thiol_state"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 600)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'bmrb.png'


# The bmrb.write user function.
uf = uf_info.add_uf('bmrb.write')
uf.title = "Write the results to a BMRB NMR-STAR formatted file."
uf.title_short = "BMRB file writing."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the BMRB file to output results to.  Optionally this can be a file object, or any object with a write() method.",
    wiz_filesel_style = wx.FD_SAVE
)
uf.add_keyarg(
    name = "dir",
    default = "pipe_name",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory name.",
    can_be_none = True
)
uf.add_keyarg(
    name = "version",
    default = "3.1",
    py_type = "str",
    desc_short = "NMR-STAR dictionary version",
    desc = "The NMR-STAR dictionary format version to create.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "2.1",
        "3.0",
        "3.1"
    ],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    arg_type = "force flag",
    desc_short = "force flag",
    desc = "A flag which if True will cause the any pre-existing file to be overwritten."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will create a NMR-STAR formatted file of the data in the current data pipe for BMRB deposition.")
uf.desc[-1].add_paragraph("In the prompt/script UI modes, to place the BMRB file in the current working directory, set dir to None.  If dir is set to the special name 'pipe_name', then the results file will be placed into a directory with the same name as the current data pipe.")
uf.backend = bmrb.write
uf.menu_text = "&write"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (800, 600)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'bmrb.png'
