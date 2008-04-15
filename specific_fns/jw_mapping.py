###############################################################################
#                                                                             #
# Copyright (C) 2004-2008 Edward d'Auvergne                                   #
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
from data import Data as relax_data_store
from base_class import Common_functions
from generic_fns.selection import exists_mol_res_spin_data, spin_loop
from maths_fns.jw_mapping import Mapping
from relax_errors import RelaxError, RelaxFuncSetupError, RelaxNoPipeError, RelaxNoSequenceError, RelaxNoValueError, RelaxNucleusError, RelaxParamSetError
from physical_constants import N15_CSA, NH_BOND_LENGTH, h_bar, mu0, return_gyromagnetic_ratio


class Jw_mapping(Common_functions):
    def __init__(self):
        """Class containing functions specific to reduced spectral density mapping."""


    def calculate(self, verbosity=1, sim_index=None, spin_id=None):
        """Calculation of the spectral density values."""

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test if the frequency has been set.
        if not hasattr(cdp, 'jw_frq') or type(cdp.jw_frq) != float:
            raise RelaxError, "The frequency has not been set up."

        # Test if the sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Test if the CSA and bond length values have been set.
        for spin in spin_loop(spin_id):
            # Skip unselected residues.
            if not spin.select:
                continue

            # Test if the CSA value has been set.
            if not hasattr(spin, 'csa') or spin.csa == None:
                raise RelaxNoValueError, "CSA"

            # Test if the bond length has been set.
            if not hasattr(spin, 'r') or spin.r == None:
                raise RelaxNoValueError, "bond length"

            # Test if the spin type has been set.
            if not hasattr(spin, 'heteronuc_type'):
                raise RelaxSpinTypeError

            # Test if the type attached proton has been set.
            if not hasattr(spin, 'proton_type'):
                raise RelaxProtonTypeError

        # Frequency index.
        if cdp.jw_frq not in cdp.frq:
            raise RelaxError, "No relaxation data corresponding to the frequency " + `cdp.jw_frq` + " has been loaded."

        # Reduced spectral density mapping.
        for spin in spin_loop(spin_id):

            # Skip unselected residues.
            if not spin.select:
                continue

            # Residue specific frequency index.
            frq_index = None
            for j in xrange(spin.num_frq):
                if spin.frq[j] == cdp.jw_frq:
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
            self.jw = Mapping(frq=cdp.jw_frq, gx=return_gyromagnetic_ratio(spin.heteronuc_type), gh=return_gyromagnetic_ratio(spin.proton_type), mu0=mu0, h_bar=h_bar)

            # Calculate the spectral density values.
            j0, jwx, jwh = self.jw.func(r=spin.r, csa=spin.csa, r1=r1, r2=r2, noe=noe)

            # Reduced spectral density values.
            if sim_index == None:
                spin.j0 = j0
                spin.jwx = jwx
                spin.jwh = jwh

            # Monte Carlo simulated reduced spectral density values.
            else:
                # Initialise the simulation data structures.
                self.spin_init(spin, sim=1)
                if spin.j0_sim == None:
                    spin.j0_sim = []
                    spin.jwx_sim = []
                    spin.jwh_sim = []

                # Reduced spectral density values.
                spin.j0_sim.append(j0)
                spin.jwx_sim.append(jwx)
                spin.jwh_sim.append(jwh)


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


    def data_names(self):
        """Function for returning a list of names of data structures.

        Description
        ~~~~~~~~~~~

        r:  Bond length.

        csa:  CSA value.

        heteronuc_type:  The heteronucleus type.

        j0:  Spectral density value at 0 MHz.

        jwx:  Spectral density value at the frequency of the heteronucleus.

        jwh:  Spectral density value at the frequency of the heteronucleus.
        """

        # Initialise.
        names = []

        # Values.
        names.append('r')
        names.append('csa')
        names.append('heteronuc_type')

        # Spectral density values.
        names.append('j0')
        names.append('jwx')
        names.append('jwh')

        return names


    def default_value(self, param):
        """
        Reduced spectral density mapping default values
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        These default values are found in the file 'physical_constants.py'.

        _______________________________________________________________________________________
        |                                       |                    |                        |
        | Data type                             | Object name        | Value                  |
        |_______________________________________|____________________|________________________|
        |                                       |                    |                        |
        | Bond length                           | 'r'                | 1.02 * 1e-10           |
        |                                       |                    |                        |
        | CSA                                   | 'csa'              | -172 * 1e-6            |
        |                                       |                    |                        |
        | Heteronucleus type                    | 'heteronuc_type'   | '15N'                  |
        |                                       |                    |                        |
        | Proton type                           | 'proton_type'      | '1H'                   |
        |_______________________________________|____________________|________________________|

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


    def overfit_deselect(self):
        """Function for deselecting spins without sufficient data to support calculation"""

        # Test the sequence data exists:
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
        Reduced spectral density mapping data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                        |                  |                                              |
        | Data type              | Object name      | Patterns                                     |
        |________________________|__________________|______________________________________________|
        |                        |                  |                                              |
        | J(0)                   | 'j0'             | '^[Jj]0$' or '[Jj]\(0\)'                     |
        |                        |                  |                                              |
        | J(wX)                  | 'jwx'            | '^[Jj]w[Xx]$' or '[Jj]\(w[Xx]\)'             |
        |                        |                  |                                              |
        | J(wH)                  | 'jwh'            | '^[Jj]w[Hh]$' or '[Jj]\(w[Hh]\)'             |
        |                        |                  |                                              |
        | Bond length            | 'r'              | '^r$' or '[Bb]ond[ -_][Ll]ength'             |
        |                        |                  |                                              |
        | CSA                    | 'csa'            | '^[Cc][Ss][Aa]$'                             |
        |                        |                  |                                              |
        | Heteronucleus type     | 'heteronuc_type' | '^[Hh]eteronucleus$'                         |
        |                        |                  |                                              |
        | Proton type            | 'proton_type'    | '^[Pp]roton$'                                |
        |________________________|__________________|______________________________________________|

        """
        __docformat__ = "plaintext"

        # J(0).
        if search('^[Jj]0$', name) or search('[Jj]\(0\)', name):
            return 'j0'

        # J(wX).
        if search('^[Jj]w[Xx]$', name) or search('[Jj]\(w[Xx]\)', name):
            return 'jwx'

        # J(wH).
        if search('^[Jj]w[Hh]$', name) or search('[Jj]\(w[Hh]\)', name):
            return 'jwh'

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


    def return_grace_string(self, data_type):
        """Function for returning the Grace string representing the data type for axis labelling."""

        # Get the object name.
        object_name = self.return_data_name(data_type)

        # J(0).
        if object_name == 'j0':
            return '\\qJ(0)\\Q'

        # J(wX).
        elif object_name == 'jwx':
            return '\\qJ(\\xw\\f{}\\sX\\N)\\Q'

        # J(wH).
        elif object_name == 'jwh':
            return '\\qJ(\\xw\\f{}\\sH\\N)\\Q'

        # Bond length.
        elif object_name == 'r':
            return 'Bond length'

        # CSA.
        elif object_name == 'csa':
            return '\\qCSA\\Q'


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


    def set_doc(self, value=None, error=None, param=None, spin=None):
        """
        Reduced spectral density mapping set details
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        In reduced spectral density mapping, three values must be set prior to the calculation of
        spectral density values:  the bond length, CSA, and heteronucleus type.
        """
        __docformat__ = "plaintext"


    def set_frq(self, frq=None):
        """Function for selecting which relaxation data to use in the J(w) mapping."""

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test if the current pipe exists.
        if not relax_data_store.current_pipe:
            raise RelaxNoPipeError

        # Test if the pipe type is set to 'jw'.
        function_type = relax_data_store[relax_data_store.current_pipe].pipe_type
        if function_type != 'jw':
            raise RelaxFuncSetupError, specific_fns.setup.get_string(function_type)

        # Test if the frequency has been set.
        if hasattr(cdp, 'jw_frq'):
            raise RelaxError, "The frequency has already been set."

        # Create the data structure if it doesn't exist.
        if not hasattr(cdp, 'jw_frq'):
           cdp.jw_frq = {}

        # Set the frequency.
        cdp.jw_frq = frq


    def set_error(self, spin, index, error):
        """Function for setting parameter errors."""

        # Return J(0) sim data.
        if index == 0:
            spin.j0_err = error

        # Return J(wX) sim data.
        if index == 1:
            spin.jwx_err = error

        # Return J(wH) sim data.
        if index == 2:
            spin.jwh_err = error


    def sim_return_param(self, spin, index):
        """Function for returning the array of simulation parameter values."""

        # Skip unselected residues.
        if not spin.select:
                return

        # Return J(0) sim data.
        if index == 0:
            return spin.j0_sim

        # Return J(wX) sim data.
        if index == 1:
            return spin.jwx_sim

        # Return J(wH) sim data.
        if index == 2:
            return spin.jwh_sim


    def sim_return_selected(self, spin):
        """Function for returning the array of selected simulation flags."""

        # Multiple spins.
        return spin.select_sim


    def set_selected_sim(self, select_sim, spin):
        """Function for returning the array of selected simulation flags."""

        # Multiple spins.
        spin.select_sim = select_sim


    def sim_pack_data(self, spin, sim_data):
        """Function for packing Monte Carlo simulation data."""

        # Test if the simulation data already exists.
        if hasattr(relax_data_store.res[run][i], 'relax_sim_data'):
            raise RelaxError, "Monte Carlo simulation data already exists."

        # Create the data structure.
        relax_data_store.res[run][i].relax_sim_data = sim_data


    def write_columnar_line(self, file=None, num=None, name=None, select=None, data_set=None, heteronuc_type=None, wH=None, j0=None, jwx=None, jwh=None, r=None, csa=None, ri_labels=None, remap_table=None, frq_labels=None, frq=None, ri=None, ri_error=None):
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
        file.write("%-25s " % jwx)
        file.write("%-25s " % jwh)
        file.write("%-25s " % r)
        file.write("%-25s " % csa)

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
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError


        # Header.
        #########

        # Relaxation data and errors.
        ri = []
        ri_error = []
        if hasattr(relax_data_store, 'num_ri'):
            for i in xrange(cdp.num_ri):
                ri.append('Ri_(' + cdp.ri_labels[i] + "_" + cdp.frq_labels[cdp.remap_table[i]] + ")")
                ri_error.append('Ri_error_(' + cdp.ri_labels[i] + "_" + cdp.frq_labels[cdp.remap_table[i]] + ")")

        # Write the header line.
        self.write_columnar_line(file=file, num='Num', name='Name', select='Selected', data_set='Data_set', heteronuc_type='Nucleus', wH='Proton_frq_(MHz)', j0='J(0)', jwx='J(wX)', jwh='J(wH)', r='Bond_length_(A)', csa='CSA_(ppm)', ri_labels='Ri_labels', remap_table='Remap_table', frq_labels='Frq_labels', frq='Frequencies', ri=ri, ri_error=ri_error)


        # Values.
        #########

        # Nucleus.
        heteronuc_type = self.relax.generic.nuclei.find_heteronuc_type()

        # The proton frequency in MHz.
        wH = cdp.jw_frq / 1e6

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
        for spin in spin_loop(spin_id):

            # Reassign data structure.
            data = cdp.res[i]

            # J(0).
            j0 = None
            if hasattr(spin, 'j0'):
                j0 = spin.j0

            # J(wX).
            jwx = None
            if hasattr(spin, 'jwx'):
                jwx = spin.jwx

            # J(wH).
            jwh = None
            if hasattr(spin, 'jwh'):
                jwh = spin.jwh

            # Bond length.
            r = None
            if hasattr(spin, 'r') and spin.r != None:
                r = spin.r / 1e-10

            # CSA.
            csa = None
            if hasattr(spin, 'csa') and spin.csa != None:
                csa = spin.csa / 1e-6

            # Relaxation data and errors.
            ri = []
            ri_error = []
            if hasattr(cdp, 'num_ri'):
                for i in xrange(cdp.num_ri):
                    try:
                        # Find the residue specific data corresponding to i.
                        index = None
                        for j in xrange(spin.num_ri):
                            if spin.ri_labels[j] == cdp.ri_labels[i] and spin.frq_labels[spin.remap_table[j]] == cdp.frq_labels[cdp.remap_table[i]]:
                                index = j

                        # Data exists for this data type.
                        ri.append(spin.relax_data[index])
                        ri_error.append(spin.relax_error[index])

                    # No data exists for this data type.
                    except:
                        ri.append(None)
                        ri_error.append(None)

            # Write the line.
            self.write_columnar_line(file=file, num=spin.num, name=spin.name, select=spin.select, spin_set='value', heteronuc_type=heteronuc_type, wH=`wH`, j0=`j0`, jwx=`jwx`, jwh=`jwh`, r=`r`, csa=`csa`, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Errors.
        #########

        # Skip this section and the next if no simulations have been setup.
        if not hasattr(cdp, 'sim_state'):
            return
        elif cdp.sim_state == 0:
            return

        # Loop over the sequence.
        for spin in spin_loop(spin_id):

            # J(0).
            j0 = None
            if hasattr(spin, 'j0_err'):
                j0 = spin.j0_err

            # J(wX).
            jwx = None
            if hasattr(spin, 'jwx_err'):
                jwx = spin.jwx_err

            # J(wH).
            jwh = None
            if hasattr(spin, 'jwh_err'):
                jwh = spin.jwh_err

            # Bond length.
            r = None
            if hasattr(spin, 'r_err') and spin.r_err != None:
                r = spin.r_err / 1e-10

            # CSA.
            csa = None
            if hasattr(spin, 'csa_err') and spin.csa_err != None:
                csa = spin.csa_err / 1e-6

            # Relaxation data and errors.
            ri = []
            ri_error = []
            for i in xrange(cdp.num_ri):
                ri.append(None)
                ri_error.append(None)

            # Write the line.
            self.write_columnar_line(file=file, num=spin.num, name=spin.name, select=spin.select, spin_set='error', heteronuc_type=heteronuc_type, wH=`wH`, j0=`j0`, jwx=`jwx`, jwh=`jwh`, r=`r`, csa=`csa`, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Simulation values.
        ####################

        # Loop over the simulations.
        for i in xrange(cdp.sim_number):
            # Loop over the sequence.
            for spin in spin_loop(spin_id):

                # J(0).
                j0 = None
                if hasattr(spin, 'j0_sim'):
                    j0 = spin.j0_sim[i]

                # J(wX).
                jwx = None
                if hasattr(spin, 'jwx_sim'):
                    jwx = spin.jwx_sim[i]

                # J(wH).
                jwh = None
                if hasattr(spin, 'jwh_sim'):
                    jwh = spin.jwh_sim[i]

                # Bond length.
                r = None
                if hasattr(spin, 'r_sim') and spin.r_sim != None and spin.r_sim[i] != None:
                    r = spin.r_sim[i] / 1e-10

                # CSA.
                csa = None
                if hasattr(spin, 'csa_sim') and spin.csa_sim != None and spin.csa_sim[i] != None:
                    csa = spin.csa_sim[i] / 1e-6

                # Relaxation data and errors.
                ri = []
                ri_error = []
                if hasattr(cdp, 'num_ri'):
                    for k in xrange(cdp.num.ri):
                        try:
                            # Find the residue specific data corresponding to k.
                            index = None
                            for l in xrange(spin.num_ri):
                                if spin.ri_labels[l] == cdp.ri_labels[k] and spin.frq_labels[spin.remap_table[l]] == cdp.frq_labels[cdp.remap_table[k]]:
                                    index = l

                            # Data exists for this data type.
                            ri.append(`spin.relax_sim_data[i][index]`)
                            ri_error.append(`spin.relax_error[index]`)

                        # No data exists for this data type.
                        except:
                            ri.append(None)
                            ri_error.append(None)

                # Write the line.
                self.write_columnar_line(file=file, num=spin.num, name=spin.name, select=spin.select, spin_set='sim_'+`i`, heteronuc_type=heteronuc_type, wH=`wH`, j0=`j0`, jwx=`jwx`, jwh=`jwh`, r=`r`, csa=`csa`, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)
