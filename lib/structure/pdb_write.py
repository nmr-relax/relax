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

# Module docstring.
"""Module for creating PDB records.

This module currently used the PDB format version 3.30 from July, 2011 U{http://www.wwpdb.org/documentation/format33/v3.3.html}.
"""

# Python module imports.
from textwrap import wrap

# relax module imports.
from lib.errors import RelaxError


def _handle_none(value):
    """Auxiliary function for handling values of None.

    @param value:   The value to convert.
    @type value:    anything
    @return:        If the value is None, then an empty string.  Otherwise the original value is returned.
    @rtype:         anything
    """

    # Handle None.
    if value == None:
        return ''

    # Normal value.
    return value


def _handle_text(text):
    """Auxiliary function for handling text values.

    This will convert None to empty strings and make sure everything is capitalised.


    @param text:    The text to convert.
    @type text:     anything
    @return:        If the text is None, then an empty string.  All text will be capitalised.
    @rtype:         anything
    """

    # Handle None.
    if text == None:
        return ''

    # Return capitalised text.
    return text.upper()


def _record_validate(record):
    """Check that the record is ok.

    @param record:      The PDB record as text.
    @type record:       str
    @raises RelaxError: If the record is not exactly 80 characters long.
    """

    # Check the length.
    if len(record) != 80:
        if len(record) < 80:
            raise RelaxError("The PDB record '%s' is too short." % record)
        else:
            raise RelaxError("The PDB record '%s' is too long." % record)


def atom(file, serial='', name='', alt_loc='', res_name='', chain_id='', res_seq='', icode='', x='', y='', z='', occupancy='', temp_factor='', element='', charge=''):
    """Generate the ATOM record.

    The following is the PDB v3.3 documentation U{http://www.wwpdb.org/documentation/format33/sect9.html#ATOM}.

    ATOM
    ====

    Overview
    --------

    The ATOM records present the atomic coordinates for standard amino acids and nucleotides.  They also present the occupancy and temperature factor for each atom.  Non-polymer chemical coordinates use the HETATM record type.  The element symbol is always present on each ATOM record; charge is optional.

    Changes in ATOM/HETATM records result from the standardization atom and residue nomenclature.  This nomenclature is described in the Chemical Component Dictionary (U{ftp://ftp.wwpdb.org/pub/pdb/data/monomers}).


    Record Format
    -------------

    The format is::
     __________________________________________________________________________________________
     |         |              |              |                                                |
     | Columns | Data type    | Field        | Definition                                     |
     |_________|______________|______________|________________________________________________|
     |         |              |              |                                                |
     |  1 -  6 | Record name  | "ATOM"       |                                                |
     |  7 - 11 | Integer      | serial       | Atom serial number.                            |
     | 13 - 16 | Atom         | name         | Atom name.                                     |
     | 17      | Character    | altLoc       | Alternate location indicator.                  |
     | 18 - 20 | Residue name | resName      | Residue name.                                  |
     | 22      | Character    | chainID      | Chain identifier.                              |
     | 23 - 26 | Integer      | resSeq       | Residue sequence number.                       |
     | 27      | AChar        | iCode        | Code for insertion of residues.                |
     | 31 - 38 | Real(8.3)    | x            | Orthogonal coordinates for X in Angstroms.     |
     | 39 - 46 | Real(8.3)    | y            | Orthogonal coordinates for Y in Angstroms.     |
     | 47 - 54 | Real(8.3)    | z            | Orthogonal coordinates for Z in Angstroms.     |
     | 55 - 60 | Real(6.2)    | occupancy    | Occupancy.                                     |
     | 61 - 66 | Real(6.2)    | tempFactor   | Temperature factor.                            |
     | 77 - 78 | LString(2)   | element      | Element symbol, right-justified.               |
     | 79 - 80 | LString(2)   | charge       | Charge on the atom.                            |
     |_________|______________|______________|________________________________________________|


    Details
    -------

    ATOM records for proteins are listed from amino to carboxyl terminus.

    Nucleic acid residues are listed from the 5' to the 3' terminus.

    Alignment of one-letter atom name such as C starts at column 14, while two-letter atom name such as FE starts at column 13.

    Atom nomenclature begins with atom type.

    No ordering is specified for polysaccharides.

    Non-blank alphanumerical character is used for chain identifier.

    The list of ATOM records in a chain is terminated by a TER record.

    If more than one model is present in the entry, each model is delimited by MODEL and ENDMDL records.

    AltLoc is the place holder to indicate alternate conformation.  The alternate conformation can be in the entire polymer chain, or several residues or partial residue (several atoms within one residue).  If an atom is provided in more than one position, then a non-blank alternate location indicator must be used for each of the atomic positions.  Within a residue, all atoms that are associated with each other in a given conformation are assigned the same alternate position indicator.  There are two ways of representing alternate conformation- either at atom level or at residue level (see examples).

    For atoms that are in alternate sites indicated by the alternate site indicator, sorting of atoms in the ATOM/HETATM list uses the following general rules:

      - In the simple case that involves a few atoms or a few residues with alternate sites, the coordinates occur one after the other in the entry.
      - In the case of a large heterogen groups which are disordered, the atoms for each conformer are listed together.

    Alphabet letters are commonly used for insertion code.  The insertion code is used when two residues have the same numbering.  The combination of residue numbering and insertion code defines the unique residue.

    If the depositor provides the data, then the isotropic B value is given for the temperature factor.

    If there are neither isotropic B values from the depositor, nor anisotropic temperature factors in ANISOU, then the default value of 0.0 is used for the temperature factor.

    Columns 79 - 80 indicate any charge on the atom, e.g., 2+, 1-.  In most cases, these are blank.

    For refinements with program REFMAC prior 5.5.0042 which use TLS refinement, the values of B may include only the TLS contribution to the isotropic temperature factor rather than the full isotropic value.


    Verification/Validation/Value Authority Control
    -----------------------------------------------

    The ATOM/HETATM records are checked for PDB file format, sequence information, and packing.


    Relationships to Other Record Types
    -----------------------------------

    The ATOM records are compared to the corresponding sequence database.  Sequence discrepancies appear in the SEQADV record.  Missing atoms are annotated in the remarks.  HETATM records are formatted in the same way as ATOM records.  The sequence implied by ATOM records must be identical to that given in SEQRES, with the exception that residues that have no coordinates, e.g., due to disorder, must appear in SEQRES.


    Example
    -------

    Example 1::

                 1         2         3         4         5         6         7         8
        12345678901234567890123456789012345678901234567890123456789012345678901234567890
        ATOM     32  N  AARG A  -3      11.281  86.699  94.383  0.50 35.88           N  
        ATOM     33  N  BARG A  -3      11.296  86.721  94.521  0.50 35.60           N  
        ATOM     34  CA AARG A  -3      12.353  85.696  94.456  0.50 36.67           C  
        ATOM     35  CA BARG A  -3      12.333  85.862  95.041  0.50 36.42           C  
        ATOM     36  C  AARG A  -3      13.559  86.257  95.222  0.50 37.37           C  
        ATOM     37  C  BARG A  -3      12.759  86.530  96.365  0.50 36.39           C  
        ATOM     38  O  AARG A  -3      13.753  87.471  95.270  0.50 37.74           O  
        ATOM     39  O  BARG A  -3      12.924  87.757  96.420  0.50 37.26           O  
        ATOM     40  CB AARG A  -3      12.774  85.306  93.039  0.50 37.25           C  
        ATOM     41  CB BARG A  -3      13.428  85.746  93.980  0.50 36.60           C  
        ATOM     42  CG AARG A  -3      11.754  84.432  92.321  0.50 38.44           C  
        ATOM     43  CG BARG A  -3      12.866  85.172  92.651  0.50 37.31           C  
        ATOM     44  CD AARG A  -3      11.698  84.678  90.815  0.50 38.51           C  
        ATOM     45  CD BARG A  -3      13.374  85.886  91.406  0.50 37.66           C  
        ATOM     46  NE AARG A  -3      12.984  84.447  90.163  0.50 39.94           N  
        ATOM     47  NE BARG A  -3      12.644  85.487  90.195  0.50 38.24           N  
        ATOM     48  CZ AARG A  -3      13.202  84.534  88.850  0.50 40.03           C  
        ATOM     49  CZ BARG A  -3      13.114  85.582  88.947  0.50 39.55           C  
        ATOM     50  NH1AARG A  -3      12.218  84.840  88.007  0.50 40.76           N  
        ATOM     51  NH1BARG A  -3      14.338  86.056  88.706  0.50 40.23           N  
        ATOM     52  NH2AARG A  -3      14.421  84.308  88.373  0.50 40.45           N  

    Example 2::

                 1         2         3         4         5         6         7         8
        12345678901234567890123456789012345678901234567890123456789012345678901234567890
        ATOM     32  N  AARG A  -3      11.281  86.699  94.383  0.50 35.88           N  
        ATOM     33  CA AARG A  -3      12.353  85.696  94.456  0.50 36.67           C  
        ATOM     34  C  AARG A  -3      13.559  86.257  95.222  0.50 37.37           C  
        ATOM     35  O  AARG A  -3      13.753  87.471  95.270  0.50 37.74           O  
        ATOM     36  CB AARG A  -3      12.774  85.306  93.039  0.50 37.25           C  
        ATOM     37  CG AARG A  -3      11.754  84.432  92.321  0.50 38.44           C  
        ATOM     38  CD AARG A  -3      11.698  84.678  90.815  0.50 38.51           C  
        ATOM     39  NE AARG A  -3      12.984  84.447  90.163  0.50 39.94           N  
        ATOM     40  CZ AARG A  -3      13.202  84.534  88.850  0.50 40.03           C  
        ATOM     41  NH1AARG A  -3      12.218  84.840  88.007  0.50 40.76           N  
        ATOM     42  NH2AARG A  -3      14.421  84.308  88.373  0.50 40.45           N  
        ATOM     43  N  BARG A  -3      11.296  86.721  94.521  0.50 35.60           N  
        ATOM     44  CA BARG A  -3      12.333  85.862  95.041  0.50 36.42           C  
        ATOM     45  C  BARG A  -3      12.759  86.530  96.365  0.50 36.39           C  
        ATOM     46  O  BARG A  -3      12.924  87.757  96.420  0.50 37.26           O  
        ATOM     47  CB BARG A  -3      13.428  85.746  93.980  0.50 36.60           C  
        ATOM     48  CG BARG A  -3      12.866  85.172  92.651  0.50 37.31           C  
        ATOM     49  CD BARG A  -3      13.374  85.886  91.406  0.50 37.66           C  
        ATOM     50  NE BARG A  -3      12.644  85.487  90.195  0.50 38.24           N  
        ATOM     51  CZ BARG A  -3      13.114  85.582  88.947  0.50 39.55           C  
        ATOM     52  NH1BARG A  -3      14.338  86.056  88.706  0.50 40.23           N  


    @param file:            The file to write the record to.
    @type file:             file object
    @keyword serial:        The atom serial number.
    @type serial:           int
    @keyword name:          The atom name.
    @type name:             str
    @keyword alt_loc:       The alternate location indicator.
    @type alt_loc:          str
    @keyword res_name:      The residue name.
    @type res_name:         str
    @keyword chain_id:      The chain identifier.
    @type chain_id:         str
    @keyword res_seq:       The sequence number.
    @type res_seq:          int
    @keyword icode:         The insertion code.
    @type icode:            str
    @keyword x:             Orthogonal coordinates for X in Angstroms.
    @type x:                float
    @keyword y:             Orthogonal coordinates for Y in Angstroms.
    @type y:                float
    @keyword z:             Orthogonal coordinates for Z in Angstroms.
    @type z:                float
    @keyword occupancy:     Occupancy.
    @type occupancy:        float
    @keyword temp_factor:   Temperature factor.
    @type temp_factor:      float
    @keyword element:       Element symbol.
    @type element:          str
    @keyword charge:        Charge on the atom.
    @type charge:           int
    """

    # The formatted record.
    text = "%-6s%5s %-4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6.2f%6.2f          %2s%2s" % (
        'ATOM',
        _handle_none(serial),
        _handle_none(name),
        _handle_none(alt_loc),
        _handle_none(res_name),
        _handle_none(chain_id),
        _handle_none(res_seq),
        _handle_none(icode),
        _handle_none(x),
        _handle_none(y),
        _handle_none(z),
        _handle_none(occupancy),
        _handle_none(temp_factor),
        _handle_none(element),
        _handle_none(charge)
    )

    # Validate.
    _record_validate(text)

    # Write out the formatted record.
    file.write(text)
    file.write('\n')


def conect(file, serial='', bonded1='', bonded2='', bonded3='', bonded4=''):
    """Generate the CONECT record.

    The following is the PDB v3.3 documentation U{http://www.wwpdb.org/documentation/format33/sect10.html#CONECT}.

    CONECT
    ======

    Overview
    --------

    The CONECT records specify connectivity between atoms for which coordinates are supplied.  The connectivity is described using the atom serial number as shown in the entry.  CONECT records are mandatory for HET groups (excluding water) and for other bonds not specified in the standard residue connectivity table.  These records are generated automatically.

    Record Format
    -------------

    The format is::
     ______________________________________________________________________________________________
     |         |              |              |                                                    |
     | Columns | Data type    | Field        | Definition                                         |
     |_________|______________|______________|____________________________________________________|
     |         |              |              |                                                    |
     |  1 -  6 | Record name  | "CONECT"     |                                                    |
     |  7 - 11 | Integer      | serial       | Atom serial number                                 |
     | 12 - 16 | Integer      | serial       | Serial number of bonded atom                       |
     | 17 - 21 | Integer      | serial       | Serial number of bonded atom                       |
     | 22 - 26 | Integer      | serial       | Serial number of bonded atom                       |
     | 27 - 31 | Integer      | serial       | Serial number of bonded atom                       |
     |_________|______________|______________|____________________________________________________|


    Details
    -------

    CONECT records are present for:

      - Intra-residue connectivity within non-standard (HET) residues (excluding water).
      - Inter-residue connectivity of HET groups to standard groups (including water) or to other HET groups.
      - Disulfide bridges specified in the SSBOND records have corresponding records.

    No differentiation is made between atoms with delocalized charges (excess negative or positive charge).

    Atoms specified in the CONECT records have the same numbers as given in the coordinate section.

    All atoms connected to the atom with serial number in columns 7 - 11 are listed in the remaining fields of the record.

    If more than four fields are required for non-hydrogen and non-salt bridges, a second CONECT record with the same atom serial number in columns 7 - 11 will be used.

    These CONECT records occur in increasing order of the atom serial numbers they carry in columns 7 - 11.  The target-atom serial numbers carried on these records also occur in increasing order.

    The connectivity list given here is redundant in that each bond indicated is given twice, once with each of the two atoms involved specified in columns 7 - 11.

    For hydrogen bonds, when the hydrogen atom is present in the coordinates, a CONECT record between the hydrogen atom and its acceptor atom is generated.

    For NMR entries, CONECT records for one model are generated describing heterogen connectivity and others for LINK records assuming that all models are homogeneous models.


    Verification/Validation/Value Authority Control
    -----------------------------------------------

    Connectivity is checked for unusual bond lengths.


    Relationships to Other Record Types
    -----------------------------------

    CONECT records must be present in an entry that contains either non-standard groups or disulfide bonds.


    Example
    -------

    Example 1::

                 1         2         3         4         5         6         7         8
        12345678901234567890123456789012345678901234567890123456789012345678901234567890
        CONECT 1179  746 1184 1195 1203
        CONECT 1179 1211 1222
        CONECT 1021  544 1017 1020 1022


    Known Problems
    --------------

    CONECT records involving atoms for which the coordinates are not present in the entry (e.g., symmetry-generated) are not given.

    CONECT records involving atoms for which the coordinates are missing due to disorder, are also not provided.


    @param file:            The file to write the record to.
    @type file:             file object
    @keyword serial:        The atom serial number.
    @type serial:           int
    @keyword bonded1:       The serial number of the bonded atom.
    @type bonded1:          int
    @keyword bonded2:       The serial number of the bonded atom.
    @type bonded2:          int
    @keyword bonded3:       The serial number of the bonded atom.
    @type bonded3:          int
    @keyword bonded4:       The serial number of the bonded atom.
    @type bonded4:          int
    """

    # The formatted record.
    text = "%-6s%5s%5s%5s%5s%5s%49s" % (
        'CONECT',
        _handle_none(serial),
        _handle_none(bonded1),
        _handle_none(bonded2),
        _handle_none(bonded3),
        _handle_none(bonded4),
        ''
    )

    # Validate.
    _record_validate(text)

    # Write out the formatted record.
    file.write(text)
    file.write('\n')


def end(file):
    """Generate the END record.

    The following is the PDB v3.3 documentation U{http://www.wwpdb.org/documentation/format33/sect11.html#END}.

    END
    ===

    Overview
    --------

    The END record marks the end of the PDB file.


    Record Format
    -------------

    The format is::
     ______________________________________________________________________________________________
     |         |              |              |                                                    |
     | Columns | Data type    | Field        | Definition                                         |
     |_________|______________|______________|____________________________________________________|
     |         |              |              |                                                    |
     |  1 -  6 | Record name  | "END   "     |                                                    |
     |_________|______________|______________|____________________________________________________|


    Details
    -------

    END is the final record of a coordinate entry.


    Verification/Validation/Value Authority Control
    -----------------------------------------------

    END must appear in every coordinate entry.


    Relationships to Other Record Types
    -----------------------------------

    This is the final record in the entry.


    Example
    -------

    Example 1::

                 1         2         3         4         5         6         7         8
        12345678901234567890123456789012345678901234567890123456789012345678901234567890
        END


    @param file:            The file to write the record to.
    @type file:             file object
    """

    # The formatted record.
    text = "END" + ' '*77

    # Validate.
    _record_validate(text)

    # Write out the formatted record.
    file.write(text)
    file.write('\n')


def endmdl(file):
    """Generate the ENDMDL record.

    The following is the PDB v3.3 documentation U{http://www.wwpdb.org/documentation/format33/v3.3.html}.

    ENDMDL
    ======

    Overview
    --------

    The ENDMDL records are paired with MODEL records to group individual structures found in a coordinate entry.


    Record Format
    -------------

    The format is::
     ______________________________________________________________________________________________
     |         |              |              |                                                    |
     | Columns | Data type    | Field        | Definition                                         |
     |_________|______________|______________|____________________________________________________|
     |         |              |              |                                                    |
     |  1 -  6 | Record name  | "ENDMDL"     |                                                    |
     |_________|______________|______________|____________________________________________________|


    Details
    -------

    MODEL/ENDMDL records are used only when more than one structure is presented in the entry, as is often the case with NMR entries.

    All the models in a multi-model entry must represent the same structure.

    Every MODEL record has an associated ENDMDL record.


    Verification/Validation/Value Authority Control
    -----------------------------------------------

    Entries with multiple structures in the NUMMDL record are checked for corresponding pairs of MODEL/ ENDMDL records, and for consecutively numbered models.


    Relationships to Other Record Types
    -----------------------------------

    There must be a corresponding MODEL record.

    In the case of an NMR entry, the NUMMDL record states the number of model structures that are present in the individual entry.


    Example
    -------

    Example 1::

                 1         2         3         4         5         6         7         8
        12345678901234567890123456789012345678901234567890123456789012345678901234567890
        ...
        ...
        ATOM  14550 1HG  GLU   122     -14.364  14.787 -14.258  1.00  0.00           H
        ATOM  14551 2HG  GLU   122     -13.794  13.738 -12.961  1.00  0.00           H
        TER   14552      GLU   122
        ENDMDL
        MODEL        9
        ATOM  14553  N   SER     1     -28.280   1.567  12.004  1.00  0.00           N
        ATOM  14554  CA  SER     1     -27.749   0.392  11.256  1.00  0.00           C
        ...
        ...
        ATOM  16369 1HG  GLU   122      -3.757  18.546  -8.439  1.00  0.00           H
        ATOM  16370 2HG  GLU   122      -3.066  17.166  -7.584  1.00  0.00           H
        TER   16371      GLU   122
        ENDMDL


    @param file:            The file to write the record to.
    @type file:             file object
    """

    # The formatted record.
    text = 'ENDMDL' + ' '*74

    # Validate.
    _record_validate(text)

    # Write out the formatted record.
    file.write(text)
    file.write('\n')


def formul(file, comp_num='', het_id='', continuation='', asterisk='', text=''):
    """Generate the FORMUL record.

    The following is the PDB v3.3 documentation U{http://www.wwpdb.org/documentation/format33/sect4.html#FORMUL}.

    FORMUL
    ======

    Overview
    --------

    The FORMUL record presents the chemical formula and charge of a non-standard group.


    Record Format
    -------------

    The format is::
     ______________________________________________________________________________________________
     |         |              |              |                                                    |
     | Columns | Data type    | Field        | Definition                                         |
     |_________|______________|______________|____________________________________________________|
     |         |              |              |                                                    |
     |  1 -  6 | Record name  | "FORMUL"     |                                                    |
     |  9 - 10 | Integer      | compNum      | Component number.                                  |
     | 13 - 15 | LString(3)   | hetID        | Het identifier.                                    |
     | 17 - 18 | Integer      | continuation | Continuation number.                               |
     | 19      | Character    | asterisk     | "*" for water.                                     |
     | 20 - 70 | String       | text         | Chemical formula.                                  |
     |_________|______________|______________|____________________________________________________|


    Details
    -------

    The elements of the chemical formula are given in the order following Hill ordering.  The order of elements depends on whether carbon is present or not.  If carbon is present, the order should be: C, then H, then the other elements in alphabetical order of their symbol.  If carbon is not present, the elements are listed purely in alphabetic order of their symbol.  This is the 'Hill' system used by Chemical Abstracts.

    The number of each atom type present immediately follows its chemical symbol without an intervening blank space.  There will be no number indicated if there is only one atom for a particular atom type.

    Each set of SEQRES records and each HET group is assigned a component number in an entry.  These numbers are assigned serially, beginning with 1 for the first set of SEQRES records.  In addition:

      - If a HET group is presented on a SEQRES record its FORMUL is assigned the component number of the chain in which it appears.
      - If the HET group occurs more than once and is not presented on SEQRES records, the component number of its first occurrence is used.

    All occurrences of the HET group within a chain are grouped together with a multiplier.  The remaining occurrences are also grouped with a multiplier.  The sum of the multipliers is the number equaling the number of times that that HET group appears in the entry.

    A continuation field is provided in the event that more space is needed for the formula.  Columns 17 - 18 are used in order to maintain continuity with the existing format.


    Verification/Validation/Value Authority Control
    -----------------------------------------------

    For each het group that appears in the entry, the corresponding HET, HETNAM, FORMUL, HETATM, and CONECT records must appear.  The FORMUL record is generated automatically by PDB processing programs using the het group template file and information from HETATM records.  UNL, UNK and UNX will not be listed in FORMUL even though these het groups present in the coordinate section.


    Relationships to Other Record Types
    -----------------------------------

    For each het group that appears in the entry, the corresponding HET, HETNAM, FORMUL, HETATM, and CONECT records must appear.


    Example
    -------

    Example 1::

                 1         2         3         4         5         6         7         8
        12345678901234567890123456789012345678901234567890123456789012345678901234567890
        FORMUL   3   MG    2(MG 2+)
        FORMUL   5  SO4    6(O4 S 2-)
        FORMUL  13  HOH   *360(H2 O)

        FORMUL   3  NAP    2(C21 H28 N7 O17 P3)
        FORMUL   4  FOL    2(C19 H19 N7 O6)
        FORMUL   5  1PE    C10 H22 O6

        FORMUL   2  NX5    C14 H10 O2 CL2 S


    @param file:            The file to write the record to.
    @type file:             file object
    @keyword comp_num:      The component number.
    @type comp_num:         int
    @keyword het_id:        The Het identifier.
    @type het_id:           str
    @keyword continuation:  Allows concatenation of multiple records.
    @type continuation:     int
    @keyword asterisk:      "*" for water.
    @type asterisk:         str
    @keyword text:          Text describing the Het group.
    @type text:             str
    """

    # The formatted record.
    text = "%-6s  %2s  %3s %2s%1s%-51s%10s" % (
        'FORMUL',
        _handle_none(comp_num),
        _handle_none(het_id),
        _handle_none(continuation),
        _handle_none(asterisk),
        _handle_none(text),
        ''
    )

    # Validate.
    _record_validate(text)

    # Write out the formatted record.
    file.write(text)
    file.write('\n')


def helix(file, ser_num='', helix_id='', init_res_name='', init_chain_id='', init_seq_num='', init_icode='', end_res_name='', end_chain_id='', end_seq_num='', end_icode='', helix_class='', comment='', length=''):
    """Generate the HELIX record.

    The following is the PDB v3.3 documentation U{http://www.wwpdb.org/documentation/format33/sect5.html#HELIX}.

    HELIX
    =====

    Overview
    --------

    HELIX records are used to identify the position of helices in the molecule.  Helices are named, numbered, and classified by type.  The residues where the helix begins and ends are noted, as well as the total length.


    Record Format
    -------------

    The format is::
     ______________________________________________________________________________________________
     |         |              |              |                                                    |
     | Columns | Data type    | Field        | Definition                                         |
     |_________|______________|______________|____________________________________________________|
     |         |              |              |                                                    |
     |  1 -  6 | Record name  | "HELIX "     |                                                    |
     |  8 - 10 | Integer      | serNum       | Serial number of the helix.  This starts at 1 and  |
     |         |              |              |      increases incrementally.                      |
     | 12 - 14 | LString(3)   | helixID      | Helix identifier.  In addition to a serial number, |
     |         |              |              |      each helix is given an alphanumeric character |
     |         |              |              |      helix identifier.                             |
     | 16 - 18 | Residue name | initResName  | Name of the initial residue.                       |
     | 20      | Character    | initChainID  | Chain identifier for the chain containing this     |
     |         |              |              |      helix.                                        |
     | 22 - 25 | Integer      | initSeqNum   | Sequence number of the initial residue.            |
     | 26      | AChar        | initICode    | Insertion code of the initial residue.             |
     | 28 - 30 | Residue name | endResName   | Name of the terminal residue of the helix.         |
     | 32      | Character    | endChainID   | Chain identifier for the chain containing this     |
     |         |              |              |      helix.                                        |
     | 34 - 37 | Integer      | endSeqNum    | Sequence number of the terminal residue.           |
     | 38      | AChar        | endICode     | Insertion code of the terminal residue.            |
     | 39 - 40 | Integer      | helixClass   | Helix class (see below).                           |
     | 41 - 70 | String       | comment      | Comment about this helix.                          |
     | 72 - 76 | Integer      | length       | Length of this helix.                              |
     |_________|______________|______________|____________________________________________________|


    Details
    -------

    Additional HELIX records with different serial numbers and identifiers occur if more than one helix is present.

    The initial residue of the helix is the N-terminal residue.

    Helices are classified as follows::

     _____________________________________________________
     |                               |  CLASS NUMBER     |
     | TYPE OF  HELIX                | (COLUMNS 39 - 40) |
     |_______________________________|___________________|
     |                               |                   |
     | Right-handed alpha (default)  |          1        |
     | Right-handed omega            |          2        |
     | Right-handed pi               |          3        |
     | Right-handed gamma            |          4        |
     | Right-handed 3 - 10           |          5        |
     | Left-handed alpha             |          6        |
     | Left-handed omega             |          7        |
     | Left-handed gamma             |          8        |
     | 2 - 7 ribbon/helix            |          9        |
     | Polyproline                   |         10        |
     |_______________________________|___________________|


    Relationships to Other Record Types
    -----------------------------------

    There may be related information in the REMARKs.


    Example
    -------

    Example 1::

                 1         2         3         4         5         6         7         8
        12345678901234567890123456789012345678901234567890123456789012345678901234567890
        HELIX    1  HA GLY A   86  GLY A   94  1                                   9
        HELIX    2  HB GLY B   86  GLY B   94  1                                   9

        HELIX   21  21 PRO J  385  LEU J  388  5                                   4
        HELIX   22  22 PHE J  397  PHE J  402  5                                   6


    @param file:            The file to write the record to.
    @type file:             file object
    @keyword ser_num:       The helix serial number
    @type ser_num:          int
    @keyword helix_id:      The helix identifier
    @type helix_id:         str
    @keyword init_res_name: The name of the initial residue
    @type init_res_name:    str
    @keyword init_chain_id: The chain identifier
    @type init_chain_id:    str
    @keyword init_seq_num:  The sequence number of the initial residue
    @type init_seq_num:     int
    @keyword init_icode:    The insertion code of the initial residue
    @type init_icode:       str
    @keyword end_res_name:  The name of the terminal residue
    @type end_res_name:     str
    @keyword end_chain_id:  The chain identifier
    @type end_chain_id:     str
    @keyword end_seq_num:   The sequence number of the terminal residue
    @type end_seq_num:      int
    @keyword end_icode:     The insertion code of the terminal residue
    @type end_icode:        str
    @keyword helix_class:   The helix class
    @type helix_class:      int
    @keyword comment:       The comment
    @type comment:          str
    @keyword length:        The helix length.
    @type length:           int
    """

    # The formatted record.
    text = "%-6s %3s %3s %3s %1s %4s%1s %3s %1s %4s%1s%2s%30s %5s    " % (
        'HELIX',
        _handle_none(ser_num),
        _handle_none(helix_id),
        _handle_none(init_res_name),
        _handle_none(init_chain_id),
        _handle_none(init_seq_num),
        _handle_none(init_icode),
        _handle_none(end_res_name),
        _handle_none(end_chain_id),
        _handle_none(end_seq_num),
        _handle_none(end_icode),
        _handle_none(helix_class),
        _handle_none(comment),
        _handle_none(length)
    )

    # Validate.
    _record_validate(text)

    # Write out the formatted record.
    file.write(text)
    file.write('\n')


def het(file, het_id='', chain_id='', seq_num='', icode='', num_het_atoms='', text=''):
    """Generate the HET record.

    The following is the PDB v3.3 documentation U{http://www.wwpdb.org/documentation/format33/sect4.html#HET}.

    HET
    ===

    Overview
    --------

    HET records are used to describe non-standard residues, such as prosthetic groups, inhibitors, solvent molecules, and ions for which coordinates are supplied.  Groups are considered HET if they are not part of a biological polymer described in SEQRES and considered to be a molecule bound to the polymer, or they are a chemical species that constitute part of a biological polymer and is not one of the following:

        - standard amino acids, or
        - standard nucleic acids (C, G, A, U, I, DC, DG, DA, DU, DT and DI), or
        - unknown amino acid (UNK) or nucleic acid (N) where UNK and N are used to indicate the unknown residue name.

    HET records also describe chemical components for which the chemical identity is unknown, in which case the group is assigned the hetID UNL (Unknown Ligand).

    The heterogen section of a PDB formatted file contains the complete description of non-standard residues in the entry.


    Record Format
    -------------

    The format is::
     ______________________________________________________________________________________________
     |         |              |              |                                                    |
     | Columns | Data type    | Field        | Definition                                         |
     |_________|______________|______________|____________________________________________________|
     |         |              |              |                                                    |
     |  1 -  6 | Record name  | "HET   "     |                                                    |
     |  8 - 10 | LString(3)   | hetID        | Het identifier, right-justified.                   |
     | 13      | Character    | ChainID      | Chain identifier.                                  |
     | 14 - 17 | Integer      | seqNum       | Sequence number.                                   |
     | 18      | AChar        | iCode        | Insertion code.                                    |
     | 21 - 25 | Integer      | numHetAtoms  | Number of HETATM records for the group present in  |
     |         |              |              | the entry.                                         |
     | 31 - 70 | String       | text         | Text describing Het group.                         |
     |_________|______________|______________|____________________________________________________|


    Details
    -------

    Each HET group is assigned a hetID of not more than three (3) alphanumeric characters.  The sequence number, chain identifier, insertion code, and number of coordinate records are given for each occurrence of the HET group in the entry.  The chemical name of the HET group is given in the HETNAM record and synonyms for the chemical name are given in the HETSYN records, see U{ftp://ftp.wwpdb.org/pub/pdb/data/monomers}.

    There is a separate HET record for each occurrence of the HET group in an entry.

    A particular HET group is represented in the PDB archive with a unique hetID.

    PDB entries do not have HET records for water molecules, deuterated water, or methanol (when used as solvent).

    Unknown atoms or ions will be represented as UNX with the chemical formula X1.  Unknown ligands are UNL; unknown amino acids are UNK.


    Verification/Validation/Value Authority Control
    -----------------------------------------------

    For each het group that appears in the entry, the wwPDB checks that the corresponding HET, HETNAM, HETSYN, FORMUL, HETATM, and CONECT records appear, if applicable.  The HET record is generated automatically using the Chemical Component Dictionary and information from the HETATM records.

    Each unique hetID represents a unique molecule.


    Relationships to Other Record Types
    -----------------------------------

    For each het group that appears in the entry, there must be corresponding HET, HETNAM, HETSYN, FORMUL,HETATM, and CONECT records.  LINK records may also be created.


    Example
    -------

    Example 1::

                 1         2         3         4         5         6         7         8
        12345678901234567890123456789012345678901234567890123456789012345678901234567890
        HET    TRS  B 975       8

        HET    UDP  A1457      25
        HET    B3P  A1458      19

        HET    NAG  Y   3      15
        HET    FUC  Y   4      10
        HET    NON  Y   5      12
        HET    UNK  A 161       1


    @param file:            The file to write the record to.
    @type file:             file object
    @keyword het_id:        The Het identifier.
    @type het_id:           str
    @keyword chain_id:      The chain identifier.
    @type chain_id:         str
    @keyword seq_num:       The sequence number.
    @type seq_num:          int
    @keyword icode:         The insertion code.
    @type icode:            str
    @keyword num_het_atoms: The number of HETATM records for the group present in the entry.
    @type num_het_atoms:    int
    @keyword text:          Text describing the Het group.
    @type text:             str
    """

    # The formatted record.
    text = "%-6s %3s  %1s%4s%1s  %5s     %-40s%10s" % (
        'HET',
        _handle_none(het_id),
        _handle_none(chain_id),
        _handle_none(seq_num),
        _handle_none(icode),
        _handle_none(num_het_atoms),
        _handle_text(text),
        ''
    )

    # Validate.
    _record_validate(text)

    # Write out the formatted record.
    file.write(text)
    file.write('\n')


def hetatm(file, serial='', name='', alt_loc='', res_name='', chain_id='', res_seq='', icode='', x='', y='', z='', occupancy='', temp_factor='', element='', charge=''):
    """Generate the HETATM record.

    The following is the PDB v3.3 documentation U{http://www.wwpdb.org/documentation/format33/sect9.html#HETATM}.

    HETATM
    ======

    Overview
    --------

    Non-polymer or other "non-standard" chemical coordinates, such as water molecules or atoms presented in HET groups use the HETATM record type.  They also present the occupancy and temperature factor for each atom.  The ATOM records present the atomic coordinates for standard residues.  The element symbol is always present on each HETATM record; charge is optional.

    Changes in ATOM/HETATM records will require standardization in atom and residue nomenclature.  This nomenclature is described in the Chemical Component Dictionary, U{ftp://ftp.wwpdb.org/pub/pdb/data/monomers}.


    Record Format
    -------------

    The format is::
     ______________________________________________________________________________________________
     |         |              |              |                                                    |
     | Columns | Data type    | Field        | Definition                                         |
     |_________|______________|______________|____________________________________________________|
     |         |              |              |                                                    |
     |  1 -  6 | Record name  | "HETATM"     |                                                    |
     |  7 - 11 | Integer      | serial       | Atom serial number.                                |
     | 13 - 16 | Atom         | name         | Atom name.                                         |
     | 17      | Character    | altLoc       | Alternate location indicator.                      |
     | 18 - 20 | Residue name | resName      | Residue name.                                      |
     | 22      | Character    | chainID      | Chain identifier.                                  |
     | 23 - 26 | Integer      | resSeq       | Residue sequence number.                           |
     | 27      | AChar        | iCode        | Code for insertion of residues.                    |
     | 31 - 38 | Real(8.3)    | x            | Orthogonal coordinates for X.                      |
     | 39 - 46 | Real(8.3)    | y            | Orthogonal coordinates for Y.                      |
     | 47 - 54 | Real(8.3)    | z            | Orthogonal coordinates for Z.                      |
     | 55 - 60 | Real(6.2)    | occupancy    | Occupancy.                                         |
     | 61 - 66 | Real(6.2)    | tempFactor   | Temperature factor.                                |
     | 77 - 78 | LString(2)   | element      | Element symbol; right-justified.                   |
     | 79 - 80 | LString(2)   | charge       | Charge on the atom.                                |
     |_________|______________|______________|____________________________________________________|


    Details
    -------

    The x, y, z coordinates are in Angstrom units.

    No ordering is specified for polysaccharides.

    See the HET section of this document regarding naming of heterogens.  See the Chemical Component Dictionary for residue names, formulas, and topology of the HET groups that have appeared so far in the PDB (see U{ftp://ftp.wwpdb.org/pub/pdb/data/monomers}).

    If the depositor provides the data, then the isotropic B value is given for the temperature factor.

    If there are neither isotropic B values provided by the depositor, nor anisotropic temperature factors in ANISOU, then the default value of 0.0 is used for the temperature factor.

    Insertion codes and element naming are fully described in the ATOM section of this document.


    Verification/Validation/Value Authority Control
    -----------------------------------------------

    Processing programs check ATOM/HETATM records for PDB file format, sequence information, and packing.


    Relationships to Other Record Types
    -----------------------------------

    HETATM records must have corresponding HET, HETNAM, FORMUL and CONECT records, except for waters.


    Example
    -------

    Example 1::

                 1         2         3         4         5         6         7         8
        12345678901234567890123456789012345678901234567890123456789012345678901234567890
        HETATM 8237 MG    MG A1001      13.872  -2.555 -29.045  1.00 27.36          MG

        HETATM 3835 FE   HEM A   1      17.140   3.115  15.066  1.00 14.14          FE
        HETATM 8238  S   SO4 A2001      10.885 -15.746 -14.404  1.00 47.84           S
        HETATM 8239  O1  SO4 A2001      11.191 -14.833 -15.531  1.00 50.12           O
        HETATM 8240  O2  SO4 A2001       9.576 -16.338 -14.706  1.00 48.55           O
        HETATM 8241  O3  SO4 A2001      11.995 -16.703 -14.431  1.00 49.88           O
        HETATM 8242  O4  SO4 A2001      10.932 -15.073 -13.100  1.00 49.91           O


    @param file:            The file to write the record to.
    @type file:             file object
    @keyword serial:        The atom serial number.
    @type serial:           int
    @keyword name:          The atom name.
    @type name:             str
    @keyword alt_loc:       The alternate location indicator.
    @type alt_loc:          str
    @keyword res_name:      The residue name.
    @type res_name:         str
    @keyword chain_id:      The chain identifier.
    @type chain_id:         str
    @keyword res_seq:       The sequence number.
    @type res_seq:          int
    @keyword icode:         The insertion code.
    @type icode:            str
    @keyword x:             Orthogonal coordinates for X in Angstroms.
    @type x:                float
    @keyword y:             Orthogonal coordinates for Y in Angstroms.
    @type y:                float
    @keyword z:             Orthogonal coordinates for Z in Angstroms.
    @type z:                float
    @keyword occupancy:     Occupancy.
    @type occupancy:        float
    @keyword temp_factor:   Temperature factor.
    @type temp_factor:      float
    @keyword element:       Element symbol.
    @type element:          str
    @keyword charge:        Charge on the atom.
    @type charge:           int
    """

    # The formatted record.
    text = "%-6s%5s %4s%1s%3s %1s%4s%1s   %8.3f%8.3f%8.3f%6.2f%6.2f          %2s%2s" % (
        'HETATM',
        _handle_none(serial),
        _handle_none(name),
        _handle_none(alt_loc),
        _handle_none(res_name),
        _handle_none(chain_id),
        _handle_none(res_seq),
        _handle_none(icode),
        _handle_none(x),
        _handle_none(y),
        _handle_none(z),
        _handle_none(occupancy),
        _handle_none(temp_factor),
        _handle_none(element),
        _handle_none(charge)
    )

    # Validate.
    _record_validate(text)

    # Write out the formatted record.
    file.write(text)
    file.write('\n')


def hetnam(file, continuation='', het_id='', text=''):
    """Generate the HETNAM record.

    The following is the PDB v3.3 documentation U{http://www.wwpdb.org/documentation/format33/sect4.html#HETNAM}.

    HETNAM
    ======

    Overview
    --------

    This record gives the chemical name of the compound with the given hetID.


    Record Format
    -------------

    The format is::
     ______________________________________________________________________________________________
     |         |              |              |                                                    |
     | Columns | Data type    | Field        | Definition                                         |
     |_________|______________|______________|____________________________________________________|
     |         |              |              |                                                    |
     |  1 -  6 | Record name  | "HETNAM"     |                                                    |
     |  9 - 10 | Continuation | continuation | Allows concatenation of multiple records.          |
     | 12 - 14 | LString(3)   | hetID        | Het identifier, right-justified.                   |
     | 16 - 70 | String       | text         | Chemical name.                                     |
     |_________|______________|______________|____________________________________________________|


    Details
    -------

    Each hetID is assigned a unique chemical name for the HETNAM record, see U{ftp://ftp.wwpdb.org/pub/pdb/data/monomers}.

    Other names for the group are given on HETSYN records.

    PDB entries follow IUPAC/IUB naming conventions to describe groups systematically.

    The special character "~" is used to indicate superscript in a heterogen name.  For example: N6 will be listed in the HETNAM section as N~6~, with the ~ character indicating both the start and end of the superscript in the name, e.g.:

      - N-(BENZYLSULFONYL)SERYL-N~1~-{4-[AMINO(IMINO)METHYL]BENZYL}GLYCINAMIDE

    Continuation of chemical names onto subsequent records is allowed.

    Only one HETNAM record is included for a given hetID, even if the same hetID appears on more than one HET record.


    Verification/Validation/Value Authority Control
    -----------------------------------------------

    For each het group that appears in the entry, the corresponding HET, HETNAM, FORMUL, HETATM, and CONECT records must appear.  The HETNAM record is generated automatically using the Chemical Component Dictionary and information from HETATM records.


    Relationships to Other Record Types
    -----------------------------------

    For each het group that appears in the entry, there must be corresponding HET, HETNAM, FORMUL, HETATM, and CONECT records.  HETSYN and LINK records may also be created.


    Example
    -------

    Example 1::

                 1         2         3         4         5         6         7         8
        12345678901234567890123456789012345678901234567890123456789012345678901234567890
        HETNAM     NAG N-ACETYL-D-GLUCOSAMINE
        HETNAM     SAD BETA-METHYLENE SELENAZOLE-4-CARBOXAMIDE ADENINE
        HETNAM  2  SAD DINUCLEOTIDE

        HETNAM     UDP URIDINE-5'-DIPHOSPHATE

        HETNAM     UNX UNKNOWN ATOM OR ION
        HETNAM     UNL UNKNOWN LIGAND

        HETNAM     B3P 2-[3-(2-HYDROXY-1,1-DIHYDROXYMETHYL-ETHYLAMINO)-
        HETNAM   2 B3P  PROPYLAMINO]-2-HYDROXYMETHYL-PROPANE-1,3-DIOL


    @param file:            The file to write the record to.
    @type file:             file object
    @keyword continuation:  Allows concatenation of multiple records.
    @type continuation:     int
    @keyword het_id:        The Het identifier.
    @type het_id:           str
    @keyword text:          The chemical name.
    @type text:             str
    """

    # The formatted record.
    text = "%-6s  %2s %3s %-55s%10s" % (
        'HETNAM',
        _handle_none(continuation),
        _handle_none(het_id),
        _handle_text(text),
        ''
    )

    # Validate.
    _record_validate(text)

    # Write out the formatted record.
    file.write(text)
    file.write('\n')


def master(file, num_remark=0, num_het=0, num_helix=0, num_sheet=0, num_turn=0, num_site=0, num_xform=0, num_coord=0, num_ter=0, num_conect=0, num_seq=0):
    """Generate the MASTER record.

    The following is the PDB v3.3 documentation U{http://www.wwpdb.org/documentation/format33/sect11.html#MASTER}.

    MASTER
    ======

    Overview
    --------

    The MASTER record is a control record for bookkeeping.  It lists the number of lines in the coordinate entry or file for selected record types.  MASTER records only the first model when there are multiple models in the coordinates.


    Record Format
    -------------

    The format is::
     ______________________________________________________________________________________________
     |         |              |              |                                                    |
     | Columns | Data type    | Field        | Definition                                         |
     |_________|______________|______________|____________________________________________________|
     |         |              |              |                                                    |
     |  1 -  6 | Record name  | "MASTER"     |                                                    |
     | 11 - 15 | Integer      | numRemark    | Number of REMARK records                           |
     | 16 - 20 | Integer      | "0"          |                                                    |
     | 21 - 25 | Integer      | numHet       | Number of HET records                              |
     | 26 - 30 | Integer      | numHelix     | Number of HELIX records                            |
     | 31 - 35 | Integer      | numSheet     | Number of SHEET records                            |
     | 36 - 40 | Integer      | numTurn      | deprecated                                         |
     | 41 - 45 | Integer      | numSite      | Number of SITE records                             |
     | 46 - 50 | Integer      | numXform     | Number of coordinate transformation records        |
     |         |              |              | (ORIGX+SCALE+MTRIX)                                |
     | 51 - 55 | Integer      | numCoord     | Number of atomic coordinate records (ATOM+HETATM)  |
     | 56 - 60 | Integer      | numTer       | Number of TER records                              |
     | 61 - 65 | Integer      | numConect    | Number of CONECT records                           |
     | 66 - 70 | Integer      | numSeq       | Number of SEQRES records                           |
     |_________|______________|______________|____________________________________________________|


    Details
    -------

    MASTER gives checksums of the number of records in the entry, for selected record types.

    MASTER records only the first model when there are multiple models in the coordinates.


    Verification/Validation/Value Authority Control
    -----------------------------------------------

    The MASTER line is automatically generated.


    Relationships to Other Record Types
    -----------------------------------

    MASTER presents a checksum of the lines present for each of the record types listed above.


    Example
    -------

    Example 1::

                 1         2         3         4         5         6         7         8
        12345678901234567890123456789012345678901234567890123456789012345678901234567890
        MASTER       40    0    0    0    0    0    0    6 2930    2    0   29          


    @param file:            The file to write the record to.
    @type file:             file object
    @keyword num_remark:    The number of REMARK records.
    @type num_remark:       int
    @keyword num_het:       The number of HET records.
    @type num_het:          int
    @keyword num_helix:     The number of HELIX records.
    @type num_helix:        int
    @keyword num_sheet:     The number of SHEET records.
    @type num_sheet:        int
    @keyword num_turn:      Depreciated.
    @type num_turn:         int
    @keyword num_site:      The number of SITE records.
    @type num_site:         int
    @keyword num_xform:     The number of coordinate transformation records (ORIGX+SCALE+MTRIX).
    @type num_xform:        int
    @keyword num_coord:     The number of atomic coordinate records (ATOM+HETATM).
    @type num_coord:        int
    @keyword num_ter:       The number of TER records.
    @type num_ter:          int
    @keyword num_conect:    The number of CONECT records.
    @type num_conect:       int
    @keyword num_seq        The number of SEQRES records.
    @type num_seq           int
    """

    # The formatted record.
    text = "%-6s    %5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%10s" % (
        'MASTER',
        _handle_none(num_remark),
        0,
        _handle_none(num_het),
        _handle_none(num_helix),
        _handle_none(num_sheet),
        _handle_none(num_turn),
        _handle_none(num_site),
        _handle_none(num_xform),
        _handle_none(num_coord),
        _handle_none(num_ter),
        _handle_none(num_conect),
        _handle_none(num_seq),
        ''
    )

    # Validate.
    _record_validate(text)

    # Write out the formatted record.
    file.write(text)
    file.write('\n')


def model(file, serial=''):
    """Generate the MODEL record.

    The following is the PDB v3.3 documentation U{http://www.wwpdb.org/documentation/format33/sect9.html#MODEL}.

    MODEL
    =====

    Overview
    --------

    The MODEL record specifies the model serial number when multiple models of the same structure are presented in a single coordinate entry, as is often the case with structures determined by NMR.


    Record Format
    -------------

    The format is::
     ______________________________________________________________________________________________
     |         |              |              |                                                    |
     | Columns | Data type    | Field        | Definition                                         |
     |_________|______________|______________|____________________________________________________|
     |         |              |              |                                                    |
     |  1 -  6 | Record name  | "MODEL "     |                                                    |
     | 11 - 14 | Integer      | serial       | Model serial number.                               |
     |_________|______________|______________|____________________________________________________|


    Details
    -------

    This record is used only when more than one model appears in an entry.  Generally, it is employed mainly for NMR structures.  The chemical connectivity should be the same for each model.  ATOM, HETATM, ANISOU, and TER records for each model structure and are interspersed as needed between MODEL and ENDMDL records.

    The numbering of models is sequential, beginning with 1.

    All models in a deposition should be superimposed in an appropriate author determined manner and only one superposition method should be used.  Structures from different experiments, or different domains of a structure should not be superimposed and deposited as models of a deposition.

    All models in an NMR ensemble should be homogeneous - each model should have the exact same atoms (hydrogen and heavy atoms), sequence and chemistry.

    All models in an NMR entry should have hydrogen atoms.

    Deposition of minimized average structure must be accompanied with ensemble and must be homogeneous with ensemble.

    A model cannot have more than 99,999 atoms.  Where the entry does not contain an ensemble of models, then the entry cannot have more than 99,999 atoms.  Entries that go beyond this atom limit must be split into multiple entries, each containing no more than the limits specified above.


    Verification/Validation/Value Authority Control
    -----------------------------------------------

    Entries with multiple models in the NUMMDL record are checked for corresponding pairs of MODEL/ ENDMDL records, and for consecutively numbered models.


    Relationships to Other Record Types
    -----------------------------------

    Each MODEL must have a corresponding ENDMDL record.


    Examples
    --------

    Example 1::

                 1         2         3         4         5         6         7         8
        12345678901234567890123456789012345678901234567890123456789012345678901234567890
        MODEL        1
        ATOM      1  N   ALA A   1      11.104   6.134  -6.504  1.00  0.00           N
        ATOM      2  CA  ALA A   1      11.639   6.071  -5.147  1.00  0.00           C
        ...
        ...
        ...
        ATOM    293 1HG  GLU A   18    -14.861  -4.847   0.361  1.00  0.00           H
        ATOM    294 2HG  GLU A   18    -13.518  -3.769   0.084  1.00  0.00           H
        TER     295      GLU A   18
        ENDMDL
        MODEL        2
        ATOM    296  N   ALA  A   1     10.883   6.779  -6.464  1.00  0.00           N
        ATOM    297  CA  ALA  A   1     11.451   6.531  -5.142  1.00  0.00           C
        ...
        ...
        ATOM    588 1HG  GLU A   18    -13.363  -4.163  -2.372  1.00  0.00           H
        ATOM    589 2HG  GLU A   18    -12.634  -3.023  -3.475  1.00  0.00           H
        TER     590      GLU A   18
        ENDMDL

    Example 2::

                 1         2         3         4         5         6         7         8
        12345678901234567890123456789012345678901234567890123456789012345678901234567890
        MODEL        1
        ATOM      1  N  AALA A   1      72.883  57.697  56.410  0.50 83.80           N
        ATOM      2  CA AALA A   1      73.796  56.531  56.644  0.50 84.78           C
        ATOM      3  C  AALA A   1      74.549  56.551  57.997  0.50 85.05           C
        ATOM      4  O  AALA A   1      73.951  56.413  59.075  0.50 84.77           O
        ...
        ...
        ...
        HETATM37900  O  AHOH   490     -24.915 147.513  36.413  0.50 41.86           O
        HETATM37901  O  AHOH   491     -28.699 130.471  22.248  0.50 36.06           O
        HETATM37902  O  AHOH   492     -33.309 184.488  26.176  0.50 15.00           O
        ENDMDL
        MODEL        2
        ATOM      1  N  BALA A   1      72.883  57.697  56.410  0.50 83.80           N
        ATOM      2  CA BALA A   1      73.796  56.531  56.644  0.50 84.78           C
        ATOM      3  C  BALA A   1      74.549  56.551  57.997  0.50 85.05           C
        ATOM      4  O  BALA A   1      73.951  56.413  59.075  0.50 84.77           O
        ATOM      5  CB BALA A   1      74.804  56.369  55.453  0.50 84.29           C
        ATOM      6  N  BASP A   2      75.872  56.703  57.905  0.50 85.59           N
        ATOM      7  CA BASP A   2      76.801  56.651  59.048  0.50 85.67           C
        ATOM      8  C  BASP A   2      76.283  57.361  60.309  0.50 84.80           C
        ...


    @param file:            The file to write the record to.
    @type file:             file object
    @keyword serial:        The model serial number.
    @type serial:           int
    """

    # The formatted record.
    text = "%-6s    %4i%66s" % (
        'MODEL',
        _handle_none(serial),
        ''
    )

    # Validate.
    _record_validate(text)

    # Write out the formatted record.
    file.write(text)
    file.write('\n')


def remark(file, num='', remark=''):
    """Generate the REMARK record.

    The following is the PDB v3.3 documentation U{http://www.wwpdb.org/documentation/format33/remarks.html}.

    REMARK
    ======

    Overview
    --------

    REMARK records present experimental details, annotations, comments, and information not included in other records.  In a number of cases, REMARKs are used to expand the contents of other record types.  A new level of structure is being used for some REMARK records.  This is expected to facilitate searching and will assist in the conversion to a relational database.

    The very first line of every set of REMARK records is used as a spacer to aid in reading::

     ______________________________________________________________________________________________
     |         |             |             |                                                      |
     | Columns | Data type   | Field       | Definition                                           |
     |_________|_____________|_____________|______________________________________________________|
     |         |             |             |                                                      |
     |  1 -  6 | Record name | "REMARK"    |                                                      |
     |  8 - 10 | Integer     | remarkNum   | Remark number.  It is not an error for remark n to   |
     |         |             |             | exist in an entry when remark n-1 does not.          |
     | 12 - 79 | LString     | empty       | Left as white space in first line of each new        |
     |         |             |             | remark.                                              |
     |_________|_____________|_____________|______________________________________________________|


    @param file:        The file to write the record to.
    @type file:         file object
    @keyword num:       The remarkNum value.
    @type num:          int
    @keyword remark:    The remark.
    @type remark:       str
    """

    # Initialise.
    lines = []

    # Handle empty lines.
    if remark == None:
        lines.append("%-6s %3s %-68s " % ("REMARK", num, ''))

    # The formatted record, splitting across lines if needed.
    else:
        for line in wrap(remark, 68):
            lines.append("%-6s %3s %-68s " % ("REMARK", num, line.upper()))

    # Output all lines.
    for text in lines:
        # Validate.
        _record_validate(text)

        # Write out the formatted record.
        file.write(text)
        file.write('\n')


def sheet(file, strand='', sheet_id='', num_strands='', init_res_name='', init_chain_id='', init_seq_num='', init_icode='', end_res_name='', end_chain_id='', end_seq_num='', end_icode='', sense='', cur_atom='', cur_res_name='', cur_chain_id='', cur_res_seq='', cur_icode='', prev_atom='', prev_res_name='', prev_chain_id='', prev_res_seq='', prev_icode=''):
    """Generate the SHEET record.

    The following is the PDB v3.3 documentation U{http://www.wwpdb.org/documentation/format33/sect5.html#SHEET}.

    SHEET
    =====

    Overview
    --------

    SHEET records are used to identify the position of sheets in the molecule.  Sheets are both named and numbered.  The residues where the sheet begins and ends are noted.


    Record Format
    -------------

    The format is::
     ______________________________________________________________________________________________
     |         |              |              |                                                    |
     | Columns | Data type    | Field        | Definition                                         |
     |_________|______________|______________|____________________________________________________|
     |         |              |              |                                                    |
     |  1 -  6 | Record name  | "SHEET "     |                                                    |
     |  8 - 10 | Integer      | strand       | Strand number which starts at 1 for each strand    |
     |         |              |              | within a sheet and increases by one.               |
     | 12 - 14 | LString(3)   | sheetID      | Sheet identifier.                                  |
     | 15 - 16 | Integer      | numStrands   | Number of strands in sheet.                        |
     | 18 - 20 | Residue name | initResName  | Residue name of initial residue.                   |
     | 22      | Character    | initChainID  | Chain identifier of initial residue in strand.     |
     | 23 - 26 | Integer      | initSeqNum   | Sequence number of initial residue in strand.      |
     | 27      | AChar        | initICode    | Insertion code of initial residue in strand.       |
     | 29 - 31 | Residue name | endResName   | Residue name of terminal residue.                  |
     | 33      | Character    | endChainID   | Chain identifier of terminal residue.              |
     | 34 - 37 | Integer      | endSeqNum    | Sequence number of terminal residue.               |
     | 38      | AChar        | endICode     | Insertion code of terminal residue.                |
     | 39 - 40 | Integer      | sense        | Sense of strand with respect to previous strand in |
     |         |              |              | the sheet. 0 if first strand, 1 if parallel, and   |
     |         |              |              | -1 if anti-parallel.                               |
     | 42 - 45 | Atom         | curAtom      | Registration.  Atom name in current strand.        |
     | 46 - 48 | Residue name | curResName   | Registration.  Residue name in current strand.     |
     | 50      | Character    | curChainId   | Registration.  Chain identifier in current strand. |
     | 51 - 54 | Integer      | curResSeq    | Registration.  Residue sequence number in current  |
     |         |              |              | strand.                                            |
     | 55      | AChar        | curICode     | Registration.  Insertion code in current strand.   |
     | 57 - 60 | Atom         | prevAtom     | Registration.  Atom name in previous strand.       |
     | 61 - 63 | Residue name | prevResName  | Registration.  Residue name in previous strand.    |
     | 65      | Character    | prevChainId  | Registration.  Chain identifier in previous strand.|
     | 66 - 69 | Integer      | prevResSeq   | Registration.  Residue sequence number in previous |
     |         |              |              | strand.                                            |
     | 70      | AChar        | prevICode    | Registration.  Insertion code in previous strand.  |
     |_________|______________|______________|____________________________________________________|


    Details
    -------

    The initial residue for a strand is its N-terminus.  Strand registration information is provided in columns 39 - 70.  Strands are listed starting with one edge of the sheet and continuing to the spatially adjacent strand.

    The sense in columns 39 - 40 indicates whether strand n is parallel (sense = 1) or anti-parallel (sense = -1) to strand n-1.  Sense is equal to zero (0) for the first strand of a sheet.

    The registration (columns 42 - 70) of strand n to strand n-1 may be specified by one hydrogen bond between each such pair of strands.  This is done by providing the hydrogen bonding between the current and previous strands.  No register information should be provided for the first strand.

    Split strands, or strands with two or more runs of residues from discontinuous parts of the amino acid sequence, are explicitly listed.  Detail description can be included in the REMARK 700.


    Relationships to Other Record Types
    -----------------------------------

    If the entry contains bifurcated sheets or beta-barrels, the relevant REMARK 700 records must be provided.  See the REMARK section for details.


    Examples
    --------

    Example 1::

                 1         2         3         4         5         6         7         8
        12345678901234567890123456789012345678901234567890123456789012345678901234567890
        SHEET    1   A 5 THR A 107  ARG A 110  0
        SHEET    2   A 5 ILE A  96  THR A  99 -1  N  LYS A  98   O  THR A 107
        SHEET    3   A 5 ARG A  87  SER A  91 -1  N  LEU A  89   O  TYR A  97
        SHEET    4   A 5 TRP A  71  ASP A  75 -1  N  ALA A  74   O  ILE A  88
        SHEET    5   A 5 GLY A  52  PHE A  56 -1  N  PHE A  56   O  TRP A  71
        SHEET    1   B 5 THR B 107  ARG B 110  0
        SHEET    2   B 5 ILE B  96  THR B  99 -1  N  LYS B  98   O  THR B 107
        SHEET    3   B 5 ARG B  87  SER B  91 -1  N  LEU B  89   O  TYR B  97
        SHEET    4   B 5 TRP B  71  ASP B  75 -1  N  ALA B  74   O  ILE B  88
        SHEET    5   B 5 GLY B  52  ILE B  55 -1  N  ASP B  54   O  GLU B  73

    The sheet presented as BS1 below is an eight-stranded beta-barrel.  This is represented by a nine-stranded sheet in which the first and last strands are identical::

        SHEET    1 BS1 9  VAL   13  ILE    17  0                               
        SHEET    2 BS1 9  ALA   70  ILE    73  1  O  TRP    72   N  ILE    17  
        SHEET    3 BS1 9  LYS  127  PHE   132  1  O  ILE   129   N  ILE    73  
        SHEET    4 BS1 9  GLY  221  ASP   225  1  O  GLY   221   N  ILE   130  
        SHEET    5 BS1 9  VAL  248  GLU   253  1  O  PHE   249   N  ILE   222  
        SHEET    6 BS1 9  LEU  276  ASP   278  1  N  LEU   277   O  GLY   252  
        SHEET    7 BS1 9  TYR  310  THR   318  1  O  VAL   317   N  ASP   278  
        SHEET    8 BS1 9  VAL  351  TYR   356  1  O  VAL   351   N  THR   318  
        SHEET    9 BS1 9  VAL   13  ILE    17  1  N  VAL    14   O  PRO   352  

    The sheet structure of this example is bifurcated.  In order to represent this feature, two sheets are defined.  Strands 2 and 3 of BS7 and BS8 are identical::

        SHEET    1 BS7 3  HIS  662  THR   665  0                               
        SHEET    2 BS7 3  LYS  639  LYS   648 -1  N  PHE   643   O  HIS   662  
        SHEET    3 BS7 3  ASN  596  VAL   600 -1  N  TYR   598   O  ILE   646  
        SHEET    1 BS8 3  ASN  653  TRP   656  0                               
        SHEET    2 BS8 3  LYS  639  LYS   648 -1  N  LYS   647   O  THR   655  
        SHEET    3 BS8 3  ASN  596  VAL   600 -1  N  TYR   598   O  ILE   646  


    @param file:            The file to write the record to.
    @type file:             file object
    @keyword strand:        The strand number.
    @type strand:           int
    @keyword sheet_id:      The sheet identifier.
    @type sheet_id:         str
    @keyword num_strands:   The number of strands in sheet.
    @type num_strands:      int
    @keyword init_res_name: The residue name of initial residue.
    @type init_res_name:    str
    @keyword init_chain_id: The chain identifier of initial residue in strand.
    @type init_chain_id:    str
    @keyword init_seq_num:  The sequence number of initial residue in strand.
    @type init_seq_num:     int
    @keyword init_icode:    The insertion code of initial residue in strand.
    @type init_icode:       str
    @keyword end_res_name:  The residue name of terminal residue.
    @type end_res_name:     str
    @keyword end_chain_id:  The chain identifier of terminal residue.
    @type end_chain_id:     str
    @keyword end_seq_num:   The sequence number of terminal residue.
    @type end_seq_num:      int
    @keyword end_icode:     The insertion code of terminal residue.
    @type end_icode:        str
    @keyword sense:         The sense of strand with respect to previous strand.
    @type sense:            int
    @keyword cur_atom:      The atom name in current strand.
    @type cur_atom:         str
    @keyword cur_res_name:  The residue name in current strand.
    @type cur_res_name:     str
    @keyword cur_chain_id:  The chain identifier in current strand.
    @type cur_chain_id:     str
    @keyword cur_res_seq:   The residue sequence number in current strand.
    @type cur_res_seq:      int
    @keyword cur_icode:     The insertion code in current strand.
    @type cur_icode:        str
    @keyword prev_atom:     The atom name in previous strand.
    @type prev_atom:        str
    @keyword prev_res_name: The residue name in previous strand.
    @type prev_res_name:    str
    @keyword prev_chain_id: The chain identifier in previous strand.
    @type prev_chain_id:    str
    @keyword prev_res_seq:  The residue sequence number in previous strand.
    @type prev_res_seq:     int
    @keyword prev_icode:    The insertion code in previous strand.
    @type prev_icode:       str
    """

    # The formatted record.
    text = "%-6s %3s %3s%2s %3s %1s%4s%1s %3s %1s%4s%1s%2s %4s%3s %1s%4s%1s %4s%3s %1s%4s%1s%10s" % (
        'SHEET',
        _handle_none(strand),
        _handle_none(sheet_id),
        _handle_none(num_strands),
        _handle_none(init_res_name),
        _handle_none(init_chain_id),
        _handle_none(init_seq_num),
        _handle_none(init_icode),
        _handle_none(end_res_name),
        _handle_none(end_chain_id),
        _handle_none(end_seq_num),
        _handle_none(end_icode),
        _handle_none(sense),
        _handle_none(cur_atom),
        _handle_none(cur_res_name),
        _handle_none(cur_chain_id),
        _handle_none(cur_res_seq),
        _handle_none(cur_icode),
        _handle_none(prev_atom),
        _handle_none(prev_res_name),
        _handle_none(prev_chain_id),
        _handle_none(prev_res_seq),
        _handle_none(prev_icode),
        ''
    )

    # Validate.
    _record_validate(text)

    # Write out the formatted record.
    file.write(text)
    file.write('\n')


def ter(file, serial='', res_name='', chain_id='', res_seq='', icode=''):
    """Generate the TER record.

    The following is the PDB v3.3 documentation U{http://www.wwpdb.org/documentation/format33/sect9.html#TER}.

    TER
    ===

    Overview
    --------

    The TER record indicates the end of a list of ATOM/HETATM records for a chain.


    Record Format
    -------------

    The format is::
     ______________________________________________________________________________________________
     |         |              |              |                                                    |
     | Columns | Data type    | Field        | Definition                                         |
     |_________|______________|______________|____________________________________________________|
     |         |              |              |                                                    |
     |  1 -  6 | Record name  | "TER   "     |                                                    |
     |  7 - 11 | Integer      | serial       | Serial number.                                     |
     | 18 - 20 | Residue name | resName      | Residue name.                                      |
     | 22      | Character    | chainID      | Chain identifier.                                  |
     | 23 - 26 | Integer      | resSeq       | Residue sequence number.                           |
     | 27      | AChar        | iCode        | Insertion code.                                    |
     |_________|______________|______________|____________________________________________________|


    Details
    -------

    Every chain of ATOM/HETATM records presented on SEQRES records is terminated with a TER record.

    The TER records occur in the coordinate section of the entry, and indicate the last residue presented for each polypeptide and/or nucleic acid chain for which there are determined coordinates.  For proteins, the residue defined on the TER record is the carboxy-terminal residue; for nucleic acids it is the 3'-terminal residue.

    For a cyclic molecule, the choice of termini is arbitrary.

    Terminal oxygen atoms are presented as OXT for proteins, and as O5' or OP3 for nucleic acids.  These atoms are present only if the last residue in the polymer is truly the last residue in the SEQRES.

    The TER record has the same residue name, chain identifier, sequence number and insertion code as the terminal residue.  The serial number of the TER record is one number greater than the serial number of the ATOM/HETATM preceding the TER.


    Verification/Validation/Value Authority Control
    -----------------------------------------------

    TER must appear at the terminal carboxyl end or 3' end of a chain.  For proteins, there is usually a terminal oxygen, labeled OXT.  The validation program checks for the occurrence of TER and OXT records.


    Relationships to Other Record Types
    -----------------------------------

    The residue name appearing on the TER record must be the same as the residue name of the immediately preceding ATOM or non-water HETATM record.


    Example
    -------

    Example 1::

                 1         2         3         4         5         6         7         8
        12345678901234567890123456789012345678901234567890123456789012345678901234567890
        ATOM    601  N   LEU A  75     -17.070 -16.002   2.409  1.00 55.63           N
        ATOM    602  CA  LEU A  75     -16.343 -16.746   3.444  1.00 55.50           C
        ATOM    603  C   LEU A  75     -16.499 -18.263   3.300  1.00 55.55           C
        ATOM    604  O   LEU A  75     -16.645 -18.789   2.195  1.00 55.50           O
        ATOM    605  CB  LEU A  75     -16.776 -16.283   4.844  1.00 55.51           C
        TER     606      LEU A  75
        ...
        ATOM   1185  O   LEU B  75      26.292  -4.310  16.940  1.00 55.45           O
        ATOM   1186  CB  LEU B  75      23.881  -1.551  16.797  1.00 55.32           C
        TER    1187      LEU B  75
        HETATM 1188  H2  SRT A1076     -17.263  11.260  28.634  1.00 59.62           H
        HETATM 1189  HA  SRT A1076     -19.347  11.519  28.341  1.00 59.42           H
        HETATM 1190  H3  SRT A1076     -17.157  14.303  28.677  1.00 58.00           H
        HETATM 1191  HB  SRT A1076     -15.110  13.610  28.816  1.00 57.77           H
        HETATM 1192  O1  SRT A1076     -17.028  11.281  31.131  1.00 62.63           O

        ATOM    295  HB2 ALA A  18       4.601  -9.393   7.275  1.00  0.00           H
        ATOM    296  HB3 ALA A  18       3.340  -9.147   6.043  1.00  0.00           H
        TER     297      ALA A  18
        ENDMDL


    @param file:            The file to write the record to.
    @type file:             file object
    @keyword serial:        The atom serial number.
    @type serial:           int
    @keyword res_name:      The residue name.
    @type res_name:         str
    @keyword chain_id:      The chain identifier.
    @type chain_id:         str
    @keyword res_seq:       The sequence number.
    @type res_seq:          int
    @keyword icode:         The insertion code.
    @type icode:            str
    """

    # Write out the formatted record.
    text = "%-6s%5s      %3s %1s%4s%1s%53s" % (
        'TER',
        _handle_none(serial),
        _handle_none(res_name),
        _handle_none(chain_id),
        _handle_none(res_seq),
        _handle_none(icode),
        ''
    )

    # Validate.
    _record_validate(text)

    # Write out the formatted record.
    file.write(text)
    file.write('\n')
