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
"""Module containing a Python object representation of the period table."""

# relax module imports.
from lib.errors import RelaxError


class Periodic_table:
    """The periodic table object."""

    def __init__(self):
        """Set up the object."""

        # Initialise some data structures.
        self.symbol = []
        self.name = []


    def add(self, atomic_number=None, symbol=None, name=None):
        """Add an element to the table.

        @keyword atomic_number:     The atomic number.
        @type atomic_number:        int
        @keyword symbol:            The atomic symbol.
        @type symbol:               str
        @keyword name:              The chemical element name.
        @type name:                 str
        """

        # Check that atomic_number is correctly ordered.
        if atomic_number != len(self.symbol)+1:
            raise RelaxError("Incorrect setup.")

        # Append the values.
        self.symbol.append(symbol)
        self.name.append(name)


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
periodic_table.add(
    atomic_number=1,
    symbol='H',
    name='Hydrogen'
)

periodic_table.add(
    atomic_number=2,
    symbol='He',
    name='Helium'
)

periodic_table.add(
    atomic_number=3,
    symbol='Li',
    name='Lithium'
)

periodic_table.add(
    atomic_number=4,
    symbol='Be',
    name='Beryllium'
)

periodic_table.add(
    atomic_number=5,
    symbol='B',
    name='Boron'
)

periodic_table.add(
    atomic_number=6,
    symbol='C',
    name='Carbon'
)

periodic_table.add(
    atomic_number=7,
    symbol='N',
    name='Nitrogen'
)

periodic_table.add(
    atomic_number=8,
    symbol='O',
    name='Oxygen'
)

periodic_table.add(
    atomic_number=9,
    symbol='F',
    name='Fluorine'
)

periodic_table.add(
    atomic_number=10,
    symbol='Ne',
    name='Neon'
)

periodic_table.add(
    atomic_number=11,
    symbol='Na',
    name='Sodium'
)

periodic_table.add(
    atomic_number=12,
    symbol='Mg',
    name='Magnesium'
)

periodic_table.add(
    atomic_number=13,
    symbol='Al',
    name='Aluminium'
)

periodic_table.add(
    atomic_number=14,
    symbol='Si',
    name='Silicon'
)

periodic_table.add(
    atomic_number=15,
    symbol='P',
    name='Phosphorus'
)

periodic_table.add(
    atomic_number=16,
    symbol='S',
    name='Sulfur'
)

periodic_table.add(
    atomic_number=17,
    symbol='Cl',
    name='Chlorine'
)

periodic_table.add(
    atomic_number=18,
    symbol='Ar',
    name='Argon'
)

periodic_table.add(
    atomic_number=19,
    symbol='K',
    name='Potassium'
)

periodic_table.add(
    atomic_number=20,
    symbol='Ca',
    name='Calcium'
)

periodic_table.add(
    atomic_number=21,
    symbol='Sc',
    name='Scandium'
)

periodic_table.add(
    atomic_number=22,
    symbol='Ti',
    name='Titanium'
)

periodic_table.add(
    atomic_number=23,
    symbol='V',
    name='Vanadium'
)

periodic_table.add(
    atomic_number=24,
    symbol='Cr',
    name='Chromium'
)

periodic_table.add(
    atomic_number=25,
    symbol='Mn',
    name='Manganese'
)

periodic_table.add(
    atomic_number=26,
    symbol='Fe',
    name='Iron'
)

periodic_table.add(
    atomic_number=27,
    symbol='Co',
    name='Cobalt'
)

periodic_table.add(
    atomic_number=28,
    symbol='Ni',
    name='Nickel'
)

periodic_table.add(
    atomic_number=29,
    symbol='Cu',
    name='Copper'
)

periodic_table.add(
    atomic_number=30,
    symbol='Zn',
    name='Zinc'
)

periodic_table.add(
    atomic_number=31,
    symbol='Ga',
    name='Gallium'
)

periodic_table.add(
    atomic_number=32,
    symbol='Ge',
    name='Germanium'
)

periodic_table.add(
    atomic_number=33,
    symbol='As',
    name='Arsenic'
)

periodic_table.add(
    atomic_number=34,
    symbol='Se',
    name='Selenium'
)

periodic_table.add(
    atomic_number=35,
    symbol='Br',
    name='Bromine'
)

periodic_table.add(
    atomic_number=36,
    symbol='Kr',
    name='Krypton'
)

periodic_table.add(
    atomic_number=37,
    symbol='Rb',
    name='Rubidium'
)

periodic_table.add(
    atomic_number=38,
    symbol='Sr',
    name='Strontium'
)

periodic_table.add(
    atomic_number=39,
    symbol='Y',
    name='Yttrium'
)

periodic_table.add(
    atomic_number=40,
    symbol='Zr',
    name='Zirconium'
)

periodic_table.add(
    atomic_number=41,
    symbol='Nb',
    name='Niobium'
)

periodic_table.add(
    atomic_number=42,
    symbol='Mo',
    name='Molybdenum'
)

periodic_table.add(
    atomic_number=43,
    symbol='Tc',
    name='Technetium'
)

periodic_table.add(
    atomic_number=44,
    symbol='Ru',
    name='Ruthenium'
)

periodic_table.add(
    atomic_number=45,
    symbol='Rh',
    name='Rhodium'
)

periodic_table.add(
    atomic_number=46,
    symbol='Pd',
    name='Palladium'
)

periodic_table.add(
    atomic_number=47,
    symbol='Ag',
    name='Silver'
)

periodic_table.add(
    atomic_number=48,
    symbol='Cd',
    name='Cadmium'
)

periodic_table.add(
    atomic_number=49,
    symbol='In',
    name='Indium'
)

periodic_table.add(
    atomic_number=50,
    symbol='Sn',
    name='Tin'
)

periodic_table.add(
    atomic_number=51,
    symbol='Sb',
    name='Antimony'
)

periodic_table.add(
    atomic_number=52,
    symbol='Te',
    name='Tellurium'
)

periodic_table.add(
    atomic_number=53,
    symbol='I',
    name='Iodine'
)

periodic_table.add(
    atomic_number=54,
    symbol='Xe',
    name='Xenon'
)

periodic_table.add(
    atomic_number=55,
    symbol='Cs',
    name='Caesium'
)

periodic_table.add(
    atomic_number=56,
    symbol='Ba',
    name='Barium'
)

periodic_table.add(
    atomic_number=57,
    symbol='La',
    name='Lanthanum'
)

periodic_table.add(
    atomic_number=58,
    symbol='Ce',
    name='Cerium'
)

periodic_table.add(
    atomic_number=59,
    symbol='Pr',
    name='Praseodymium'
)

periodic_table.add(
    atomic_number=60,
    symbol='Nd',
    name='Neodymium'
)

periodic_table.add(
    atomic_number=61,
    symbol='Pm',
    name='Promethium'
)

periodic_table.add(
    atomic_number=62,
    symbol='Sm',
    name='Samarium'
)

periodic_table.add(
    atomic_number=63,
    symbol='Eu',
    name='Europium'
)

periodic_table.add(
    atomic_number=64,
    symbol='Gd',
    name='Gadolinium'
)

periodic_table.add(
    atomic_number=65,
    symbol='Tb',
    name='Terbium'
)

periodic_table.add(
    atomic_number=66,
    symbol='Dy',
    name='Dysprosium'
)

periodic_table.add(
    atomic_number=67,
    symbol='Ho',
    name='Holmium'
)

periodic_table.add(
    atomic_number=68,
    symbol='Er',
    name='Erbium'
)

periodic_table.add(
    atomic_number=69,
    symbol='Tm',
    name='Thulium'
)

periodic_table.add(
    atomic_number=70,
    symbol='Yb',
    name='Ytterbium'
)

periodic_table.add(
    atomic_number=71,
    symbol='Lu',
    name='Lutetium'
)

periodic_table.add(
    atomic_number=72,
    symbol='Hf',
    name='Hafnium'
)

periodic_table.add(
    atomic_number=73,
    symbol='Ta',
    name='Tantalum'
)

periodic_table.add(
    atomic_number=74,
    symbol='W',
    name='Tungsten'
)

periodic_table.add(
    atomic_number=75,
    symbol='Re',
    name='Rhenium'
)

periodic_table.add(
    atomic_number=76,
    symbol='Os',
    name='Osmium'
)

periodic_table.add(
    atomic_number=77,
    symbol='Ir',
    name='Iridium'
)

periodic_table.add(
    atomic_number=78,
    symbol='Pt',
    name='Platinum'
)

periodic_table.add(
    atomic_number=79,
    symbol='Au',
    name='Gold'
)

periodic_table.add(
    atomic_number=80,
    symbol='Hg',
    name='Mercury'
)

periodic_table.add(
    atomic_number=81,
    symbol='Tl',
    name='Thallium'
)

periodic_table.add(
    atomic_number=82,
    symbol='Pb',
    name='Lead'
)

periodic_table.add(
    atomic_number=83,
    symbol='Bi',
    name='Bismuth'
)

periodic_table.add(
    atomic_number=84,
    symbol='Po',
    name='Polonium'
)

periodic_table.add(
    atomic_number=85,
    symbol='At',
    name='Astatine'
)

periodic_table.add(
    atomic_number=86,
    symbol='Rn',
    name='Radon'
)

periodic_table.add(
    atomic_number=87,
    symbol='Fr',
    name='Francium'
)

periodic_table.add(
    atomic_number=88,
    symbol='Ra',
    name='Radium'
)

periodic_table.add(
    atomic_number=89,
    symbol='Ac',
    name='Actinium'
)

periodic_table.add(
    atomic_number=90,
    symbol='Th',
    name='Thorium'
)

periodic_table.add(
    atomic_number=91,
    symbol='Pa',
    name='Protactinium'
)

periodic_table.add(
    atomic_number=92,
    symbol='U',
    name='Uranium'
)

periodic_table.add(
    atomic_number=93,
    symbol='Np',
    name='Neptunium'
)

periodic_table.add(
    atomic_number=94,
    symbol='Pu',
    name='Plutonium'
)

periodic_table.add(
    atomic_number=95,
    symbol='Am',
    name='Americium'
)

periodic_table.add(
    atomic_number=96,
    symbol='Cm',
    name='Curium'
)

periodic_table.add(
    atomic_number=97,
    symbol='Bk',
    name='Berkelium'
)

periodic_table.add(
    atomic_number=98,
    symbol='Cf',
    name='Californium'
)

periodic_table.add(
    atomic_number=99,
    symbol='Es',
    name='Einsteinium'
)

periodic_table.add(
    atomic_number=100,
    symbol='Fm',
    name='Fermium'
)

periodic_table.add(
    atomic_number=101,
    symbol='Md',
    name='Mendelevium'
)

periodic_table.add(
    atomic_number=102,
    symbol='No',
    name='Nobelium'
)

periodic_table.add(
    atomic_number=103,
    symbol='Lr',
    name='Lawrencium'
)

periodic_table.add(
    atomic_number=104,
    symbol='Rf',
    name='Rutherfordium'
)

periodic_table.add(
    atomic_number=105,
    symbol='Db',
    name='Dubnium'
)

periodic_table.add(
    atomic_number=106,
    symbol='Sg',
    name='Seaborgium'
)

periodic_table.add(
    atomic_number=107,
    symbol='Bh',
    name='Bohrium'
)

periodic_table.add(
    atomic_number=108,
    symbol='Hs',
    name='Hassium'
)

periodic_table.add(
    atomic_number=109,
    symbol='Mt',
    name='Meitnerium'
)

periodic_table.add(
    atomic_number=110,
    symbol='Ds',
    name='Darmstadtium'
)

periodic_table.add(
    atomic_number=111,
    symbol='Rg',
    name='Roentgenium'
)

periodic_table.add(
    atomic_number=112,
    symbol='Cn',
    name='Copernicium'
)

periodic_table.add(
    atomic_number=113,
    symbol='Uut',
    name='Ununtrium'
)

periodic_table.add(
    atomic_number=114,
    symbol='Fl',
    name='Flerovium'
)

periodic_table.add(
    atomic_number=115,
    symbol='Uup',
    name='Ununpentium'
)

periodic_table.add(
    atomic_number=116,
    symbol='Lv',
    name='Livermorium'
)

periodic_table.add(
    atomic_number=117,
    symbol='Uus',
    name='Ununseptium'
)

periodic_table.add(
    atomic_number=118,
    symbol='Uuo',
    name='Ununoctium'
)
