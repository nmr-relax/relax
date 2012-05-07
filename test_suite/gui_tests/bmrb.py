###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""GUI tests for the BMRB related activities."""

# Python module imports.
from os import sep

# relax module imports.
from generic_fns.pipes import VALID_TYPES
from status import Status; status = Status()
from test_suite.gui_tests.base_classes import GuiTestCase

# relax GUI imports.
from gui.misc import str_to_gui
from gui import uf_pages
from gui.wizard import Wiz_window


class Bmrb(GuiTestCase):
    """Class for testing the BMRB related functions in the GUI."""


    def test_bmrb_rw(self):
        """Test the reading and writing of BMRB files.

        This test should match that of the system test script bmrb_rw.py.
        """

        # Create a wizard instance to be used in all user function pages.
        self._wizard = Wiz_window(self.app.gui)

        # Create the data pipe.
        self.execute_uf(uf_name='pipe.create', pipe_name='results', pipe_type='mf')

        # Read the results.
        self.execute_uf(uf_name='results.read', file='final_results_trunc_1.3', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'OMP')

        # Play with the data.
        self.execute_uf(uf_name='deselect.all')
        self.execute_uf(uf_name='spin.copy', spin_from=':9', spin_to=':9@NE')
        self.execute_uf(uf_name='select.spin', spin_id=':9')
        self.execute_uf(uf_name='select.spin', spin_id=':10')
        self.execute_uf(uf_name='select.spin', spin_id=':11')
        self.execute_uf(uf_name='spin.name', name='N')
        self.execute_uf(uf_name='spin.element', element='N')
        self.execute_uf(uf_name='molecule.name', name='OMP')
        self.execute_uf(uf_name='molecule.type', type='protein')
        self.execute_uf(uf_name='bmrb.thiol_state', state='reduced')

        # Display the data (as a test).
        self.execute_uf(uf_name='relax_data.display', ri_id='R1_800')

        # Temperature control and peak intensity type.
        ri_ids = ['R1_600', 'R2_600', 'NOE_600', 'R1_800', 'R2_800', 'NOE_800']
        for i in range(6):
            self.execute_uf(uf_name='relax_data.temp_calibration', ri_id=ri_ids[i], method='methanol')
            self.execute_uf(uf_name='relax_data.temp_control', ri_id=ri_ids[i], method='single fid interleaving')
            self.execute_uf(uf_name='relax_data.peak_intensity_type', ri_id=ri_ids[i], type='height')

        # Set up some BMRB information.
        self.execute_uf(uf_name='bmrb.software_select', name='NMRPipe')
        self.execute_uf(uf_name='bmrb.software_select', name='Sparky', version='3.106')

        self.execute_uf(uf_name='bmrb.citation', cite_id='test', authors=[["Edward", "d'Auvergne", "E.", "J."], ["Paul", "Gooley", "P.", "R."]], doi="10.1039/b702202f", pubmed_id="17579774", full_citation="d'Auvergne E. J., Gooley P. R. (2007). Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm. Mol. Biosyst., 3(7), 483-494.", title="Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm.", status="published", type="journal", journal_abbrev="Mol. Biosyst.", journal_full="Molecular Biosystems", volume=3, issue=7, page_first=483, page_last=498, year=2007)
        self.execute_uf(uf_name='bmrb.software', name='X', url='http://www.nmr-relax.com', vendor_name='me', cite_ids=['test'], tasks=['procrastinating', 'nothing much', 'wasting time'])
        self.execute_uf(uf_name='bmrb.script', file='noe.py', dir=status.install_path+sep+'sample_scripts', analysis_type='noe', engine='relax')
        self.execute_uf(uf_name='bmrb.script', file='relax_fit.py', dir=status.install_path+sep+'sample_scripts', analysis_type='relax_fit', engine='relax')
        self.execute_uf(uf_name='bmrb.script', file='dauvergne_protocol.py', dir=status.install_path+sep+'sample_scripts'+sep+'model_free', analysis_type='mf', model_selection='AIC', engine='relax', model_elim=True, universal_solution=True)

        # Write, then read the data to a new data pipe.
        self.execute_uf(uf_name='bmrb.write', file=ds.tmpfile, dir=None, version=ds.version, force=True)
        self.execute_uf(uf_name='pipe.create', pipe_name='new', pipe_type='mf')
        self.execute_uf(uf_name='bmrb.read', file=ds.tmpfile, version=ds.version)

        # Display tests.
        self.execute_uf(uf_name='sequence.display')
        self.execute_uf(uf_name='relax_data.display', ri_id='R1_800')

        # Save the program state.
        self.execute_uf(uf_name='state.save', file='devnull', force=True)
