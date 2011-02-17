###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
from os import sep

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import spin_loop
from status import Status; status = Status()


class Pdc(SystemTestCase):
    """TestCase class for the functional tests for the support of different peak intensity files."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create a data pipe.
        self.interpreter.pipe.create('mf', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_pdc_read_r1(self):
        """Test the reading of a PDC R1 file."""

        # Read the sequence data.
        self.interpreter.sequence.read(file="seq", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'pdc_files', res_num_col=2, res_name_col=1)

        # Read the PDC file.
        self.interpreter.pdc.read(file="testT1.txt", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'pdc_files')

        # The R1 values and errors.
        r1 = [2.1929824561403506, 2.3315458148752621, 2.3479690068091101, 2.2487069934787498, 2.2789425706472195, 2.2202486678507993, 2.2396416573348263, 1.9677292404565132, 2.0876826722338206, 1.9972039145196723, 2.1640337589266392, 2.2722108611679164, 2.198768689533861, 2.2794620469569185, 2.0863759649488838, 2.2841480127912286, 2.1079258010118043, 2.2426553038797934, 2.3496240601503762, 2.2747952684258417, 2.4666995559940799, 2.3952095808383236, 2.1331058020477816, 2.3623907394283012, 2.3849272597185784, 2.3266635644485807, 2.4201355275895451, 2.3719165085388996, 2.3430178069353325, 2.1929824561403506, 2.2381378692927485, 2.2461814914645104, 1.9908421262193909, 2.2935779816513762, 2.254791431792559, 2.2241992882562278, 2.2794620469569185, 2.1724961981316535, 2.2794620469569185, 2.2660321776569226, 2.1720243266724588, 2.1910604732690624, 2.201188641866608, 2.113718030014796, 2.2441651705565531, 2.1335609131640707, 2.0458265139116203, 2.1920210434020166, 2.2747952684258417, 2.369106846718787, 2.2977941176470589, 2.3769907297361539, 2.2256843979523704, 2.2846698652044779, 2.3419203747072599, 1.9735543714229324, 2.164970772894566, 2.3191094619666046, 2.1891418563922942, 2.1810250817884405, 2.2675736961451247, 2.2461814914645104, 2.2487069934787498, 2.3153507756425098, 2.1758050478677111, 2.1635655560363478, 1.8566654288897142, 1.6121231662098985, 1.1622501162250116, 0.76335877862595414]
        r1_err = [0.01200965609744685, 0.010001269606943386, 0.014497328483275753, 0.017805986279093564, 0.016018667863406139, 0.017175189438147654, 0.026656491007505816, 0.031887779033080439, 0.023244092500188742, 0.020492456637261992, 0.029405891083078388, 0.01724495081874064, 0.01461697060810881, 0.02232974258295586, 0.02572151337315175, 0.010559282318387871, 0.016876893309262682, 0.017643913187751065, 0.014456078128988579, 0.016222388027422298, 0.031349594240368733, 0.01381795555426827, 0.031593715633575291, 0.014850296101237673, 0.01433010139959676, 0.014886542679656093, 0.028008532399493073, 0.016853421056507993, 0.022990136348984259, 0.0077526838964126618, 0.0087903861457864114, 0.0095823570170703309, 0.016406914713081141, 0.014017596021854406, 0.0082353341440280434, 0.0080224854977105717, 0.038356180461015923, 0.019400343009578245, 0.019328035658745031, 0.012053816426506214, 0.035782740545298959, 0.021649400748203228, 0.029269621811524992, 0.018562879666725228, 0.014902420831105908, 0.013092542922620737, 0.015532366084086535, 0.016241586270343469, 0.015471314987942781, 0.01280177019270343, 0.010884638690164417, 0.012051066637543139, 0.012052360296519725, 0.0098552267333291456, 0.01648523123453919, 0.011617590201411589, 0.010998422685668165, 0.0089587926554740432, 0.010297080815262576, 0.01703057555352612, 0.027715540546853271, 0.0075177053019219947, 0.013878906064287936, 0.012018326494346573, 0.015157605152070361, 0.012308323508744523, 0.020378703408850622, 0.030416664636750697, 0.037868020828549613, 0.0070054979630267845]

        # Loop over the spins.
        i = 0
        for spin in spin_loop():
            # Check the R1 value and error.
            self.assertAlmostEqual(spin.relax_data[0], r1[i])
            self.assertAlmostEqual(spin.relax_error[0], r1_err[i])

            # Increment the data index.
            i += 1
