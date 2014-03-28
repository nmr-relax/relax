###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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
"""The Molmol and Pymol base macro methods of the specific API for model-free analysis."""

# Python module imports.
from math import pi
from re import search

# relax module imports.
from colour import linear_gradient
from lib.errors import RelaxError, RelaxStyleError, RelaxUnknownDataTypeError
from pipe_control.mol_res_spin import spin_loop



class Macro:
    """The base class for the model-free analysis Molmol and PyMOL macro creation."""

    def classic_style(self, data_type=None, colour_start=None, colour_end=None, colour_list=None, spin_id=None):
        """The classic macro style.

        @keyword data_type:     The parameter name or data type.
        @type data_type:        str
        @keyword colour_start:  The starting colour (must be a MOLMOL or X11 name).
        @type colour_start:     str
        @keyword colour_end:    The ending colour (must be a MOLMOL or X11 name).
        @type colour_end:       str
        @keyword colour_list:   The colour list used, either 'molmol' or 'x11'.
        @type colour_list:      str
        @keyword spin_id:       The spin identification string.
        @type spin_id:          str
        """

        # Generate the macro header.
        ############################

        self.classic_header()


        # S2.
        #####

        if data_type == 's2':
            # Loop over the spins.
            for spin, mol_name, res_num, res_name in spin_loop(spin_id, full_info=True):
                # Skip deselected spins or spins with no model information set.
                if not spin.select or not hasattr(spin, 'model'):
                    continue

                # Skip spins which don't have an S2 value.
                if not hasattr(spin, 's2') or spin.s2 == None:
                    continue

                # S2 width and colour for the backbone NH.
                if spin.name == 'N':
                    self.classic_order_param(res_num, spin.s2, colour_start, colour_end, colour_list)


        # S2f.
        ######

        elif data_type == 's2f':
            # Loop over the spins.
            for spin, mol_name, res_num, res_name in spin_loop(spin_id, full_info=True):
                # Skip deselected spins or spins with no model information set.
                if not spin.select or not hasattr(spin, 'model'):
                    continue

                # The backbone NH.
                if spin.name == 'N':
                    # Colour residues which don't have an S2f value white.
                    if not hasattr(spin, 's2f') or spin.s2f == None:
                        self.classic_colour(res_num=res_num, width=0.3, rgb_array=[1, 1, 1])

                    # S2f width and colour.
                    else:
                        self.classic_order_param(res_num, spin.s2f, colour_start, colour_end, colour_list)


        # S2s.
        ######

        elif data_type == 's2s':
            # Loop over the spins.
            for spin, mol_name, res_num, res_name in spin_loop(spin_id, full_info=True):
                # Skip deselected spins or spins with no model information set.
                if not spin.select or not hasattr(spin, 'model'):
                    continue

                # The backbone NH.
                if spin.name == 'N':
                    # Colour residues which don't have an S2s value white.
                    if not hasattr(spin, 's2s') or spin.s2s == None:
                        self.classic_colour(res_num=res_num, width=0.3, rgb_array=[1, 1, 1])

                    # S2s width and colour.
                    else:
                        self.classic_order_param(res_num, spin.s2s, colour_start, colour_end, colour_list)


        # Amplitude of fast motions.
        ############################

        elif data_type == 'amp_fast':
            # Loop over the spins.
            for spin, mol_name, res_num, res_name in spin_loop(spin_id, full_info=True):
                # Skip deselected spins or spins with no model information set.
                if not spin.select or not hasattr(spin, 'model'):
                    continue

                # The model.
                if search('tm[0-9]', spin.model):
                    model = spin.model[1:]
                else:
                    model = spin.model

                # The backbone NH.
                if spin.name == 'N':
                    # S2f width and colour (for models m5 to m8).
                    if hasattr(spin, 's2f') and spin.s2f != None:
                        self.classic_order_param(res_num, spin.s2f, colour_start, colour_end, colour_list)

                    # S2 width and colour (for models m1 and m3).
                    elif model == 'm1' or model == 'm3':
                        self.classic_order_param(res_num, spin.s2, colour_start, colour_end, colour_list)

                    # S2 width and colour (for models m2 and m4 when te <= 200 ps).
                    elif (model == 'm2' or model == 'm4') and spin.te <= 200e-12:
                        self.classic_order_param(res_num, spin.s2, colour_start, colour_end, colour_list)

                    # White bonds (for models m2 and m4 when te > 200 ps).
                    elif (model == 'm2' or model == 'm4') and spin.te > 200e-12:
                        self.classic_colour(res_num=res_num, width=0.3, rgb_array=[1, 1, 1])


        # Amplitude of slow motions.
        ############################

        elif data_type == 'amp_slow':
            # Loop over the spins.
            for spin, mol_name, res_num, res_name in spin_loop(spin_id, full_info=True):
                # Skip deselected spins or spins with no model information set.
                if not spin.select or not hasattr(spin, 'model'):
                    continue

                # The model.
                if search('tm[0-9]', spin.model):
                    model = spin.model[1:]
                else:
                    model = spin.model

                # The backbone NH.
                if spin.name == 'N':
                    # S2 width and colour (for models m5 to m8).
                    if hasattr(spin, 'ts') and spin.ts != None:
                        self.classic_order_param(res_num, spin.s2, colour_start, colour_end, colour_list)

                    # S2 width and colour (for models m2 and m4 when te > 200 ps).
                    elif (model == 'm2' or model == 'm4') and spin.te > 200 * 1e-12:
                        self.classic_order_param(res_num, spin.s2, colour_start, colour_end, colour_list)

                    # White bonds for fast motions.
                    else:
                        self.classic_colour(res_num=res_num, width=0.3, rgb_array=[1, 1, 1])

        # te.
        #####

        elif data_type == 'te':
            # Loop over the spins.
            for spin, mol_name, res_num, res_name in spin_loop(spin_id, full_info=True):
                # Skip deselected spins or spins with no model information set.
                if not spin.select or not hasattr(spin, 'model'):
                    continue

                # Skip spins which don't have a te value.
                if not hasattr(spin, 'te') or spin.te == None:
                    continue

                # te width and colour (backbone NH).
                if spin.name == 'N':
                    self.classic_correlation_time(res_num, spin.te, colour_start, colour_end, colour_list)


        # tf.
        #####

        elif data_type == 'tf':
            # Loop over the spins.
            for spin, mol_name, res_num, res_name in spin_loop(spin_id, full_info=True):
                # Skip deselected spins or spins with no model information set.
                if not spin.select or not hasattr(spin, 'model'):
                    continue

                # Skip spins which don't have a tf value.
                if not hasattr(spin, 'tf') or spin.tf == None:
                    continue

                # tf width and colour (backbone NH).
                if spin.name == 'N':
                    self.classic_correlation_time(res_num, spin.tf, colour_start, colour_end, colour_list)


        # ts.
        #####

        elif data_type == 'ts':
            # Loop over the spins.
            for spin, mol_name, res_num, res_name in spin_loop(spin_id, full_info=True):
                # Skip deselected spins or spins with no model information set.
                if not spin.select or not hasattr(spin, 'model'):
                    continue

                # Skip spins which don't have a ts value.
                if not hasattr(spin, 'ts') or spin.ts == None:
                    continue

                # The default start and end colours.
                if colour_start == None:
                    colour_start = 'blue'
                if colour_end == None:
                    colour_end = 'black'

                # ts width and colour (backbone NH).
                if spin.name == 'N':
                    self.classic_correlation_time(res_num, spin.ts / 10.0, colour_start, colour_end, colour_list)


        # Timescale of fast motions.
        ############################

        elif data_type == 'time_fast':
            # Loop over the spins.
            for spin, mol_name, res_num, res_name in spin_loop(spin_id, full_info=True):
                # Skip deselected spins or spins with no model information set.
                if not spin.select or not hasattr(spin, 'model'):
                    continue

                # The model.
                if search('tm[0-9]', spin.model):
                    model = spin.model[1:]
                else:
                    model = spin.model

                # The backbone NH.
                if spin.name == 'N':
                    # tf width and colour (for models m5 to m8).
                    if hasattr(spin, 'tf') and spin.tf != None:
                        self.classic_correlation_time(res_num, spin.tf, colour_start, colour_end, colour_list)

                    # te width and colour (for models m2 and m4 when te <= 200 ps).
                    elif (model == 'm2' or model == 'm4') and spin.te <= 200e-12:
                        self.classic_correlation_time(res_num, spin.te, colour_start, colour_end, colour_list)

                    # All other residues are assumed to have a fast correlation time of zero (statistically zero, not real zero!).
                    # Colour these bonds white.
                    else:
                        self.classic_colour(res_num=res_num, width=0.3, rgb_array=[1, 1, 1])


        # Timescale of slow motions.
        ############################

        elif data_type == 'time_slow':
            # Loop over the spins.
            for spin, mol_name, res_num, res_name in spin_loop(spin_id, full_info=True):
                # Skip deselected spins or spins with no model information set.
                if not spin.select or not hasattr(spin, 'model'):
                    continue

                # The model.
                if search('tm[0-9]', spin.model):
                    model = spin.model[1:]
                else:
                    model = spin.model

                # The default start and end colours.
                if colour_start == None:
                    colour_start = 'blue'
                if colour_end == None:
                    colour_end = 'black'

                # The backbone NH.
                if spin.name == 'N':
                    # ts width and colour (for models m5 to m8).
                    if hasattr(spin, 'ts') and spin.ts != None:
                        self.classic_correlation_time(res_num, spin.ts / 10.0, colour_start, colour_end, colour_list)

                    # te width and colour (for models m2 and m4 when te > 200 ps).
                    elif (model == 'm2' or model == 'm4') and spin.te > 200e-12:
                        self.classic_correlation_time(res_num, spin.te / 10.0, colour_start, colour_end, colour_list)

                    # White bonds for the rest.
                    else:
                        self.classic_colour(res_num=res_num, width=0.3, rgb_array=[1, 1, 1])


        # Rex.
        ######

        elif data_type == 'rex':
            # Loop over the spins.
            for spin, mol_name, res_num, res_name in spin_loop(spin_id, full_info=True):
                # Skip deselected spins or spins with no model information set.
                if not spin.select or not hasattr(spin, 'model'):
                    continue

                # The backbone NH.
                if spin.name == 'N':
                    # Residues which chemical exchange.
                    if hasattr(spin, 'rex') and spin.rex != None:
                        self.classic_rex(res_num, spin.rex, colour_start, colour_end, colour_list)

                    # White bonds for the rest.
                    else:
                        self.classic_colour(res_num=res_num, width=0.3, rgb_array=[1, 1, 1])


        # Unknown data type.
        ####################

        else:
            raise RelaxUnknownDataTypeError(data_type)


    def classic_correlation_time(self, res_num, te, colour_start, colour_end, colour_list):
        """Function for generating the bond width and colours for correlation times."""

        # The te value in picoseconds.
        te = te * 1e12

        # The bond width (aiming for a width range of 2 to 0 for te values of 0 to 10 ns).
        width = 2.0 - 200.0 / (te + 100.0)

        # Catch invalid widths.
        if width <= 0.0:
            width = 0.001

        # Colour value (hyperbolic).
        colour_value = 1.0 / (te / 100.0 + 1.0)

        # Catch invalid colours.
        if colour_value < 0.0:
            colour_value = 0.0
        elif colour_value > 1.0:
            colour_value = 1.0

        # Default colours.
        if colour_start == None:
            colour_start = 'turquoise'
        if colour_end == None:
            colour_end = 'blue'

        # Get the RGB colour array (swap the colours because of the inverted hyperbolic colour value).
        rgb_array = linear_gradient(colour_value, colour_end, colour_start, colour_list)

        # Colour the peptide bond.
        self.classic_colour(res_num, width, rgb_array)


    def classic_order_param(self, res_num, s2, colour_start, colour_end, colour_list):
        """Function for generating the bond width and colours for order parameters."""

        # The bond width (aiming for a width range of 2 to 0 for S2 values of 0.0 to 1.0).
        if s2 <= 0.0:
            width = 2.0
        else:
            width = 2.0 * (1.0 - s2**2)

        # Catch invalid widths.
        if width <= 0.0:
            width = 0.001

        # Colour value (quartic).
        colour_value = s2 ** 4

        # Catch invalid colours.
        if colour_value < 0.0:
            colour_value = 0.0
        elif colour_value > 1.0:
            colour_value = 1.0

        # Default colours.
        if colour_start == None:
            colour_start = 'red'
        if colour_end == None:
            colour_end = 'yellow'

        # Get the RGB colour array.
        rgb_array = linear_gradient(colour_value, colour_start, colour_end, colour_list)

        # Colour the peptide bond.
        self.classic_colour(res_num, width, rgb_array)


    def classic_rex(self, res_num, rex, colour_start, colour_end, colour_list):
        """Function for generating the bond width and colours for correlation times."""

        # The 1st spectrometer frequency.
        if not hasattr(cdp, 'spectrometer_frq'):
            raise RelaxError("No spectrometer frequency information is present in the current data pipe.")
        if hasattr(cdp, 'ri_ids'):
            frq = cdp.spectrometer_frq[cdp.ri_ids[0]]
        else:       # Take the highest frequency, if all else fails.
            frqs = sorted(cdp.spectrometer_frq.values())
            frq = frqs[-1]

        # The Rex value.
        rex = rex * (2.0 * pi * frq)**2

        # The bond width (aiming for a width range of 2 to 0 for Rex values of 0 to 25 s^-1).
        width = 2.0 - 2.0 / (rex/5.0 + 1.0)

        # Catch invalid widths.
        if width <= 0.0:
            width = 0.001

        # Colour value (hyperbolic).
        colour_value = 1.0 / (rex + 1.0)

        # Catch invalid colours.
        if colour_value < 0.0:
            colour_value = 0.0
        elif colour_value > 1.0:
            colour_value = 1.0

        # Default colours.
        if colour_start == None:
            colour_start = 'yellow'
        if colour_end == None:
            colour_end = 'red'

        # Get the RGB colour array (swap the colours because of the inverted hyperbolic colour value).
        rgb_array = linear_gradient(colour_value, colour_end, colour_start, colour_list)

        # Colour the peptide bond.
        self.classic_colour(res_num, width, rgb_array)


    def create_macro(self, data_type, style=None, colour_start=None, colour_end=None, colour_list=None, spin_id=None):
        """Create and return an array of macros of the model-free parameters.

        @param data_type:       The parameter name or data type.
        @type data_type:        str
        @keyword style:         The Molmol style.
        @type style:            None or str
        @keyword colour_start:  The starting colour (must be a MOLMOL or X11 name).
        @type colour_start:     str
        @keyword colour_end:    The ending colour (must be a MOLMOL or X11 name).
        @type colour_end:       str
        @keyword colour_list:   The colour list used, either 'molmol' or 'x11'.
        @type colour_list:      str
        @keyword spin_id:       The spin identification string.
        @type spin_id:          str
        """

        # Initialise.
        self.commands = []

        # The classic style.
        if style == 'classic':
            self.classic_style(data_type, colour_start, colour_end, colour_list, spin_id)

        # Unknown style.
        else:
            raise RelaxStyleError(style)

        # Return the command array.
        return self.commands
