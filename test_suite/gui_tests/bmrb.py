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
        self.execute_uf(page=uf_pages.pipe.Create_page, pipe_name='results', pipe_type='mf')

        # Read the results.
        results_read = uf_pages.results.Read_page(self._wizard)
        results_read.file.SetValue(str_to_gui(status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'OMP'+sep+'final_results_trunc_1.3'))
        results_read.on_execute()

        # Play with the data.
        deselect_all = uf_pages.deselect.All_page(self._wizard)
        deselect_all.on_execute()

        spin_copy = uf_pages.spin.Copy_page(self._wizard)
        spin_copy.res_from.SetValue(str_to_gui('9 None'))
        spin_copy.res_num_to.SetValue(str_to_gui('9'))
        spin_copy.spin_name_to.SetValue(str_to_gui('NE'))
        spin_copy.on_execute()

        select_spin = uf_pages.select.Spin_page(self._wizard)
        select_spin.spin_id.SetValue(str_to_gui(':9'))
        select_spin.on_execute()
        select_spin.spin_id.SetValue(str_to_gui(':10'))
        select_spin.on_execute()
        select_spin.spin_id.SetValue(str_to_gui(':11'))
        select_spin.on_execute()

        spin_name = uf_pages.spin.Name_page(self._wizard)
        spin_name.name.SetValue(str_to_gui('N'))
        spin_name.on_execute()

        spin_element = uf_pages.spin.Element_page(self._wizard)
        spin_element.spin_id.SetValue(str_to_gui('N'))
        spin_element.on_execute()

        #molecule_name = uf_pages.molecule.Name_page(self._wizard)
        #molecule_name.name.SetValue(str_to_gui('OMP'))
        #molecule_name.type.SetValue(str_to_gui('protein'))
        #molecule_name.on_execute()

        #bmrb_thiol_state = uf_pages.bmrb.Thiol_state_page(self._wizard)
        #bmrb_thiol_state.state.SetValue(str_to_gui('reduced'))
        #bmrb_thiol_state.on_execute()

        # Display the data (as a test).
        #relax_data_display = uf_pages.relax_data.Display_page(self._wizard)
        #relax_data_display.ri_id.SetValue(str_to_gui('R1_800'))
        #relax_data_display.on_execute()

        # Temperature control and peak intensity type.
        ri_ids = ['R1_600', 'R2_600', 'NOE_600', 'R1_800', 'R2_800', 'NOE_800']
        for i in range(6):
            pass
            #relax_data_temp_calibration = uf_pages.relax_data.Temp_calibration_page(self._wizard)
            #relax_data_temp_calibration.ri_id.SetValue(str_to_gui(ri_ids[i]))
            #relax_data_temp_calibration.method.SetValue(str_to_gui('methanol'))
            #relax_data_temp_calibration.on_execute()

            #relax_data_temp_control = uf_pages.relax_data.Temp_control_page(self._wizard)
            #relax_data_temp_control.ri_id.SetValue(str_to_gui(ri_ids[i]))
            #relax_data_temp_control.method.SetValue(str_to_gui('single fid interleaving'))
            #relax_data_temp_control.on_execute()

            #relax_data_peak_intensity_type = uf_pages.relax_data.Peak_intensity_type_page(self._wizard)
            #relax_data_peak_intensity_type.ri_id.SetValue(str_to_gui(ri_ids[i]))
            #relax_data_peak_intensity_type.type.SetValue(str_to_gui('height'))
            #relax_data_peak_intensity_type.on_execute()

        # Set up some BMRB information.
        #bmrb_software_select = uf_pages.bmrb.Software_select_page(self._wizard)
        #bmrb_software_select.name.SetValue(str_to_gui('NMRPipe'))
        #bmrb_software_select.on_execute()
        #bmrb_software_select.name.SetValue(str_to_gui('Sparky'))
        #bmrb_software_select.version.SetValue(str_to_gui('3.106'))
        #bmrb_software_select.on_execute()

        self.execute_uf(page=uf_pages.bmrb.Citation_page, cite_id='test', authors=[["Edward", "d'Auvergne", "E.", "J."], ["Paul", "Gooley", "P.", "R."]], doi="10.1039/b702202f", pubmed_id="17579774", full_citation="d'Auvergne E. J., Gooley P. R. (2007). Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm. Mol. Biosyst., 3(7), 483-494.", title="Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm.", status="published", type="journal", journal_abbrev="Mol. Biosyst.", journal_full="Molecular Biosystems", volume=3, issue=7, page_first=483, page_last=498, year=2007)

        #bmrb.software(name='X', url='http://www.nmr-relax.com', vendor_name='me', cite_ids=['test'], tasks=['procrastinating', 'nothing much', 'wasting time'])

        #bmrb.script(file='noe.py', dir=status.install_path+sep+'sample_scripts', analysis_type='noe', engine='relax')
        #bmrb.script(file='relax_fit.py', dir=status.install_path+sep+'sample_scripts', analysis_type='relax_fit', engine='relax')
        #bmrb.script(file='dauvergne_protocol.py', dir=status.install_path+sep+'sample_scripts'+sep+'model_free', analysis_type='mf', model_selection='AIC', engine='relax', model_elim=True, universal_solution=True)

        # Write, then read the data to a new data pipe.
        #bmrb.write(file=ds.tmpfile, dir=None, version=ds.version, force=True)
        #pipe.create(pipe_name='new', pipe_type='mf')
        #bmrb.read(file=ds.tmpfile, version=ds.version)

        # Display tests.
        #sequence.display()
        #relax_data.display(ri_id='R1_800')

        # Save the program state.
        #state.save('devnull', force=True)
