###############################################################################
#                                                                             #
# Copyright (C) 2004-2008 Edward d'Auvergne                                   #
# Copyright (C) 2007-2008 Sebastien Morin                                     #
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

# Python module imports.
from re import search
from string import replace

# relax module imports.
from base_class import Common_functions
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import exists_mol_res_spin_data, return_spin, spin_loop
from generic_fns import pipes
from maths_fns.consistency_tests import Consistency
from physical_constants import N15_CSA, NH_BOND_LENGTH, h_bar, mu0, return_gyromagnetic_ratio
from relax_errors import RelaxError, RelaxFuncSetupError, RelaxNoPipeError, RelaxNoSequenceError, RelaxNoValueError, RelaxProtonTypeError, RelaxSpinTypeError


class Consistency_tests(Common_functions):
    def __init__(self):
        """Class containing functions specific to consistency testing."""


    def calculate(self, verbosity=1, sim_index=None, spin_id=None):
        """Calculation of the consistency functions."""

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Test if the frequency has been set.
        if not hasattr(cdp, 'ct_frq') or type(cdp.ct_frq) != float:
            raise RelaxError, "The frequency has not been set up."

        # Test if the sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Test if the CSA, bond length, angle Theta and correlation time values have been set.
        for spin in spin_loop(spin_id):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Test if the CSA value has been set.
            if not hasattr(spin, 'csa') or spin.csa == None:
                raise RelaxNoValueError, "CSA"

            # Test if the bond length has been set.
            if not hasattr(spin, 'r') or spin.r == None:
                raise RelaxNoValueError, "bond length"

            # Test if the angle Theta has been set.
            if not hasattr(spin, 'orientation') or spin.orientation == None:
                raise RelaxNoValueError, "angle Theta"

            # Test if the correlation time has been set.
            if not hasattr(spin, 'tc') or spin.tc == None:
                raise RelaxNoValueError, "correlation time"

            # Test if the spin type has been set.
            if not hasattr(spin, 'heteronuc_type'):
                raise RelaxSpinTypeError

            # Test if the type attached proton has been set.
            if not hasattr(spin, 'proton_type'):
                raise RelaxProtonTypeError

        # Frequency index.
        if cdp.ct_frq not in cdp.frq:
            raise RelaxError, "No relaxation data corresponding to the frequency " + `cdp.ct_frq` + " has been loaded."

        # Consistency testing.
        for spin in spin_loop(spin_id):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Residue specific frequency index.
            frq_index = None
            for j in xrange(spin.num_frq):
                if spin.frq[j] == cdp.ct_frq:
                    frq_index = j
            if frq_index == None:
                continue

            # Set the r1, r2, and NOE to None.
            r1 = None
            r2 = None
            noe = None

            # Get the R1, R2, and NOE values corresponding to the set frequency.
            for j in xrange(spin.num_ri):
                # R1.
                if spin.remap_table[j] == frq_index and spin.ri_labels[j] == 'R1':
                    if sim_index == None:
                        r1 = spin.relax_data[j]
                    else:
                        r1 = spin.relax_sim_data[sim_index][j]

                # R2.
                if spin.remap_table[j] == frq_index and spin.ri_labels[j] == 'R2':
                    if sim_index == None:
                        r2 = spin.relax_data[j]
                    else:
                        r2 = spin.relax_sim_data[sim_index][j]

                # NOE.
                if spin.remap_table[j] == frq_index and spin.ri_labels[j] == 'NOE':
                    if sim_index == None:
                        noe = spin.relax_data[j]
                    else:
                        noe = spin.relax_sim_data[sim_index][j]

            # Skip the residue if not all of the three value exist.
            if r1 == None or r2 == None or noe == None:
                continue

            # Initialise the function to calculate.
            self.ct = Consistency(frq=cdp.ct_frq, gx=return_gyromagnetic_ratio(spin.heteronuc_type), gh=return_gyromagnetic_ratio(spin.proton_type), mu0=mu0, h_bar=h_bar)

            # Calculate the consistency tests values.
            j0, f_eta, f_r2 = self.ct.func(orientation=spin.orientation, tc=spin.tc, r=spin.r, csa=spin.csa, r1=r1, r2=r2, noe=noe)

            # Consistency tests values.
            if sim_index == None:
                spin.j0 = j0
                spin.f_eta = f_eta
                spin.f_r2 = f_r2

            # Monte Carlo simulated consistency tests values.
            else:
                # Initialise the simulation data structures.
                self.data_init(spin, sim=1)
                if spin.j0_sim == None:
                    spin.j0_sim = []
                    spin.f_eta_sim = []
                    spin.f_r2_sim = []

                # Consistency tests values.
                spin.j0_sim.append(j0)
                spin.f_eta_sim.append(f_eta)
                spin.f_r2_sim.append(f_r2)


    def create_mc_data(self, spin_id):
        """Return the Ri data structure for the corresponding spin.

        @param spin_id: The spin identification string, as yielded by the base_data_loop() generator
                        method.
        @type spin_id:  str
        @return:        The Monte Carlo simulation data.
        @rtype:         list of floats
        """

        # Get the spin container.
        spin = return_spin(spin_id)

        # Return the data.
        return spin.relax_data


    def data_init(self, data, sim=0):
        """Function for initialising the data structures."""

        # Get the data names.
        data_names = self.data_names()

        # Loop over the data structure names.
        for name in data_names:
            # Simulation data structures.
            if sim:
                # Add '_sim' to the names.
                name = name + '_sim'

            # If the name is not in 'data', add it.
            if not hasattr(data, name):
                # Set the attribute.
                setattr(data, name, None)


    def data_names(self, set=None, error_names=False, sim_names=False):
        """Return a list of all spin container specific consistency testing object names.

        Description
        ===========

        The names are as follows:

            r:  Bond length.
            csa:  CSA value.
            heteronuc_type:  The heteronucleus type.
            orientation:  Angle between the 15N-1H vector and the principal axis of the 15N chemical
                          shift tensor.
            tc:  Correlation time.
            j0:  Spectral density value at 0 MHz.
            f_eta:  Eta-test (from Fushman D. et al. (1998) JACS, 120: 10947-10952).
            f_r2:  R2-test (from Fushman D. et al. (1998) JACS, 120: 10947-10952).


        @keyword set:           An unused variable.
        @type set:              ignored
        @keyword error_names:   A flag which if True will add the error object names as well.
        @type error_names:      bool
        @keyword sim_names:     A flag which if True will add the Monte Carlo simulation object
                                names as well.
        @type sim_names:        bool
        @return:                The list of object names.
        @rtype:                 list of str
        """

        # Initialise.
        names = []

        # Values.
        names.append('r')
        names.append('csa')
        names.append('heteronuc_type')
        names.append('orientation')
        names.append('tc')

        # Consistency tests values.
        names.append('j0')
        names.append('f_eta')
        names.append('f_r2')

        # Return the names.
        return names


    def default_value(self, param):
        """
        Consistency testing default values
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        These default values are found in the file 'physical_constants.py'.

         ______________________________________________________________________________________ 
        |                                       |                    |                         |
        | Data type                             | Object name        | Value                   |
        |_______________________________________|____________________|_________________________|
        |                                       |                    |                         |
        | Bond length                           | 'r'                | 1.02 * 1e-10            |
        |                                       |                    |                         |
        | CSA                                   | 'csa'              | -172 * 1e-6             |
        |                                       |                    |                         |
        | Heteronucleus type                    | 'heteronuc_type'   | '15N'                   |
        |                                       |                    |                         |
        | Proton type                           | 'proton_type'      | '1H'                    |
        |                                       |                    |                         |
        | Angle Theta                           | 'orientation'      | 15.7                    |
        |                                       |                    |                         |
        | Correlation time                      | 'tc'               | 13 * 1e-9               |
        |_______________________________________|____________________|_________________________|

        """
        __docformat__ = "plaintext"

        # Bond length.
        if param == 'r':
            return NH_BOND_LENGTH

        # CSA.
        elif param == 'csa':
            return N15_CSA

        # Heteronucleus type.
        elif param == 'heteronuc_type':
            return '15N'

        # Proton type.
        elif param == 'proton_type':
            return '1H'

        # Angle Theta (default value)
        elif param == 'orientation':
            return 15.7

        # Correlation time (default value)
        elif param == 'tc':
            return 13 * 1e-9


    def overfit_deselect(self):
        """Function for deselecting spins without sufficient data to support calculation"""

        # Test if the sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over spin data:
        for spin in spin_loop():

            # Check for sufficient data
            if not hasattr(spin, 'relax_data'):
                spin.select = 0
                continue

            # Require 3 or more data points
            if len(spin.relax_data) < 3:
                spin.select = 0
                continue


    def return_data_name(self, name):
        """
        Consistency testing data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

         __________________________________________________________________________________________
        |                       |                  |                                               |
        | Data type             | Object name      | Patterns                                      |
        |_______________________|__________________|_______________________________________________|
        |                       |                  |                                               |
        | J(0)                  | 'j0'             | '^[Jj]0$' or '[Jj]\(0\)'                      |
        |                       |                  |                                               |
        | F_eta                 | 'f_eta'          | '^[Ff]_[Ee][Tt][Aa]$'                         |
        |                       |                  |                                               |
        | F_R2                  | 'f_r2'           | '^[Ff]_[Rr]2$'                                |
        |                       |                  |                                               |
        | Bond length           | 'r'              | '^r$' or '[Bb]ond[ -_][Ll]ength'              |
        |                       |                  |                                               |
        | CSA                   | 'csa'            | '^[Cc][Ss][Aa]$'                              |
        |                       |                  |                                               |
        | Heteronucleus type    | 'heteronuc_type' | '^[Hh]eteronucleus$'                          |
        |                       |                  |                                               |
        | Proton type           | 'proton_type'    | '^[Pp]roton$'                                 |
        |                       |                  |                                               |
        | Angle Theta           | 'orientation'    | '^[Oo]rientation$'                            |
        |                       |                  |                                               |
        | Correlation time      | 'tc'             | '^[Tt]c$'                                     |
        |_______________________|__________________|_______________________________________________|
        """
        __docformat__ = "plaintext"

        # J(0).
        if search('^[Jj]0$', name) or search('[Jj]\(0\)', name):
            return 'j0'

        # F_eta.
        if search('^[Ff]_[Ee][Tt][Aa]$', name):
            return 'f_eta'

        # F_R2.
        if search('^^[Ff]_[Rr]2$', name):
            return 'f_r2'

        # Bond length.
        if search('^r$', name) or search('[Bb]ond[ -_][Ll]ength', name):
            return 'r'

        # CSA.
        if search('^[Cc][Ss][Aa]$', name):
            return 'csa'

        # Heteronucleus type.
        if search('^[Hh]eteronucleus$', name):
            return 'heteronuc_type'

        # Proton type.
        if search('^[Pp]roton$', name):
            return 'proton_type'

        # Angle Theta
        if search('^[Oo]rientation$', name):
            return 'orientation'

        # Correlation time
        if search('^[Tt]c$', name):
            return 'tc'


    def return_grace_string(self, data_type):
        """Function for returning the Grace string representing the data type for axis labelling."""

        # Get the object name.
        object_name = self.return_data_name(data_type)

        # J(0).
        if object_name == 'j0':
            return '\\qJ(0)\\Q'

        # J(wX).
        elif object_name == 'f_eta':
            return '\\qF\\s\\xh\\Q'

        # J(wH).
        elif object_name == 'f_r2':
            return '\\qF\\sR2\\Q'

        # Bond length.
        elif object_name == 'r':
            return 'Bond length'

        # CSA.
        elif object_name == 'csa':
            return '\\qCSA\\Q'

        # Angle Theta
        elif object_name == 'orientation':
            return '\\q\\xq\\Q'

        # Correlation time
        elif object_name == 'tc':
            return '\\q\\xt\\f{}c\\Q'


    def return_units(self, data_type):
        """Function for returning a string representing the parameters units.

        For example, the internal representation of te is in seconds, whereas the external
        representation is in picoseconds, therefore this function will return the string
        'picoseconds' for te.
        """

        # Get the object name.
        object_name = self.return_data_name(data_type)

        # Bond length (Angstrom).
        if object_name == 'r':
            return 'Angstrom'

        # CSA (ppm).
        elif object_name == 'csa':
            return 'ppm'

        # Angle Theta
        elif object_name == 'orientation':
            return 'degrees'

        # Correlation time
        elif object_name == 'tc':
            return 'ns'


    def set_doc(self, value=None, error=None, param=None, spin=None):
        """
        Consistency testing set details
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        In consistency testing, only four values can be set, the bond length, CSA, angle
        Theta ('orientation') and correlation time values. These must be set prior to the
        calculation of consistency functions.

        """
        __docformat__ = "plaintext"


    def set_frq(self, frq=None):
        """Function for selecting which relaxation data to use in the consistency tests."""

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Test if the current pipe exists.
        if not ds.current_pipe:
            raise RelaxNoPipeError

        # Test if the pipe type is set to 'ct'.
        function_type = ds[ds.current_pipe].pipe_type
        if function_type != 'ct':
            raise RelaxFuncSetupError, specific_fns.setup.get_string(function_type)

        # Test if the frequency has been set.
        if hasattr(cdp, 'ct_frq'):
            raise RelaxError, "The frequency for the run has already been set."

        # Create the data structure if it doesn't exist.
        if not hasattr(cdp, 'ct_frq'):
            cdp.ct_frq = {}

        # Set the frequency.
        cdp.ct_frq = frq


    def set_error(self, spin, index, error):
        """Function for setting parameter errors."""

        # Return J(0) sim data.
        if index == 0:
            spin.j0_err = error

        # Return F_eta sim data.
        if index == 1:
            spin.f_eta_err = error

        # Return F_R2 sim data.
        if index == 2:
            spin.f_r2_err = error


    def sim_return_param(self, spin, index):
        """Function for returning the array of simulation parameter values."""

        # Skip deselected residues.
        if not spin.select:
                return

        # Return J(0) sim data.
        if index == 0:
            return spin.j0_sim

        # Return F_eta sim data.
        if index == 1:
            return spin.f_eta_sim

        # Return F_R2 sim data.
        if index == 2:
            return spin.f_r2_sim


    def sim_return_selected(self, spin):
        """Function for returning the array of selected simulation flags."""

        # Multiple spins.
        return spin.select_sim


    def sim_pack_data(self, spin_id, sim_data):
        """Pack the Monte Carlo simulation data.

        @param spin_id:     The spin identification string, as yielded by the base_data_loop()
                            generator method.
        @type spin_id:      str
        @param sim_data:    The Monte Carlo simulation data.
        @type sim_data:     list of float
        """

        # Get the spin container.
        spin = return_spin(spin_id)

        # Test if the simulation data already exists.
        if hasattr(spin, 'relax_sim_data'):
            raise RelaxError, "Monte Carlo simulation data already exists."

        # Create the data structure.
        spin.relax_sim_data = sim_data


    def write_columnar_line(self, file=None, num=None, name=None, select=None, data_set=None, heteronuc_type=None, wH=None, j0=None, f_eta=None, f_r2=None, r=None, csa=None, orientation=None, tc=None, ri_labels=None, remap_table=None, frq_labels=None, frq=None, ri=None, ri_error=None):
        """Function for printing a single line of the columnar formatted results."""

        # Residue number and name.
        file.write("%-4s %-5s " % (num, name))

        # Selected flag and data set.
        file.write("%-9s %-9s " % (select, data_set))

        # Nucleus.
        file.write("%-7s " % heteronuc_type)

        # Proton frequency.
        file.write("%-25s " % wH)

        # Parameters.
        file.write("%-25s " % j0)
        file.write("%-25s " % f_eta)
        file.write("%-25s " % f_r2)
        file.write("%-25s " % r)
        file.write("%-25s " % csa)
        file.write("%-25s " % orientation)
        file.write("%-25s " % tc)

        # Relaxation data setup.
        if ri_labels:
            file.write("%-40s " % ri_labels)
            file.write("%-25s " % remap_table)
            file.write("%-25s " % frq_labels)
            file.write("%-30s " % frq)

        # Relaxation data.
        if ri:
            for i in xrange(len(ri)):
                if ri[i] == None:
                    file.write("%-25s " % 'None')
                else:
                    file.write("%-25s " % ri[i])

        # Relaxation errors.
        if ri_error:
            for i in xrange(len(ri_error)):
                if ri_error[i] == None:
                    file.write("%-25s " % 'None')
                else:
                    file.write("%-25s " % ri_error[i])

        # End of the line.
        file.write("\n")


    def write_columnar_results(self, file):
        """Function for printing the results into a file."""

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Test if the current pipe exists.
        if not ds.current_pipe:
            raise RelaxNoPipeError

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError


        # Header.
        #########

        # Relaxation data and errors.
        ri = []
        ri_error = []
        if hasattr(ds, 'num_ri'):
            for i in xrange(cdp.num_ri):
                ri.append('Ri_(' + cdp.ri_labels[i] + "_" + cdp.frq_labels[cdp.remap_table[i]] + ")")
                ri_error.append('Ri_error_(' + cdp.ri_labels[i] + "_" + cdp.frq_labels[cdp.remap_table[i]] + ")")

        # Write the header line.
        self.write_columnar_line(file=file, num='Num', name='Name', select='Selected', data_set='Data_set', heteronuc_type='Nucleus', wH='Proton_frq_(MHz)', j0='J(0)', f_eta='F_eta', f_r2='F_R2', r='Bond_length_(A)', csa='CSA_(ppm)', orientation='Angle_Theta_(degrees)', tc='Correlation_time_(ns)', ri_labels='Ri_labels', remap_table='Remap_table', frq_labels='Frq_labels', frq='Frequencies', ri=ri, ri_error=ri_error)


        # Values.
        #########

        # Nucleus.
        heteronuc_type = self.relax.generic.nuclei.find_heteronuc_type()

        # The proton frequency in MHz.
        wH = cdp.ct_frq / 1e6

        # Relaxation data setup.
        try:
            ri_labels = replace(`cdp.ri_labels`, ' ', '')
            remap_table = replace(`cdp.remap_table`, ' ', '')
            frq_labels = replace(`cdp.frq_labels`, ' ', '')
            frq = replace(`cdp.frq`, ' ', '')
        except AttributeError:
            ri_labels = `None`
            remap_table = `None`
            frq_labels = `None`
            frq = `None`

        # Loop over the sequence.
        for i in xrange(len(cdp.res)):
            # Reassign data structure.
            data = cdp.res[i]

            # J(0).
            j0 = None
            if hasattr(data, 'j0'):
                j0 = data.j0

            # F_eta.
            f_eta = None
            if hasattr(data, 'f_eta'):
                f_eta = data.f_eta

            # F_R2.
            f_r2 = None
            if hasattr(data, 'f_r2'):
                f_r2 = data.f_r2

            # Bond length.
            r = None
            if hasattr(data, 'r') and data.r != None:
                r = data.r / 1e-10

            # CSA.
            csa = None
            if hasattr(data, 'csa') and data.csa != None:
                csa = data.csa / 1e-6

            # Relaxation data and errors.
            ri = []
            ri_error = []
            if hasattr(cdp, 'num_ri'):
                for i in xrange(cdp.num_ri):
                    try:
                        # Find the residue specific data corresponding to i.
                        index = None
                        for j in xrange(data.num_ri):
                            if data.ri_labels[j] == cdp.ri_labels[i] and data.frq_labels[data.remap_table[j]] == cdp.frq_labels[cdp.remap_table[i]]:
                                index = j

                        # Data exists for this data type.
                        ri.append(spin)
                        ri_error.append(spin)

                    # No data exists for this data type.
                    except:
                        ri.append(None)
                        ri_error.append(None)

            # Write the line.
            self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, data_set='value', heteronuc_type=heteronuc_type, wH=`wH`, j0=`j0`, f_eta=`f_eta`, f_r2=`f_r2`, r=`r`, csa=`csa`, orientation=`orientation`, tc=`tc`, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Errors.
        #########

        # Skip this section and the next if no simulations have been setup.
        if not hasattr(cdp, 'sim_state'):
            return
        elif cdp.sim_state == 0:
            return

        # Loop over the sequence.
        for i in xrange(len(cdp.res)):
            # Reassign data structure.
            data = cdp.res[i]

            # J(0).
            j0 = None
            if hasattr(data, 'j0_err'):
                j0 = data.j0_err

            # F_eta.
            f_eta = None
            if hasattr(data, 'f_eta_err'):
                f_eta = data.f_eta_err

            # F_R2.
            f_r2 = None
            if hasattr(data, 'f_r2_err'):
                f_r2 = data.f_r2_err

            # Bond length.
            r = None
            if hasattr(data, 'r_err') and data.r_err != None:
                r = data.r_err / 1e-10

            # CSA.
            csa = None
            if hasattr(data, 'csa_err') and data.csa_err != None:
                csa = data.csa_err / 1e-6

            # Angle Theta.
            orientation = None
            if hasattr(data, 'orientation_err') and data.orientation_err != None:
                orientation = data.orientation_err

            # Correlation time.
            tc = None
            if hasattr(data, 'tc_err') and data.tc_err != None:
                tc = data.tc_err / 1e-6

            # Relaxation data and errors.
            ri = []
            ri_error = []
            for i in xrange(cdp.num_ri):
                ri.append(None)
                ri_error.append(None)

            # Write the line.
            self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, data_set='error', heteronuc_type=heteronuc_type, wH=`wH`, j0=`j0`, f_eta=`f_eta`, f_r2=`f_r2`, r=`r`, csa=`csa`, orientation=`orientation`, tc=`tc`, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Simulation values.
        ####################

        # Loop over the simulations.
        for i in xrange(cdp.sim_number):
            # Loop over the sequence.
            for j in xrange(len(cdp.res)):
                # Reassign data structure.
                data = cdp.res[j]

                # J(0).
                j0 = None
                if hasattr(data, 'j0_sim'):
                    j0 = data.j0_sim[i]

                # F_eta.
                f_eta = None
                if hasattr(data, 'f_eta_sim'):
                    f_eta = data.f_eta_sim[i]

                # F_R2.
                f_r2 = None
                if hasattr(data, 'f_r2_sim'):
                    f_r2 = data.f_r2_sim[i]

                # Bond length.
                r = None
                if hasattr(data, 'r_sim') and data.r_sim != None and data.r_sim[i] != None:
                    r = data.r_sim[i] / 1e-10

                # CSA.
                csa = None
                if hasattr(data, 'csa_sim') and data.csa_sim != None and data.csa_sim[i] != None:
                    csa = data.csa_sim[i] / 1e-6

                # Angle Theta.
                orientation = None
                if hasattr(data, 'orientation_sim') and data.orientation_sim != None and data.orientation_sim[i] != None:
                    orientation = data.orientation_sim[i]

                # Correlation time.
                tc = None
                if hasattr(data, 'tc_sim') and data.tc_sim != None and data.tc_sim[i] != None:
                    tc = data.tc_sim[i] / 1e-6

                # Relaxation data and errors.
                ri = []
                ri_error = []
                if hasattr(cdp, 'num_ri'):
                    for k in xrange(cdp.num_ri):
                        try:
                            # Find the residue specific data corresponding to k.
                            index = None
                            for l in xrange(data.num_ri):
                                if data.ri_labels[l] == cdp.ri_labels[k] and data.frq_labels[data.remap_table[l]] == cdp.frq_labels[cdp.remap_table[k]]:
                                    index = l

                            # Data exists for this data type.
                            ri.append(spin)
                            ri_error.append(spin)

                        # No data exists for this data type.
                        except:
                            ri.append(None)
                            ri_error.append(None)

                # Write the line.
                self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, data_set='sim_'+`i`, heteronuc_type=heteronuc_type, wH=`wH`, j0=`j0`, f_eta=`f_eta`, f_r2=`f_r2`, r=`r`, csa=`csa`, orientation=`orientation`, tc=`tc`, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)
