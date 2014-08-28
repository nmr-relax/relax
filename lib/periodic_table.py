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

    - Atomic weights of the elements 2011 (IUPAC Technical Report) (U{DOI: 10.1351/PAC-REP-13-03-02<http://dx.doi.org/10.1351/PAC-REP-13-03-02>).
"""

# Python module imports.
from numpy import array, average, float64

# relax module imports.
from lib.errors import RelaxError


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


class Periodic_table(dict):
    """The periodic table object."""

    def _add(self, atomic_number=None, symbol=None, name=None, atomic_weight=None):
        """Add an element to the table.

        @keyword atomic_number:     The atomic number.
        @type atomic_number:        int
        @keyword symbol:            The atomic symbol.
        @type symbol:               str
        @keyword name:              The chemical element name.
        @type name:                 str
        @keyword atomic_weight:     The atomic weight number for the atom.  This is a string as it uses the IUPAC notation of, for example, "[1.00784, 1.00811]" and "4.002602(2)" to represent ranges and uncertainty.
        @type atomic_weight:        str
        """

        # Add the element container.
        self[symbol] = Element(atomic_number=atomic_number, name=name, atomic_weight=atomic_weight)


    def atomic_weight(self, symbol=None):
        """Return the standard atomic weight as a float for the given atom.

        @keyword symbol:    The atomic symbol.
        @type symbol:       str
        @return:            The standard atomic weight.
        @rtype:             float
        """

        # Checks.
        if symbol not in self:
            raise RelaxError("The atomic symbol '%s' cannot be found in the periodic table." % symbol)

        # The weight.
        weight = self[symbol].atomic_weight

        # A range, or an unstable isotope.
        if weight[0] == '[':
            # Convert to a list.
            vals = eval(weight)

            # Use numpy to average the list, assuming equal weighting.
            return average(array(vals, float64))

        # A weight with uncertainty.
        else:
            # Obtain the first part of the number.
            val = weight.split('(')[0]

            # Convert to a float and return the value.
            return float(val)


    def lookup_symbol(self, atomic_number=None):
        """Return the atomic symbol corresponding to the atomic number.

        @keyword atomic_number: The atomic number.
        @type atomic_number:    int
        @return:                The atomic symbol.
        @rtype:                 str
        """

        # Direct lookup.
        return self.symbol[atomic_number-1]



# Initialise the table.
periodic_table = Periodic_table()

# Populate the table.
periodic_table._add(
    atomic_number=1,
    symbol='H',
    name='Hydrogen',
    atomic_weight="[1.00784, 1.00811]"
)

periodic_table._add(
    atomic_number=2,
    symbol='He',
    name='Helium',
    atomic_weight="4.002602(2)"
)

periodic_table._add(
    atomic_number=3,
    symbol='Li',
    name='Lithium',
    atomic_weight="[6.938, 6.997]"
)

periodic_table._add(
    atomic_number=4,
    symbol='Be',
    name='Beryllium',
    atomic_weight="9.012182(3)"
)

periodic_table._add(
    atomic_number=5,
    symbol='B',
    name='Boron',
    atomic_weight="[10.806, 10.821]"
)

periodic_table._add(
    atomic_number=6,
    symbol='C',
    name='Carbon',
    atomic_weight="[12.0096, 12.0116]"
)

periodic_table._add(
    atomic_number=7,
    symbol='N',
    name='Nitrogen',
    atomic_weight="[14.00643, 14.00728]"
)

periodic_table._add(
    atomic_number=8,
    symbol='O',
    name='Oxygen',
    atomic_weight="[15.99903, 15.99977]"
)

periodic_table._add(
    atomic_number=9,
    symbol='F',
    name='Fluorine',
    atomic_weight="18.9984032(5)"
)

periodic_table._add(
    atomic_number=10,
    symbol='Ne',
    name='Neon',
    atomic_weight="20.1797(6)"
)

periodic_table._add(
    atomic_number=11,
    symbol='Na',
    name='Sodium',
    atomic_weight="22.98976928(2)"
)

periodic_table._add(
    atomic_number=12,
    symbol='Mg',
    name='Magnesium',
    atomic_weight="[24.304, 24.307]"
)

periodic_table._add(
    atomic_number=13,
    symbol='Al',
    name='Aluminium',
    atomic_weight="26.9815386(8)"
)

periodic_table._add(
    atomic_number=14,
    symbol='Si',
    name='Silicon',
    atomic_weight="[28.084, 28.086]"
)

periodic_table._add(
    atomic_number=15,
    symbol='P',
    name='Phosphorus',
    atomic_weight="30.973762(2)"
)

periodic_table._add(
    atomic_number=16,
    symbol='S',
    name='Sulfur',
    atomic_weight="[32.059, 32.076]"
)

periodic_table._add(
    atomic_number=17,
    symbol='Cl',
    name='Chlorine',
    atomic_weight="[35.446, 35.457]"
)

periodic_table._add(
    atomic_number=18,
    symbol='Ar',
    name='Argon',
    atomic_weight="39.948(1)"
)

periodic_table._add(
    atomic_number=19,
    symbol='K',
    name='Potassium',
    atomic_weight="39.0983(1)"
)

periodic_table._add(
    atomic_number=20,
    symbol='Ca',
    name='Calcium',
    atomic_weight="40.078(4)"
)

periodic_table._add(
    atomic_number=21,
    symbol='Sc',
    name='Scandium',
    atomic_weight="44.955912(6)"
)

periodic_table._add(
    atomic_number=22,
    symbol='Ti',
    name='Titanium',
    atomic_weight="47.867(1)"
)

periodic_table._add(
    atomic_number=23,
    symbol='V',
    name='Vanadium',
    atomic_weight="50.9415(1)"
)

periodic_table._add(
    atomic_number=24,
    symbol='Cr',
    name='Chromium',
    atomic_weight="51.9961(6)"
)

periodic_table._add(
    atomic_number=25,
    symbol='Mn',
    name='Manganese',
    atomic_weight="54.938045(5)"
)

periodic_table._add(
    atomic_number=26,
    symbol='Fe',
    name='Iron',
    atomic_weight="55.845(2)"
)

periodic_table._add(
    atomic_number=27,
    symbol='Co',
    name='Cobalt',
    atomic_weight="58.933195(5)"
)

periodic_table._add(
    atomic_number=28,
    symbol='Ni',
    name='Nickel',
    atomic_weight="58.6934(4)"
)

periodic_table._add(
    atomic_number=29,
    symbol='Cu',
    name='Copper',
    atomic_weight="63.546(3)"
)

periodic_table._add(
    atomic_number=30,
    symbol='Zn',
    name='Zinc',
    atomic_weight="65.38(2)"
)

periodic_table._add(
    atomic_number=31,
    symbol='Ga',
    name='Gallium',
    atomic_weight="69.723(1)"
)

periodic_table._add(
    atomic_number=32,
    symbol='Ge',
    name='Germanium',
    atomic_weight="72.630(8)"
)

periodic_table._add(
    atomic_number=33,
    symbol='As',
    name='Arsenic',
    atomic_weight="74.92160(2)"
)

periodic_table._add(
    atomic_number=34,
    symbol='Se',
    name='Selenium',
    atomic_weight="78.96(3)"
)

periodic_table._add(
    atomic_number=35,
    symbol='Br',
    name='Bromine',
    atomic_weight="[79.901, 79.907]"
)

periodic_table._add(
    atomic_number=36,
    symbol='Kr',
    name='Krypton',
    atomic_weight="83.798(2)"
)

periodic_table._add(
    atomic_number=37,
    symbol='Rb',
    name='Rubidium',
    atomic_weight="85.4678(3)"
)

periodic_table._add(
    atomic_number=38,
    symbol='Sr',
    name='Strontium',
    atomic_weight="87.62(1)"
)

periodic_table._add(
    atomic_number=39,
    symbol='Y',
    name='Yttrium',
    atomic_weight="88.90585(2)"
)

periodic_table._add(
    atomic_number=40,
    symbol='Zr',
    name='Zirconium',
    atomic_weight="91.224(2)"
)

periodic_table._add(
    atomic_number=41,
    symbol='Nb',
    name='Niobium',
    atomic_weight="92.90638(2)"
)

periodic_table._add(
    atomic_number=42,
    symbol='Mo',
    name='Molybdenum',
    atomic_weight="95.96(2)"
)

periodic_table._add(
    atomic_number=43,
    symbol='Tc',
    name='Technetium',
    atomic_weight="[98]"
)

periodic_table._add(
    atomic_number=44,
    symbol='Ru',
    name='Ruthenium',
    atomic_weight="101.07(2)"
)

periodic_table._add(
    atomic_number=45,
    symbol='Rh',
    name='Rhodium',
    atomic_weight="102.90550(2)"
)

periodic_table._add(
    atomic_number=46,
    symbol='Pd',
    name='Palladium',
    atomic_weight="106.42(1)"
)

periodic_table._add(
    atomic_number=47,
    symbol='Ag',
    name='Silver',
    atomic_weight="107.8682(2)"
)

periodic_table._add(
    atomic_number=48,
    symbol='Cd',
    name='Cadmium',
    atomic_weight="112.411(8)"
)

periodic_table._add(
    atomic_number=49,
    symbol='In',
    name='Indium',
    atomic_weight="114.818(1)"
)

periodic_table._add(
    atomic_number=50,
    symbol='Sn',
    name='Tin',
    atomic_weight="118.710(7)"
)

periodic_table._add(
    atomic_number=51,
    symbol='Sb',
    name='Antimony',
    atomic_weight="121.760(1)"
)

periodic_table._add(
    atomic_number=52,
    symbol='Te',
    name='Tellurium',
    atomic_weight="127.60(3)"
)

periodic_table._add(
    atomic_number=53,
    symbol='I',
    name='Iodine',
    atomic_weight="126.90447(3)"
)

periodic_table._add(
    atomic_number=54,
    symbol='Xe',
    name='Xenon',
    atomic_weight="131.293(6)"
)

periodic_table._add(
    atomic_number=55,
    symbol='Cs',
    name='Caesium',
    atomic_weight="132.9054519(2)"
)

periodic_table._add(
    atomic_number=56,
    symbol='Ba',
    name='Barium',
    atomic_weight="137.327(7)"
)

periodic_table._add(
    atomic_number=57,
    symbol='La',
    name='Lanthanum',
    atomic_weight="138.90547(7)"
)

periodic_table._add(
    atomic_number=58,
    symbol='Ce',
    name='Cerium',
    atomic_weight="140.116(1)"
)

periodic_table._add(
    atomic_number=59,
    symbol='Pr',
    name='Praseodymium',
    atomic_weight="140.90765(2)"
)

periodic_table._add(
    atomic_number=60,
    symbol='Nd',
    name='Neodymium',
    atomic_weight="144.242(3)"
)

periodic_table._add(
    atomic_number=61,
    symbol='Pm',
    name='Promethium',
    atomic_weight="[145]"
)

periodic_table._add(
    atomic_number=62,
    symbol='Sm',
    name='Samarium',
    atomic_weight="150.36(2)"
)

periodic_table._add(
    atomic_number=63,
    symbol='Eu',
    name='Europium',
    atomic_weight="151.964(1)"
)

periodic_table._add(
    atomic_number=64,
    symbol='Gd',
    name='Gadolinium',
    atomic_weight="157.25(3)"
)

periodic_table._add(
    atomic_number=65,
    symbol='Tb',
    name='Terbium',
    atomic_weight="158.92535(2)"
)

periodic_table._add(
    atomic_number=66,
    symbol='Dy',
    name='Dysprosium',
    atomic_weight="162.500(1)"
)

periodic_table._add(
    atomic_number=67,
    symbol='Ho',
    name='Holmium',
    atomic_weight="164.93032(2)"
)

periodic_table._add(
    atomic_number=68,
    symbol='Er',
    name='Erbium',
    atomic_weight="167.259(3)"
)

periodic_table._add(
    atomic_number=69,
    symbol='Tm',
    name='Thulium',
    atomic_weight="168.93421(2)"
)

periodic_table._add(
    atomic_number=70,
    symbol='Yb',
    name='Ytterbium',
    atomic_weight="173.054(5)"
)

periodic_table._add(
    atomic_number=71,
    symbol='Lu',
    name='Lutetium',
    atomic_weight="174.9668(1)"
)

periodic_table._add(
    atomic_number=72,
    symbol='Hf',
    name='Hafnium',
    atomic_weight="178.49(2)"
)

periodic_table._add(
    atomic_number=73,
    symbol='Ta',
    name='Tantalum',
    atomic_weight="180.94788(2)"
)

periodic_table._add(
    atomic_number=74,
    symbol='W',
    name='Tungsten',
    atomic_weight="183.84(1)"
)

periodic_table._add(
    atomic_number=75,
    symbol='Re',
    name='Rhenium',
    atomic_weight="186.207(1)"
)

periodic_table._add(
    atomic_number=76,
    symbol='Os',
    name='Osmium',
    atomic_weight="190.23(3)"
)

periodic_table._add(
    atomic_number=77,
    symbol='Ir',
    name='Iridium',
    atomic_weight="192.217(3)"
)

periodic_table._add(
    atomic_number=78,
    symbol='Pt',
    name='Platinum',
    atomic_weight="195.084(9)"
)

periodic_table._add(
    atomic_number=79,
    symbol='Au',
    name='Gold',
    atomic_weight="196.966569(4)"
)

periodic_table._add(
    atomic_number=80,
    symbol='Hg',
    name='Mercury',
    atomic_weight="200.592(3)"
)

periodic_table._add(
    atomic_number=81,
    symbol='Tl',
    name='Thallium',
    atomic_weight="[204.382, 204.385]"
)

periodic_table._add(
    atomic_number=82,
    symbol='Pb',
    name='Lead',
    atomic_weight="207.2(1)"
)

periodic_table._add(
    atomic_number=83,
    symbol='Bi',
    name='Bismuth',
    atomic_weight="208.98040(1)"
)

periodic_table._add(
    atomic_number=84,
    symbol='Po',
    name='Polonium',
    atomic_weight="[209]"
)

periodic_table._add(
    atomic_number=85,
    symbol='At',
    name='Astatine',
    atomic_weight="[210]"
)

periodic_table._add(
    atomic_number=86,
    symbol='Rn',
    name='Radon',
    atomic_weight="[222]"
)

periodic_table._add(
    atomic_number=87,
    symbol='Fr',
    name='Francium',
    atomic_weight="[223]"
)

periodic_table._add(
    atomic_number=88,
    symbol='Ra',
    name='Radium',
    atomic_weight="[226]"
)

periodic_table._add(
    atomic_number=89,
    symbol='Ac',
    name='Actinium',
    atomic_weight="[227]"
)

periodic_table._add(
    atomic_number=90,
    symbol='Th',
    name='Thorium',
    atomic_weight="232.03806(2)"
)

periodic_table._add(
    atomic_number=91,
    symbol='Pa',
    name='Protactinium',
    atomic_weight="231.03588(2)"
)

periodic_table._add(
    atomic_number=92,
    symbol='U',
    name='Uranium',
    atomic_weight="238.02891(3)"
)

periodic_table._add(
    atomic_number=93,
    symbol='Np',
    name='Neptunium',
    atomic_weight="[237]"
)

periodic_table._add(
    atomic_number=94,
    symbol='Pu',
    name='Plutonium',
    atomic_weight="[244]"
)

periodic_table._add(
    atomic_number=95,
    symbol='Am',
    name='Americium',
    atomic_weight="[243]"
)

periodic_table._add(
    atomic_number=96,
    symbol='Cm',
    name='Curium',
    atomic_weight="[247]"
)

periodic_table._add(
    atomic_number=97,
    symbol='Bk',
    name='Berkelium',
    atomic_weight="[247]"
)

periodic_table._add(
    atomic_number=98,
    symbol='Cf',
    name='Californium',
    atomic_weight="[251]"
)

periodic_table._add(
    atomic_number=99,
    symbol='Es',
    name='Einsteinium',
    atomic_weight="[252]"
)

periodic_table._add(
    atomic_number=100,
    symbol='Fm',
    name='Fermium',
    atomic_weight="[257]"
)

periodic_table._add(
    atomic_number=101,
    symbol='Md',
    name='Mendelevium',
    atomic_weight="[258]"
)

periodic_table._add(
    atomic_number=102,
    symbol='No',
    name='Nobelium',
    atomic_weight="[259]"
)

periodic_table._add(
    atomic_number=103,
    symbol='Lr',
    name='Lawrencium',
    atomic_weight="[266]"
)

periodic_table._add(
    atomic_number=104,
    symbol='Rf',
    name='Rutherfordium',
    atomic_weight="[267]"
)

periodic_table._add(
    atomic_number=105,
    symbol='Db',
    name='Dubnium',
    atomic_weight="[268]"
)

periodic_table._add(
    atomic_number=106,
    symbol='Sg',
    name='Seaborgium',
    atomic_weight="[269]"
)

periodic_table._add(
    atomic_number=107,
    symbol='Bh',
    name='Bohrium',
    atomic_weight="[270]"
)

periodic_table._add(
    atomic_number=108,
    symbol='Hs',
    name='Hassium',
    atomic_weight="[269]"
)

periodic_table._add(
    atomic_number=109,
    symbol='Mt',
    name='Meitnerium',
    atomic_weight="[278]"
)

periodic_table._add(
    atomic_number=110,
    symbol='Ds',
    name='Darmstadtium',
    atomic_weight="[281]"
)

periodic_table._add(
    atomic_number=111,
    symbol='Rg',
    name='Roentgenium',
    atomic_weight="[281]"
)

periodic_table._add(
    atomic_number=112,
    symbol='Cn',
    name='Copernicium',
    atomic_weight="[285]"
)

periodic_table._add(
    atomic_number=113,
    symbol='Uut',
    name='Ununtrium',
    atomic_weight="[286]"
)

periodic_table._add(
    atomic_number=114,
    symbol='Fl',
    name='Flerovium',
    atomic_weight="[289]"
)

periodic_table._add(
    atomic_number=115,
    symbol='Uup',
    name='Ununpentium',
    atomic_weight="[289]"
)

periodic_table._add(
    atomic_number=116,
    symbol='Lv',
    name='Livermorium',
    atomic_weight="[293]"
)

periodic_table._add(
    atomic_number=117,
    symbol='Uus',
    name='Ununseptium',
    atomic_weight="[294]"
)

periodic_table._add(
    atomic_number=118,
    symbol='Uuo',
    name='Ununoctium',
    atomic_weight="[294]"
)
