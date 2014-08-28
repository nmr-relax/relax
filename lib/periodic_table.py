###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
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
"""Module containing a Python object representation of the period table.

The currently used atomic weights are from:

    - Atomic weights of the elements 2011 (IUPAC Technical Report) (U{DOI: 10.1351/PAC-REP-13-03-02<http://dx.doi.org/10.1351/PAC-REP-13-03-02>}).

The currently used isotope atomic masses are taken from U{http://www.ciaaw.org/atomic-masses.htm}, itself taken from:

    - M. Wang et al. (2012).  The Ame2012 Atomic Mass Evaluation Chinese Physics C, 36, 1603-2014.  (U{DOI: 10.1088/1674-1137/36/12/003<http://dx.doi.org/10.1088/1674-1137/36/12/003>}).
"""

# Python module imports.
from numpy import array, average, float64
from re import search, split
from string import lower, upper

# relax module imports.
from lib.errors import RelaxError


def isotope_to_mass_symbol(isotope):
    """Convert the given isotope to its mass number and atomic symbol.

    @param isotope: The isotope name, e.g. '15N'.
    @type isotope:  str
    @return:        The mass number A and atomic symbol.
    @rtype:         int, str
    """

    # The mass number.
    A = int(split('[A-Z]', isotope)[0])

    # The atomic symbol.
    symbol = process_symbol(split('[0-9]', isotope)[-1])

    # Return the components.
    return A, symbol


def process_mass(mass):
    """Process the given mass, handling ranges, unstable isotopes, and uncertainties.

    @param mass:    The atomic mass of standard atomic weight.
    @type mass:     str
    @return:        The corresponding mass.
    @rtype:         float
    """

    # A range, or an unstable isotope.
    if mass[0] == '[':
        # Convert to a list.
        vals = eval(mass)

        # Use numpy to average the list, assuming equal weighting.
        return average(array(vals, float64))

    # A mass with uncertainty.
    else:
        # Obtain the first part of the number.
        val = mass.split('(')[0]

        # Convert to a float and return the value.
        return float(val)


def process_symbol(symbol):
    """Make sure the symbol is in the correct format.

    @param symbol:  The atomic symbol.
    @type symbol:   str
    @return:        The corrected atomic symbol.
    @rtype:         str
    """

    # The format is uppercase first letter, lowercase second.
    new_symbol = upper(symbol[0])
    if len(symbol) == 2:
        new_symbol += lower(symbol[1])

    # Return the corrected atomic symbol.
    return new_symbol



class Element:
    """A special object representing each element."""

    def __init__(self, atomic_number=None, symbol=None, name=None, atomic_weight=None):
        """Set up the element object.

        @keyword atomic_number:     The atomic number.
        @type atomic_number:        int
        @keyword symbol:            The atomic symbol.
        @type symbol:               str
        @keyword name:              The chemical element name.
        @type name:                 str
        @keyword atomic_weight:     The atomic weight number for the atom.  This is a string as it uses the IUPAC notation of, for example, "[1.00784, 1.00811]" and "4.002602(2)" to represent ranges and uncertainty.
        @type atomic_weight:        str
        """

        # Store the values.
        self.atomic_number = atomic_number
        self.name = name
        self.atomic_weight = atomic_weight

        # Initialise the isotope information for the element.
        self.isotopes = []


    def _add_isotope(self, A=None, atomic_mass=None, spin=None, gyromagnetic_ratio=None):
        """Add the isotope information for the element.

        @keyword A:                     The mass number of the isotope.
        @type A:                        int
        @keyword atomic_mass:           The atomic mass of the isotope.  This uses the string notation with the uncertainty specified in brackets at the end.
        @type atomic_mass:              str
        @keyword spin:                  Nuclear spin or angular momentum of the isotope in units of h/2pi.
        @type spin:                     int or float
        @keyword gyromagnetic_ratio:    The nuclear gyromagnetic ratio.
        @type gyromagnetic_ratio:       float
        """

        # Create a new isotope container.
        isotope = Isotope(A=A, atomic_mass=atomic_mass, spin=spin, gyromagnetic_ratio=gyromagnetic_ratio)

        # Store it in the element container.
        self.isotopes.append(isotope)



class Isotope:
    """A special object for the element container for holding different isotope information."""

    def __init__(self, A=None, atomic_mass=None, spin=None, gyromagnetic_ratio=None):
        """Set up the isotope object.

        @keyword A:                     The mass number of the isotope.
        @type A:                        int
        @keyword atomic_mass:           The atomic mass of the isotope.  This uses the string notation with the uncertainty specified in brackets at the end.
        @type atomic_mass:              str
        @keyword spin:                  Nuclear spin or angular momentum of the isotope in units of h/2pi.
        @type spin:                     int or float
        @keyword gyromagnetic_ratio:    The nuclear gyromagnetic ratio.
        @type gyromagnetic_ratio:       float
        """

        # Store the values.
        self.A = A
        self.atomic_mass = atomic_mass
        self.spin = spin
        self.gyromagnetic_ratio = gyromagnetic_ratio



class Periodic_table(dict):
    """The periodic table object."""

    def __init__(self):
        """Set up the periodic table object."""

        # Initialise a fast lookup table.
        self._lookup_symbol = {}


    def _add(self, atomic_number=None, symbol=None, name=None, atomic_weight=None):
        """Add an element to the table.

        @keyword atomic_number:     The atomic number Z.
        @type atomic_number:        int
        @keyword symbol:            The atomic symbol.
        @type symbol:               str
        @keyword name:              The chemical element name.
        @type name:                 str
        @keyword atomic_weight:     The atomic weight number for the atom.  This is a string as it uses the IUPAC notation of, for example, "[1.00784, 1.00811]" and "4.002602(2)" to represent ranges and uncertainty.
        @type atomic_weight:        str
        @return:                    The element container object.
        @rtype:                     Element instance
        """

        # Add the element container.
        self[symbol] = Element(atomic_number=atomic_number, name=name, atomic_weight=atomic_weight)

        # Update the fast lookup tables.
        self._lookup_symbol[atomic_number] = symbol

        # Return the container.
        return self[symbol]


    def _get_isotope(self, symbol=None, A=None):
        """Return the matching isotope container.

        @keyword symbol:    The atomic symbol.
        @type symbol:       str
        @keyword A:         The mass number of the isotope.
        @type A:            int
        """

        # The element container.
        element = self[symbol]

        # Find the isotope.
        for isotope in element.isotopes:
            # A match.
            if isotope.A == A:
                return isotope

        # No isotope found.
        raise RelaxError("The isotope '%i%s' cannot be found." % (A, symbol))


    def atomic_mass(self, id=None):
        """Return the isotopic atomic mass or standard atomic weight as a float.

        @keyword id:    The atom or isotope identifier.  To select isotopes, merge the mass number A with the symbol to form the ID.  To select atoms, just set the ID to the atomic symbol.  For example, '15N' selects the 15N nitrogen isotope, whereas 'N' selects the nitrogen atom.
        @type id:       str
        @return:        The isotopic atomic mass or the standard atomic weight.
        @rtype:         float
        """

        # An isotope.
        if search('[0-9]', id):
            # Convert to the mass number and atomic symbol.
            A, symbol = isotope_to_mass_symbol(id)

            # Get the isotope container.
            isotope = self._get_isotope(symbol=symbol, A=A)

            # Return the processed mass.
            return process_mass(isotope.atomic_mass)

        # A normal atom.
        else:
            return self.atomic_weight(symbol=id)


    def atomic_weight(self, symbol=None):
        """Return the standard atomic weight as a float for the given atom.

        @keyword symbol:    The atomic symbol.
        @type symbol:       str
        @return:            The standard atomic weight.
        @rtype:             float
        """

        # Process the symbol.
        symbol = process_symbol(symbol)

        # Checks.
        if symbol not in self:
            raise RelaxError("The atomic symbol '%s' cannot be found in the periodic table." % symbol)

        # Return the processed weight.
        return process_mass(self[symbol].atomic_weight)


    def gyromagnetic_ratio(isotope=None):
        """Return the gyromagnetic ratio for the isotope.

        @keyword isotope:   The isotope name, e.g. '15N'.
        @type isotope:      str
        @raises RelaxError: If the nucleus type is unknown.
        @returns:           The desired gyromagnetic ratio.
        @rtype:             float
        """

        # Convert to the mass number and atomic symbol.
        A, symbol = isotope_to_mass_symbol(isotope)

        # Get the isotope container.
        isotope = self._get_isotope(symbol=symbol, A=A)

        # Return the gyromagnetic ratio.
        return isotope.gyromagnetic_ratio


    def lookup_symbol(self, atomic_number=None):
        """Return the atomic symbol corresponding to the atomic number Z.

        @keyword atomic_number: The atomic number Z.
        @type atomic_number:    int
        @return:                The atomic symbol.
        @rtype:                 str
        """

        # Direct lookup.
        return self._lookup_symbol[atomic_number]



# Initialise the table.
periodic_table = Periodic_table()

# Hydrogen.
element = periodic_table._add(
    atomic_number=1,
    symbol='H',
    name='Hydrogen',
    atomic_weight="[1.00784, 1.00811]"
)
element._add_isotope(
    A=1,
    atomic_mass="1.0078250322(6)",
    spin = 1/2.,
    gyromagnetic_ratio = 26.7522212 * 1e7    # Pales = 2.675198e+8
)
element._add_isotope(
    A=2,
    atomic_mass="2.0141017781(8)",
    spin = 1
)

# Helium.
element = periodic_table._add(
    atomic_number=2,
    symbol='He',
    name='Helium',
    atomic_weight="4.002602(2)"
)
element._add_isotope(
    A=3,
    atomic_mass="3.01602932(2)"
)
element._add_isotope(
    A=4,
    atomic_mass="4.0026032541(4)"
)

# Lithium.
element = periodic_table._add(
    atomic_number=3,
    symbol='Li',
    name='Lithium',
    atomic_weight="[6.938, 6.997]"
)
element._add_isotope(
    A=6,
    atomic_mass="6.015122887(9)"
)
element._add_isotope(
    A=7,
    atomic_mass="7.01600344(3)"
)

# Beryllium.
element = periodic_table._add(
    atomic_number=4,
    symbol='Be',
    name='Beryllium',
    atomic_weight="9.012182(3)"
)
element._add_isotope(
    A=9,
    atomic_mass="9.0121831(5)"
)

# Boron.
element = periodic_table._add(
    atomic_number=5,
    symbol='B',
    name='Boron',
    atomic_weight="[10.806, 10.821]"
)
element._add_isotope(
    A=10,
    atomic_mass="10.012937(3)"
)
element._add_isotope(
    A=11,
    atomic_mass="11.009305(3)"
)

# Carbon.
element = periodic_table._add(
    atomic_number=6,
    symbol='C',
    name='Carbon',
    atomic_weight="[12.0096, 12.0116]"
)
element._add_isotope(
    A=12,
    atomic_mass="12.0"
)
element._add_isotope(
    A=13,
    atomic_mass="13.003354835(2)",
    spin = 1/2.,
    gyromagnetic_ratio = 6.728 * 1e7
)

# Nitrogen.
element = periodic_table._add(
    atomic_number=7,
    symbol='N',
    name='Nitrogen',
    atomic_weight="[14.00643, 14.00728]"
)
element._add_isotope(
    A=14,
    atomic_mass="14.003074004(2)"
)
element._add_isotope(
    A=15,
    atomic_mass="15.000108899(4)",
    spin = -1/2.,
    gyromagnetic_ratio = -2.7126 * 1e7    # Pales = -2.7116e+7
)

# Oxygen.
element = periodic_table._add(
    atomic_number=8,
    symbol='O',
    name='Oxygen',
    atomic_weight="[15.99903, 15.99977]"
)
element._add_isotope(
    A=16,
    atomic_mass="15.994914620(2)"
)
element._add_isotope(
    A=17,
    atomic_mass="16.999131757(5)",
    spin = 5/2.,
    gyromagnetic_ratio = -3.628 * 1e7
)
element._add_isotope(
    A=18,
    atomic_mass="17.999159613(6)"
)

# Fluorine.
element = periodic_table._add(
    atomic_number=9,
    symbol='F',
    name='Fluorine',
    atomic_weight="18.9984032(5)"
)
element._add_isotope(
    A=19,
    atomic_mass="18.998403163(6)"
)

# Neon.
element = periodic_table._add(
    atomic_number=10,
    symbol='Ne',
    name='Neon',
    atomic_weight="20.1797(6)"
)
element._add_isotope(
    A=20,
    atomic_mass="19.99244018(2)"
)
element._add_isotope(
    A=21,
    atomic_mass="20.9938467(3)"
)
element._add_isotope(
    A=22,
    atomic_mass="21.9913851(2)"
)

# Sodium.
element = periodic_table._add(
    atomic_number=11,
    symbol='Na',
    name='Sodium',
    atomic_weight="22.98976928(2)"
)
element._add_isotope(
    A=23,
    atomic_mass="22.98976928(2)"
)

# Magnesium.
element = periodic_table._add(
    atomic_number=12,
    symbol='Mg',
    name='Magnesium',
    atomic_weight="[24.304, 24.307]"
)
element._add_isotope(
    A=24,
    atomic_mass="23.98504170(9)"
)
element._add_isotope(
    A=25,
    atomic_mass="24.9858370(3)"
)
element._add_isotope(
    A=26,
    atomic_mass="25.9825930(2)"
)

# Aluminium.
element = periodic_table._add(
    atomic_number=13,
    symbol='Al',
    name='Aluminium',
    atomic_weight="26.9815386(8)"
)
element._add_isotope(
    A=27,
    atomic_mass="26.9815385(7)"
)

# Silicon.
element = periodic_table._add(
    atomic_number=14,
    symbol='Si',
    name='Silicon',
    atomic_weight="[28.084, 28.086]"
)
element._add_isotope(
    A=28,
    atomic_mass="27.976926535(3)"
)
element._add_isotope(
    A=29,
    atomic_mass="28.976494665(3)"
)
element._add_isotope(
    A=30,
    atomic_mass="29.97377001(2)"
)

# Phosphorus.
element = periodic_table._add(
    atomic_number=15,
    symbol='P',
    name='Phosphorus',
    atomic_weight="30.973762(2)"
)
element._add_isotope(
    A=31,
    atomic_mass="30.973761998(5)",
    spin = 1/2.,
    gyromagnetic_ratio = 10.841 * 1e7
)

# Sulfur.
element = periodic_table._add(
    atomic_number=16,
    symbol='S',
    name='Sulfur',
    atomic_weight="[32.059, 32.076]"
)
element._add_isotope(
    A=32,
    atomic_mass="31.972071174(9)"
)
element._add_isotope(
    A=33,
    atomic_mass="32.971458910(9)"
)
element._add_isotope(
    A=34,
    atomic_mass="33.9678670(3)"
)
element._add_isotope(
    A=36,
    atomic_mass="35.967081(2)"
)

# Chlorine.
element = periodic_table._add(
    atomic_number=17,
    symbol='Cl',
    name='Chlorine',
    atomic_weight="[35.446, 35.457]"
)
element._add_isotope(
    A=35,
    atomic_mass="34.9688527(3)"
)
element._add_isotope(
    A=37,
    atomic_mass="36.9659026(4)"
)

# Argon.
element = periodic_table._add(
    atomic_number=18,
    symbol='Ar',
    name='Argon',
    atomic_weight="39.948(1)"
)
element._add_isotope(
    A=36,
    atomic_mass="35.9675451(2)"
)
element._add_isotope(
    A=38,
    atomic_mass="37.962732(2)"
)
element._add_isotope(
    A=40,
    atomic_mass="39.96238312(2)"
)

# Potassium.
element = periodic_table._add(
    atomic_number=19,
    symbol='K',
    name='Potassium',
    atomic_weight="39.0983(1)"
)
element._add_isotope(
    A=39,
    atomic_mass="38.96370649(3)"
)
element._add_isotope(
    A=40,
    atomic_mass="39.9639982(4)"
)
element._add_isotope(
    A=41,
    atomic_mass="40.96182526(3)"
)

# Calcium.
element = periodic_table._add(
    atomic_number=20,
    symbol='Ca',
    name='Calcium',
    atomic_weight="40.078(4)"
)
element._add_isotope(
    A=40,
    atomic_mass="39.9625909(2)"
)
element._add_isotope(
    A=42,
    atomic_mass="41.958618(1)"
)
element._add_isotope(
    A=43,
    atomic_mass="42.958766(2)"
)
element._add_isotope(
    A=44,
    atomic_mass="43.955482(2)"
)
element._add_isotope(
    A=46,
    atomic_mass="45.95369(2)"
)
element._add_isotope(
    A=48,
    atomic_mass="47.9525228(8)"
)

# Scandium.
element = periodic_table._add(
    atomic_number=21,
    symbol='Sc',
    name='Scandium',
    atomic_weight="44.955912(6)"
)
element._add_isotope(
    A=45,
    atomic_mass="44.955908(5)"
)

# Titanium.
element = periodic_table._add(
    atomic_number=22,
    symbol='Ti',
    name='Titanium',
    atomic_weight="47.867(1)"
)
element._add_isotope(
    A=46,
    atomic_mass="45.952628(3)"
)
element._add_isotope(
    A=47,
    atomic_mass="46.951759(3)"
)
element._add_isotope(
    A=48,
    atomic_mass="47.947942(3)"
)
element._add_isotope(
    A=49,
    atomic_mass="48.947866(3)"
)
element._add_isotope(
    A=50,
    atomic_mass="49.944787(3)"
)

# Vanadium.
element = periodic_table._add(
    atomic_number=23,
    symbol='V',
    name='Vanadium',
    atomic_weight="50.9415(1)"
)
element._add_isotope(
    A=50,
    atomic_mass="49.947156(6)"
)
element._add_isotope(
    A=51,
    atomic_mass="50.943957(6)"
)

# Chromium.
element = periodic_table._add(
    atomic_number=24,
    symbol='Cr',
    name='Chromium',
    atomic_weight="51.9961(6)"
)
element._add_isotope(
    A=50,
    atomic_mass="49.946042(6)"
)
element._add_isotope(
    A=52,
    atomic_mass="51.940506(4)"
)
element._add_isotope(
    A=53,
    atomic_mass="52.940648(4)"
)
element._add_isotope(
    A=54,
    atomic_mass="53.938879(4)"
)

# Manganese.
element = periodic_table._add(
    atomic_number=25,
    symbol='Mn',
    name='Manganese',
    atomic_weight="54.938045(5)"
)
element._add_isotope(
    A=55,
    atomic_mass="54.938044(3)"
)

# Iron.
element = periodic_table._add(
    atomic_number=26,
    symbol='Fe',
    name='Iron',
    atomic_weight="55.845(2)"
)
element._add_isotope(
    A=54,
    atomic_mass="53.939609(3)"
)
element._add_isotope(
    A=56,
    atomic_mass="55.934936(3)"
)
element._add_isotope(
    A=57,
    atomic_mass="56.935393(3)"
)
element._add_isotope(
    A=58,
    atomic_mass="57.933274(3)"
)

# Cobalt.
element = periodic_table._add(
    atomic_number=27,
    symbol='Co',
    name='Cobalt',
    atomic_weight="58.933195(5)"
)
element._add_isotope(
    A=59,
    atomic_mass="58.933194(4)"
)

# Nickel.
element = periodic_table._add(
    atomic_number=28,
    symbol='Ni',
    name='Nickel',
    atomic_weight="58.6934(4)"
)
element._add_isotope(
    A=58,
    atomic_mass="57.935342(3)"
)
element._add_isotope(
    A=60,
    atomic_mass="59.930786(3)"
)
element._add_isotope(
    A=61,
    atomic_mass="60.931056(3)"
)
element._add_isotope(
    A=62,
    atomic_mass="61.928345(4)"
)
element._add_isotope(
    A=64,
    atomic_mass="63.927967(4)"
)

# Copper.
element = periodic_table._add(
    atomic_number=29,
    symbol='Cu',
    name='Copper',
    atomic_weight="63.546(3)"
)
element._add_isotope(
    A=63,
    atomic_mass="62.929598(4)"
)
element._add_isotope(
    A=65,
    atomic_mass="64.927790(5)"
)

# Zinc.
element = periodic_table._add(
    atomic_number=30,
    symbol='Zn',
    name='Zinc',
    atomic_weight="65.38(2)"
)
element._add_isotope(
    A=64,
    atomic_mass="63.929142(5)"
)
element._add_isotope(
    A=66,
    atomic_mass="65.926034(6)"
)
element._add_isotope(
    A=67,
    atomic_mass="66.927128(6)"
)
element._add_isotope(
    A=68,
    atomic_mass="67.924845(6)"
)
element._add_isotope(
    A=70,
    atomic_mass="69.92532(2)"
)

# Gallium.
element = periodic_table._add(
    atomic_number=31,
    symbol='Ga',
    name='Gallium',
    atomic_weight="69.723(1)"
)
element._add_isotope(
    A=69,
    atomic_mass="68.925574(8) 71	70.924703(6)"
)

# Germanium.
element = periodic_table._add(
    atomic_number=32,
    symbol='Ge',
    name='Germanium',
    atomic_weight="72.630(8)"
)
element._add_isotope(
    A=70,
    atomic_mass="69.924249(6)"
)
element._add_isotope(
    A=72,
    atomic_mass="71.9220758(5)"
)
element._add_isotope(
    A=73,
    atomic_mass="72.9234590(4)"
)
element._add_isotope(
    A=74,
    atomic_mass="73.92117776(9)"
)
element._add_isotope(
    A=76,
    atomic_mass="75.9214027(2)"
)

# Arsenic.
element = periodic_table._add(
    atomic_number=33,
    symbol='As',
    name='Arsenic',
    atomic_weight="74.92160(2)"
)
element._add_isotope(
    A=75,
    atomic_mass="74.921595(6)"
)

# Selenium.
element = periodic_table._add(
    atomic_number=34,
    symbol='Se',
    name='Selenium',
    atomic_weight="78.96(3)"
)
element._add_isotope(
    A=74,
    atomic_mass="73.9224759(1)"
)
element._add_isotope(
    A=76,
    atomic_mass="75.9192137(2)"
)
element._add_isotope(
    A=77,
    atomic_mass="76.9199142(5)"
)
element._add_isotope(
    A=78,
    atomic_mass="77.917309(2)"
)
element._add_isotope(
    A=80,
    atomic_mass="79.916522(8)"
)
element._add_isotope(
    A=82,
    atomic_mass="81.916700(9)"
)

# Bromine.
element = periodic_table._add(
    atomic_number=35,
    symbol='Br',
    name='Bromine',
    atomic_weight="[79.901, 79.907]"
)
element._add_isotope(
    A=79,
    atomic_mass="78.918338(9)"
)
element._add_isotope(
    A=81,
    atomic_mass="80.916290(9)"
)

# Krypton.
element = periodic_table._add(
    atomic_number=36,
    symbol='Kr',
    name='Krypton',
    atomic_weight="83.798(2)"
)
element._add_isotope(
    A=78,
    atomic_mass="77.920365(5)"
)
element._add_isotope(
    A=80,
    atomic_mass="79.916378(5)"
)
element._add_isotope(
    A=82,
    atomic_mass="81.913483(6)"
)
element._add_isotope(
    A=83,
    atomic_mass="82.914127(2)"
)
element._add_isotope(
    A=84,
    atomic_mass="83.91149773(3)"
)
element._add_isotope(
    A=86,
    atomic_mass="85.91061063(3)"
)

# Rubidium.
element = periodic_table._add(
    atomic_number=37,
    symbol='Rb',
    name='Rubidium',
    atomic_weight="85.4678(3)"
)
element._add_isotope(
    A=85,
    atomic_mass="84.91178974(3)"
)
element._add_isotope(
    A=87,
    atomic_mass="86.90918053(5)"
)

# Strontium.
element = periodic_table._add(
    atomic_number=38,
    symbol='Sr',
    name='Strontium',
    atomic_weight="87.62(1)"
)
element._add_isotope(
    A=84,
    atomic_mass="83.913419(8)"
)
element._add_isotope(
    A=86,
    atomic_mass="85.909261(8)"
)
element._add_isotope(
    A=87,
    atomic_mass="86.908878(8)"
)
element._add_isotope(
    A=88,
    atomic_mass="87.905613(8)"
)

# Yttrium.
element = periodic_table._add(
    atomic_number=39,
    symbol='Y',
    name='Yttrium',
    atomic_weight="88.90585(2)"
)
element._add_isotope(
    A=89,
    atomic_mass="88.90584(2)"
)

# Zirconium.
element = periodic_table._add(
    atomic_number=40,
    symbol='Zr',
    name='Zirconium',
    atomic_weight="91.224(2)"
)
element._add_isotope(
    A=90,
    atomic_mass="89.90470(2)"
)
element._add_isotope(
    A=91,
    atomic_mass="90.90564(2)"
)
element._add_isotope(
    A=92,
    atomic_mass="91.90503(2)"
)
element._add_isotope(
    A=94,
    atomic_mass="93.90631(2)"
)
element._add_isotope(
    A=96,
    atomic_mass="95.90827(2)"
)

# Niobium.
element = periodic_table._add(
    atomic_number=41,
    symbol='Nb',
    name='Niobium',
    atomic_weight="92.90638(2)"
)
element._add_isotope(
    A=93,
    atomic_mass="92.90637(2)"
)

# Molybdenum.
element = periodic_table._add(
    atomic_number=42,
    symbol='Mo',
    name='Molybdenum',
    atomic_weight="95.96(2)"
)
element._add_isotope(
    A=92,
    atomic_mass="91.906808(5)"
)
element._add_isotope(
    A=94,
    atomic_mass="93.905085(3)"
)
element._add_isotope(
    A=95,
    atomic_mass="94.905839(3)"
)
element._add_isotope(
    A=96,
    atomic_mass="95.904676(3)"
)
element._add_isotope(
    A=97,
    atomic_mass="96.906018(3)"
)
element._add_isotope(
    A=98,
    atomic_mass="97.905405(3)"
)
element._add_isotope(
    A=100,
    atomic_mass="99.907472(7)"
)

# Technetium.
element = periodic_table._add(
    atomic_number=43,
    symbol='Tc',
    name='Technetium',
    atomic_weight="[98]"
)
element._add_isotope(
    A=98,
    atomic_mass="97.90721(3)"
)

# Ruthenium.
element = periodic_table._add(
    atomic_number=44,
    symbol='Ru',
    name='Ruthenium',
    atomic_weight="101.07(2)"
)
element._add_isotope(
    A=96,
    atomic_mass="95.907590(3)"
)
element._add_isotope(
    A=98,
    atomic_mass="97.90529(5)"
)
element._add_isotope(
    A=99,
    atomic_mass="98.905934(7)"
)
element._add_isotope(
    A=100,
    atomic_mass="99.904214(7)"
)
element._add_isotope(
    A=101,
    atomic_mass="100.905577(8)"
)
element._add_isotope(
    A=102,
    atomic_mass="101.904344(8)"
)
element._add_isotope(
    A=104,
    atomic_mass="103.90543(2)"
)

# Rhodium.
element = periodic_table._add(
    atomic_number=45,
    symbol='Rh',
    name='Rhodium',
    atomic_weight="102.90550(2)"
)
element._add_isotope(
    A=103,
    atomic_mass="102.90550(2)"
)

# Palladium.
element = periodic_table._add(
    atomic_number=46,
    symbol='Pd',
    name='Palladium',
    atomic_weight="106.42(1)"
)
element._add_isotope(
    A=102,
    atomic_mass="101.90560(2)"
)
element._add_isotope(
    A=104,
    atomic_mass="103.904031(9)"
)
element._add_isotope(
    A=105,
    atomic_mass="104.905080(8)"
)
element._add_isotope(
    A=106,
    atomic_mass="105.903480(8)"
)
element._add_isotope(
    A=108,
    atomic_mass="107.903892(8)"
)
element._add_isotope(
    A=110,
    atomic_mass="109.905172(5)"
)

# Silver.
element = periodic_table._add(
    atomic_number=47,
    symbol='Ag',
    name='Silver',
    atomic_weight="107.8682(2)"
)
element._add_isotope(
    A=107,
    atomic_mass="106.90509(2)"
)
element._add_isotope(
    A=109,
    atomic_mass="108.904755(9)"
)

# Cadmium.
element = periodic_table._add(
    atomic_number=48,
    symbol='Cd',
    name='Cadmium',
    atomic_weight="112.411(8)"
)
element._add_isotope(
    A=106,
    atomic_mass="105.906460(8)"
)
element._add_isotope(
    A=108,
    atomic_mass="107.904183(8)"
)
element._add_isotope(
    A=110,
    atomic_mass="109.903007(4)"
)
element._add_isotope(
    A=111,
    atomic_mass="110.904183(4)"
)
element._add_isotope(
    A=112,
    atomic_mass="111.902763(4)"
)
element._add_isotope(
    A=113,
    atomic_mass="112.904408(3)"
)
element._add_isotope(
    A=114,
    atomic_mass="113.903365(3)"
)
element._add_isotope(
    A=116,
    atomic_mass="115.904763(2)"
)

# Indium.
element = periodic_table._add(
    atomic_number=49,
    symbol='In',
    name='Indium',
    atomic_weight="114.818(1)"
)
element._add_isotope(
    A=113,
    atomic_mass="112.904062(6)"
)
element._add_isotope(
    A=115,
    atomic_mass="114.90387878(8)"
)

# Tin.
element = periodic_table._add(
    atomic_number=50,
    symbol='Sn',
    name='Tin',
    atomic_weight="118.710(7)"
)
element._add_isotope(
    A=112,
    atomic_mass="111.904824(4)"
)
element._add_isotope(
    A=114,
    atomic_mass="113.902783(6)"
)
element._add_isotope(
    A=115,
    atomic_mass="114.9033447(1)"
)
element._add_isotope(
    A=116,
    atomic_mass="115.901743(1)"
)
element._add_isotope(
    A=117,
    atomic_mass="116.902954(3)"
)
element._add_isotope(
    A=118,
    atomic_mass="117.901607(3)"
)
element._add_isotope(
    A=119,
    atomic_mass="118.903311(5)"
)
element._add_isotope(
    A=120,
    atomic_mass="119.902202(6)"
)
element._add_isotope(
    A=122,
    atomic_mass="121.90344(2)"
)
element._add_isotope(
    A=124,
    atomic_mass="123.905277(7)"
)

# Antimony.
element = periodic_table._add(
    atomic_number=51,
    symbol='Sb',
    name='Antimony',
    atomic_weight="121.760(1)"
)
element._add_isotope(
    A=121,
    atomic_mass="120.90381(2)"
)
element._add_isotope(
    A=123,
    atomic_mass="122.90421(2)"
)

# Tellurium.
element = periodic_table._add(
    atomic_number=52,
    symbol='Te',
    name='Tellurium',
    atomic_weight="127.60(3)"
)
element._add_isotope(
    A=120,
    atomic_mass="119.90406(2)"
)
element._add_isotope(
    A=122,
    atomic_mass="121.90304(1)"
)
element._add_isotope(
    A=123,
    atomic_mass="122.90427(1)"
)
element._add_isotope(
    A=124,
    atomic_mass="123.90282(1)"
)
element._add_isotope(
    A=125,
    atomic_mass="124.90443(1)"
)
element._add_isotope(
    A=126,
    atomic_mass="125.90331(1)"
)
element._add_isotope(
    A=128,
    atomic_mass="127.904461(6)"
)
element._add_isotope(
    A=130,
    atomic_mass="129.90622275(8)"
)

# Iodine.
element = periodic_table._add(
    atomic_number=53,
    symbol='I',
    name='Iodine',
    atomic_weight="126.90447(3)"
)
element._add_isotope(
    A=127,
    atomic_mass="126.90447(3)"
)

# Xenon.
element = periodic_table._add(
    atomic_number=54,
    symbol='Xe',
    name='Xenon',
    atomic_weight="131.293(6)"
)
element._add_isotope(
    A=124,
    atomic_mass="123.90589(2)"
)
element._add_isotope(
    A=126,
    atomic_mass="125.90430(3)"
)
element._add_isotope(
    A=128,
    atomic_mass="127.903531(7)"
)
element._add_isotope(
    A=129,
    atomic_mass="128.90478086(4)"
)
element._add_isotope(
    A=130,
    atomic_mass="129.9035094(1)"
)
element._add_isotope(
    A=131,
    atomic_mass="130.905084(2)"
)
element._add_isotope(
    A=132,
    atomic_mass="131.90415509(4)"
)
element._add_isotope(
    A=134,
    atomic_mass="133.905395(6)"
)
element._add_isotope(
    A=136,
    atomic_mass="135.90721448(7)"
)

# Caesium.
element = periodic_table._add(
    atomic_number=55,
    symbol='Cs',
    name='Caesium',
    atomic_weight="132.9054519(2)"
)
element._add_isotope(
    A=133,
    atomic_mass="132.90545196(6)"
)

# Barium.
element = periodic_table._add(
    atomic_number=56,
    symbol='Ba',
    name='Barium',
    atomic_weight="137.327(7)"
)
element._add_isotope(
    A=130,
    atomic_mass="129.90632(2)"
)
element._add_isotope(
    A=132,
    atomic_mass="131.905061(7)"
)
element._add_isotope(
    A=134,
    atomic_mass="133.904508(2)"
)
element._add_isotope(
    A=135,
    atomic_mass="134.905688(2)"
)
element._add_isotope(
    A=136,
    atomic_mass="135.904576(2)"
)
element._add_isotope(
    A=137,
    atomic_mass="136.905827(2)"
)
element._add_isotope(
    A=138,
    atomic_mass="137.905247(2)"
)

# Lanthanum.
element = periodic_table._add(
    atomic_number=57,
    symbol='La',
    name='Lanthanum',
    atomic_weight="138.90547(7)"
)
element._add_isotope(
    A=138,
    atomic_mass="137.90712(3)"
)
element._add_isotope(
    A=139,
    atomic_mass="138.90636(2)"
)

# Cerium.
element = periodic_table._add(
    atomic_number=58,
    symbol='Ce',
    name='Cerium',
    atomic_weight="140.116(1)"
)
element._add_isotope(
    A=136,
    atomic_mass="135.907129(3)"
)
element._add_isotope(
    A=138,
    atomic_mass="137.90599(7)"
)
element._add_isotope(
    A=140,
    atomic_mass="139.90544(2)"
)
element._add_isotope(
    A=142,
    atomic_mass="141.90925(2)"
)

# Praseodymium.
element = periodic_table._add(
    atomic_number=59,
    symbol='Pr',
    name='Praseodymium',
    atomic_weight="140.90765(2)"
)
element._add_isotope(
    A=141,
    atomic_mass="140.90766(2)"
)

# Neodymium.
element = periodic_table._add(
    atomic_number=60,
    symbol='Nd',
    name='Neodymium',
    atomic_weight="144.242(3)"
)
element._add_isotope(
    A=142,
    atomic_mass="141.90773(2)"
)
element._add_isotope(
    A=143,
    atomic_mass="142.90982(2)"
)
element._add_isotope(
    A=144,
    atomic_mass="143.91009(2)"
)
element._add_isotope(
    A=145,
    atomic_mass="144.91258(2)"
)
element._add_isotope(
    A=146,
    atomic_mass="145.91312(2)"
)
element._add_isotope(
    A=148,
    atomic_mass="147.91690(2)"
)
element._add_isotope(
    A=150,
    atomic_mass="149.92090(2)"
)

# Promethium.
element = periodic_table._add(
    atomic_number=61,
    symbol='Pm',
    name='Promethium',
    atomic_weight="[145]"
)
element._add_isotope(
    A=145,
    atomic_mass="144.91276(2)"
)

# Samarium.
element = periodic_table._add(
    atomic_number=62,
    symbol='Sm',
    name='Samarium',
    atomic_weight="150.36(2)"
)
element._add_isotope(
    A=144,
    atomic_mass="143.91201(2)"
)
element._add_isotope(
    A=147,
    atomic_mass="146.91490(2)"
)
element._add_isotope(
    A=148,
    atomic_mass="147.91483(2)"
)
element._add_isotope(
    A=149,
    atomic_mass="148.91719(2)"
)
element._add_isotope(
    A=150,
    atomic_mass="149.91728(2)"
)
element._add_isotope(
    A=152,
    atomic_mass="151.91974(2)"
)
element._add_isotope(
    A=154,
    atomic_mass="153.92222(2)"
)

# Europium.
element = periodic_table._add(
    atomic_number=63,
    symbol='Eu',
    name='Europium',
    atomic_weight="151.964(1)"
)
element._add_isotope(
    A=151,
    atomic_mass="150.91986(2)"
)
element._add_isotope(
    A=153,
    atomic_mass="152.92124(2)"
)

# Gadolinium.
element = periodic_table._add(
    atomic_number=64,
    symbol='Gd',
    name='Gadolinium',
    atomic_weight="157.25(3)"
)
element._add_isotope(
    A=152,
    atomic_mass="151.91980(2)"
)
element._add_isotope(
    A=154,
    atomic_mass="153.92087(2)"
)
element._add_isotope(
    A=155,
    atomic_mass="154.92263(2)"
)
element._add_isotope(
    A=156,
    atomic_mass="155.92213(2)"
)
element._add_isotope(
    A=157,
    atomic_mass="156.92397(2)"
)
element._add_isotope(
    A=158,
    atomic_mass="157.92411(2)"
)
element._add_isotope(
    A=160,
    atomic_mass="159.92706(2)"
)

# Terbium.
element = periodic_table._add(
    atomic_number=65,
    symbol='Tb',
    name='Terbium',
    atomic_weight="158.92535(2)"
)
element._add_isotope(
    A=159,
    atomic_mass="158.92535(2)"
)

# Dysprosium.
element = periodic_table._add(
    atomic_number=66,
    symbol='Dy',
    name='Dysprosium',
    atomic_weight="162.500(1)"
)
element._add_isotope(
    A=156,
    atomic_mass="155.92428(2)"
)
element._add_isotope(
    A=158,
    atomic_mass="157.92442(2)"
)
element._add_isotope(
    A=160,
    atomic_mass="159.92520(2)"
)
element._add_isotope(
    A=161,
    atomic_mass="160.92694(2)"
)
element._add_isotope(
    A=162,
    atomic_mass="161.92681(2)"
)
element._add_isotope(
    A=163,
    atomic_mass="162.92874(2)"
)
element._add_isotope(
    A=164,
    atomic_mass="163.92918(2)"
)

# Holmium.
element = periodic_table._add(
    atomic_number=67,
    symbol='Ho',
    name='Holmium',
    atomic_weight="164.93032(2)"
)
element._add_isotope(
    A=165,
    atomic_mass="164.93033(2)"
)

# Erbium.
element = periodic_table._add(
    atomic_number=68,
    symbol='Er',
    name='Erbium',
    atomic_weight="167.259(3)"
)
element._add_isotope(
    A=162,
    atomic_mass="161.92879(2)"
)
element._add_isotope(
    A=164,
    atomic_mass="163.92921(2)"
)
element._add_isotope(
    A=166,
    atomic_mass="165.93030(2)"
)
element._add_isotope(
    A=167,
    atomic_mass="166.93205(2)"
)
element._add_isotope(
    A=168,
    atomic_mass="167.93238(2)"
)
element._add_isotope(
    A=170,
    atomic_mass="169.93547(2)"
)

# Thulium.
element = periodic_table._add(
    atomic_number=69,
    symbol='Tm',
    name='Thulium',
    atomic_weight="168.93421(2)"
)
element._add_isotope(
    A=169,
    atomic_mass="168.93422(2)"
)

# Ytterbium.
element = periodic_table._add(
    atomic_number=70,
    symbol='Yb',
    name='Ytterbium',
    atomic_weight="173.054(5)"
)
element._add_isotope(
    A=168,
    atomic_mass="167.93389(2)"
)
element._add_isotope(
    A=170,
    atomic_mass="169.93477(2)"
)
element._add_isotope(
    A=171,
    atomic_mass="170.93633(2)"
)
element._add_isotope(
    A=172,
    atomic_mass="171.93639(2)"
)
element._add_isotope(
    A=173,
    atomic_mass="172.93822(2)"
)
element._add_isotope(
    A=174,
    atomic_mass="173.93887(2)"
)
element._add_isotope(
    A=176,
    atomic_mass="175.94258(2)"
)

# Lutetium.
element = periodic_table._add(
    atomic_number=71,
    symbol='Lu',
    name='Lutetium',
    atomic_weight="174.9668(1)"
)
element._add_isotope(
    A=175,
    atomic_mass="174.94078(2)"
)
element._add_isotope(
    A=176,
    atomic_mass="175.94269(2)"
)

# Hafnium.
element = periodic_table._add(
    atomic_number=72,
    symbol='Hf',
    name='Hafnium',
    atomic_weight="178.49(2)"
)
element._add_isotope(
    A=174,
    atomic_mass="173.94005(2)"
)
element._add_isotope(
    A=176,
    atomic_mass="175.94141(2)"
)
element._add_isotope(
    A=177,
    atomic_mass="176.94323(2)"
)
element._add_isotope(
    A=178,
    atomic_mass="177.94371(2)"
)
element._add_isotope(
    A=179,
    atomic_mass="178.94582(2)"
)
element._add_isotope(
    A=180,
    atomic_mass="179.94656(2)"
)

# Tantalum.
element = periodic_table._add(
    atomic_number=73,
    symbol='Ta',
    name='Tantalum',
    atomic_weight="180.94788(2)"
)
element._add_isotope(
    A=180,
    atomic_mass="179.94746(2)"
)
element._add_isotope(
    A=181,
    atomic_mass="180.94800(2)"
)

# Tungsten.
element = periodic_table._add(
    atomic_number=74,
    symbol='W',
    name='Tungsten',
    atomic_weight="183.84(1)"
)
element._add_isotope(
    A=180,
    atomic_mass="179.94671(2)"
)
element._add_isotope(
    A=182,
    atomic_mass="181.948204(6)"
)
element._add_isotope(
    A=183,
    atomic_mass="182.950223(6)"
)
element._add_isotope(
    A=184,
    atomic_mass="183.950931(6)"
)
element._add_isotope(
    A=186,
    atomic_mass="185.95436(2)"
)

# Rhenium.
element = periodic_table._add(
    atomic_number=75,
    symbol='Re',
    name='Rhenium',
    atomic_weight="186.207(1)"
)
element._add_isotope(
    A=185,
    atomic_mass="184.952955(8)"
)
element._add_isotope(
    A=187,
    atomic_mass="186.95575(1)"
)

# Osmium.
element = periodic_table._add(
    atomic_number=76,
    symbol='Os',
    name='Osmium',
    atomic_weight="190.23(3)"
)
element._add_isotope(
    A=184,
    atomic_mass="183.952489(9)"
)
element._add_isotope(
    A=186,
    atomic_mass="185.95384(1)"
)
element._add_isotope(
    A=187,
    atomic_mass="186.95575(1)"
)
element._add_isotope(
    A=188,
    atomic_mass="187.95584(1)"
)
element._add_isotope(
    A=189,
    atomic_mass="188.95814(2)"
)
element._add_isotope(
    A=190,
    atomic_mass="189.95844(2)"
)
element._add_isotope(
    A=192,
    atomic_mass="191.96148(2)"
)

# Iridium.
element = periodic_table._add(
    atomic_number=77,
    symbol='Ir',
    name='Iridium',
    atomic_weight="192.217(3)"
)
element._add_isotope(
    A=191,
    atomic_mass="190.96059(2)"
)
element._add_isotope(
    A=193,
    atomic_mass="192.96292(2)"
)

# Platinum.
element = periodic_table._add(
    atomic_number=78,
    symbol='Pt',
    name='Platinum',
    atomic_weight="195.084(9)"
)
element._add_isotope(
    A=190,
    atomic_mass="189.95993(4)"
)
element._add_isotope(
    A=192,
    atomic_mass="191.96104(2)"
)
element._add_isotope(
    A=194,
    atomic_mass="193.962681(6)"
)
element._add_isotope(
    A=195,
    atomic_mass="194.964792(6)"
)
element._add_isotope(
    A=196,
    atomic_mass="195.964952(6)"
)
element._add_isotope(
    A=198,
    atomic_mass="197.96789(2)"
)

# Gold.
element = periodic_table._add(
    atomic_number=79,
    symbol='Au',
    name='Gold',
    atomic_weight="196.966569(4)"
)
element._add_isotope(
    A=197,
    atomic_mass="196.966569(5)"
)

# Mercury.
element = periodic_table._add(
    atomic_number=80,
    symbol='Hg',
    name='Mercury',
    atomic_weight="200.592(3)"
)
element._add_isotope(
    A=196,
    atomic_mass="195.96583(2)"
)
element._add_isotope(
    A=198,
    atomic_mass="197.966769(3)"
)
element._add_isotope(
    A=199,
    atomic_mass="198.968281(3)"
)
element._add_isotope(
    A=200,
    atomic_mass="199.968327(3)"
)
element._add_isotope(
    A=201,
    atomic_mass="200.970303(5)"
)
element._add_isotope(
    A=202,
    atomic_mass="201.970643(5)"
)
element._add_isotope(
    A=204,
    atomic_mass="203.973494(3)"
)

# Thallium.
element = periodic_table._add(
    atomic_number=81,
    symbol='Tl',
    name='Thallium',
    atomic_weight="[204.382, 204.385]"
)
element._add_isotope(
    A=203,
    atomic_mass="202.972345(9)"
)
element._add_isotope(
    A=205,
    atomic_mass="204.974428(9)"
)

# Lead.
element = periodic_table._add(
    atomic_number=82,
    symbol='Pb',
    name='Lead',
    atomic_weight="207.2(1)"
)
element._add_isotope(
    A=204,
    atomic_mass="203.973044(8)"
)
element._add_isotope(
    A=206,
    atomic_mass="205.974466(8)"
)
element._add_isotope(
    A=207,
    atomic_mass="206.975897(8)"
)
element._add_isotope(
    A=208,
    atomic_mass="207.976653(8)"
)

# Bismuth.
element = periodic_table._add(
    atomic_number=83,
    symbol='Bi',
    name='Bismuth',
    atomic_weight="208.98040(1)"
)
element._add_isotope(
    A=209,
    atomic_mass="208.98040(1)"
)

# Polonium.
element = periodic_table._add(
    atomic_number=84,
    symbol='Po',
    name='Polonium',
    atomic_weight="[209]"
)

# Astatine.
element = periodic_table._add(
    atomic_number=85,
    symbol='At',
    name='Astatine',
    atomic_weight="[210]"
)

# Radon.
element = periodic_table._add(
    atomic_number=86,
    symbol='Rn',
    name='Radon',
    atomic_weight="[222]"
)

# Francium.
element = periodic_table._add(
    atomic_number=87,
    symbol='Fr',
    name='Francium',
    atomic_weight="[223]"
)

# Radium.
element = periodic_table._add(
    atomic_number=88,
    symbol='Ra',
    name='Radium',
    atomic_weight="[226]"
)

# Actinium.
element = periodic_table._add(
    atomic_number=89,
    symbol='Ac',
    name='Actinium',
    atomic_weight="[227]"
)

# Thorium.
element = periodic_table._add(
    atomic_number=90,
    symbol='Th',
    name='Thorium',
    atomic_weight="232.03806(2)"
)
element._add_isotope(
    A=230,
    atomic_mass="230.03313(2)"
)
element._add_isotope(
    A=232,
    atomic_mass="232.03806(2)"
)

# Protactinium.
element = periodic_table._add(
    atomic_number=91,
    symbol='Pa',
    name='Protactinium',
    atomic_weight="231.03588(2)"
)
element._add_isotope(
    A=231,
    atomic_mass="231.03588(2)"
)

# Uranium.
element = periodic_table._add(
    atomic_number=92,
    symbol='U',
    name='Uranium',
    atomic_weight="238.02891(3)"
)
element._add_isotope(
    A=233,
    atomic_mass="233.03964(2)"
)
element._add_isotope(
    A=234,
    atomic_mass="234.04095(2)"
)
element._add_isotope(
    A=235,
    atomic_mass="235.04393(2)"
)
element._add_isotope(
    A=238,
    atomic_mass="238.05079(2)"
)

# Neptunium.
element = periodic_table._add(
    atomic_number=93,
    symbol='Np',
    name='Neptunium',
    atomic_weight="[237]"
)

# Plutonium.
element = periodic_table._add(
    atomic_number=94,
    symbol='Pu',
    name='Plutonium',
    atomic_weight="[244]"
)

# Americium.
element = periodic_table._add(
    atomic_number=95,
    symbol='Am',
    name='Americium',
    atomic_weight="[243]"
)

# Curium.
element = periodic_table._add(
    atomic_number=96,
    symbol='Cm',
    name='Curium',
    atomic_weight="[247]"
)

# Berkelium.
element = periodic_table._add(
    atomic_number=97,
    symbol='Bk',
    name='Berkelium',
    atomic_weight="[247]"
)

# Californium.
element = periodic_table._add(
    atomic_number=98,
    symbol='Cf',
    name='Californium',
    atomic_weight="[251]"
)

# Einsteinium.
element = periodic_table._add(
    atomic_number=99,
    symbol='Es',
    name='Einsteinium',
    atomic_weight="[252]"
)

# Fermium.
element = periodic_table._add(
    atomic_number=100,
    symbol='Fm',
    name='Fermium',
    atomic_weight="[257]"
)

# Mendelevium.
element = periodic_table._add(
    atomic_number=101,
    symbol='Md',
    name='Mendelevium',
    atomic_weight="[258]"
)

# Nobelium.
element = periodic_table._add(
    atomic_number=102,
    symbol='No',
    name='Nobelium',
    atomic_weight="[259]"
)

# Lawrencium.
element = periodic_table._add(
    atomic_number=103,
    symbol='Lr',
    name='Lawrencium',
    atomic_weight="[266]"
)

# Rutherfordium.
element = periodic_table._add(
    atomic_number=104,
    symbol='Rf',
    name='Rutherfordium',
    atomic_weight="[267]"
)

# Dubnium.
element = periodic_table._add(
    atomic_number=105,
    symbol='Db',
    name='Dubnium',
    atomic_weight="[268]"
)

# Seaborgium.
element = periodic_table._add(
    atomic_number=106,
    symbol='Sg',
    name='Seaborgium',
    atomic_weight="[269]"
)

# Bohrium.
element = periodic_table._add(
    atomic_number=107,
    symbol='Bh',
    name='Bohrium',
    atomic_weight="[270]"
)

# Hassium.
element = periodic_table._add(
    atomic_number=108,
    symbol='Hs',
    name='Hassium',
    atomic_weight="[269]"
)

# Meitnerium.
element = periodic_table._add(
    atomic_number=109,
    symbol='Mt',
    name='Meitnerium',
    atomic_weight="[278]"
)

# Darmstadtium.
element = periodic_table._add(
    atomic_number=110,
    symbol='Ds',
    name='Darmstadtium',
    atomic_weight="[281]"
)

# Roentgenium.
element = periodic_table._add(
    atomic_number=111,
    symbol='Rg',
    name='Roentgenium',
    atomic_weight="[281]"
)

# Copernicium.
element = periodic_table._add(
    atomic_number=112,
    symbol='Cn',
    name='Copernicium',
    atomic_weight="[285]"
)

# Ununtrium.
element = periodic_table._add(
    atomic_number=113,
    symbol='Uut',
    name='Ununtrium',
    atomic_weight="[286]"
)

# Flerovium.
element = periodic_table._add(
    atomic_number=114,
    symbol='Fl',
    name='Flerovium',
    atomic_weight="[289]"
)

# Ununpentium.
element = periodic_table._add(
    atomic_number=115,
    symbol='Uup',
    name='Ununpentium',
    atomic_weight="[289]"
)

# Livermorium.
element = periodic_table._add(
    atomic_number=116,
    symbol='Lv',
    name='Livermorium',
    atomic_weight="[293]"
)

# Ununseptium.
element = periodic_table._add(
    atomic_number=117,
    symbol='Uus',
    name='Ununseptium',
    atomic_weight="[294]"
)

# Ununoctium.
element = periodic_table._add(
    atomic_number=118,
    symbol='Uuo',
    name='Ununoctium',
    atomic_weight="[294]"
)
