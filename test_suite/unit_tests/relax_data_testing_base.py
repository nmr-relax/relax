###############################################################################
#                                                                             #
# Copyright (C) 2007-2010 Edward d'Auvergne                                   #
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
import __main__
from os import sep
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes, sequence


class Relax_data_base_class:
    """Base class for the tests of the relaxation data tensor modules.

    This includes both the 'prompt.relax_data' and 'generic_fns.relax_data' modules.
    The base class also contains many shared unit tests.
    """


    def setUp(self):
        """Set up for all the relaxation data unit tests."""

        # Reset the relax data storage object.
        ds.__reset__()

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')

        # Add a second data pipe for copying tests.
        ds.add(pipe_name='test', pipe_type='mf')

        # Set the current data pipe to 'orig'.
        pipes.switch('orig')

        # The Ap4Aase 600 MHz NOE data.
        self.Ap4Aase_600_NOE_val = [None, None, None, 0.12479588727508535, 0.42240815792914105, 0.45281703194372114, 0.60727570079478255, 0.63871921623680161, None, None, None, 0.92927160307645906, 0.88832516377296256, 0.84945042565860407, 0.73027277534135793, 1.0529350986375761, 0.80025161548578949, 0.9225805138227271, None, 0.83690702968916975, 0.82750462671474634, 0.94498415442235661, None, 0.8935097799257431, 0.86456261089305875, 0.74923159572687958, 0.82028906681170666, 0.95078138769755005, 0.88196946543481614, 0.88560694800603623, None, 0.93583460370655014, 0.83709220285834895, 0.77065893466772672, 0.74898049254126575, 0.75473259762308997, None, 0.72339922138816593, 0.7409139945787665, 0.81036305956996824, 0.93259428996098348, None, None, None, 0.97484276729559749, 0.79870627747000578, 0.77846459298477833, 0.85891945210952814, 0.82545651205700832, 0.77308724653857397, 0.83873490797355599, 0.78962147119962445, None, None, 0.83658554344066838, 0.94444774229292805, 0.88892100988408906, 0.89074818049490534, 0.93798213161209065, 0.89579384792870853, 0.90689840050040216, 0.86826627855975114, 0.88998453873904826, 0.93193995326551327, 0.91380634390651083, 0.86088897739301773, 0.91200692603214106, 0.89667919287639897, 0.95894205272847033, 0.83602820831090652, 0.91434697423385458, 0.78332056488518564, 0.82655263496972042, 0.82607341906155618, 0.88040402181165589, 0.8440486006693505, None, 0.82043041764520075, 0.78703432521087158, 0.82699368240002646, 0.85174803791662423, None, 0.84885669819226628, 0.89183703777040746, None, None, 0.92544635676371245, 0.68656513923277818, 0.72560011690157689, 0.69795502821734268, 0.57079416490593249, None, 0.71563067539320835, None, 0.50533076429030188, None, 0.75242786769880365, 0.70895981542011155, None, 0.33272491279305588, None, 0.90094329970739295, 0.88707256046705585, 0.87992586160833552, 0.79195727809693339, 0.91358573817741873, 0.90242759014288332, 0.97529004068103053, 0.88453257922238127, 0.93282837259539797, 0.80050317711189245, 0.87281500262478917, 0.82161925495299371, 0.75331847553368936, 0.86583135026629754, 0.8423490949685033, 0.75544980660586103, 0.89663290907940885, 0.86241114220463833, 0.865189333746754, 0.76072465838213588, 0.8627935013491016, 0.58872842981275242, None, 0.66265488495054237, None, 0.6175482423717148, 0.57128306878306878, None, 0.65783414097673298, 0.78352915459861194, 0.90660549423688019, 0.69562244671213447, 0.8986224709427465, 0.93456283575144872, None, 0.96438783132840478, 0.88494476363170493, None, 0.81450919045756742, None, 0.89273806940361811, 0.89784704409243976, 0.89409823895739682, None, 0.75626758626525903, None, 0.81861161936806948, 0.77704881157681638, 0.93492416343713725, 0.80529201617441148, None, 0.75214448729046979, 0.77939624899611037, 0.88957406230133507, 0.83119933716570005, 0.91593660447979419, 1.0269367764915405, 0.95254605768690148, 0.80783819302725635, 0.91264712309949736, 0.87414218862982118, None, 0.8457055541736257, 0.7976400443272097]
        self.Ap4Aase_600_NOE_err = [None, None, None, 0.020551827436105764, 0.02016346825976852, 0.026272719841642134, 0.032369427242382849, 0.024695665815261791, None, None, None, 0.059569089743604184, 0.044119641308479306, 0.060533543601110441, 0.054366133132835504, 0.10226383618816391, 0.05217226473549319, 0.040042471153624366, None, 0.043355836219158402, 0.070804231151989958, 0.045958118280731972, None, 0.040080159235713876, 0.025516073550159439, 0.031147400155540676, 0.029551538089533019, 0.058781807250738359, 0.053798141218956298, 0.04058564845028198, None, 0.049964861028149038, 0.056277751722041303, 0.055862610530979066, 0.062426501508834664, 0.037655461974785032, None, 0.037437746270300623, 0.031899198795702917, 0.05883492648236429, 0.049025044758579737, None, None, None, 0.061101732084737577, 0.039371899134381119, 0.047660696280181554, 0.047240554321579087, 0.023582035074293468, 0.047687722096308678, 0.023196186303095979, 0.030389229790461863, None, None, 0.033964837875935606, 0.039442739174763576, 0.02652568603842493, 0.044926643986551523, 0.039072857662117114, 0.045558051667044089, 0.034817385027641354, 0.037932460586176255, 0.04416504039747577, 0.046692690948839703, 0.065323967027699076, 0.039701400872345881, 0.042298623934643773, 0.079080932418819722, 0.067928676079858738, 0.020489325306093879, 0.036174251087283844, 0.024485137678863723, 0.059736004586569386, 0.028861627878037942, 0.029401903503258862, 0.045460315556323593, None, 0.02537282712438679, 0.053007727294934082, 0.061355070294094288, 0.047992183164804886, None, 0.056269021809127781, 0.063703951001952613, None, None, 0.10564633090541133, 0.057727260927784539, 0.046307285409240992, 0.043081197184003071, 0.040201168842464927, None, 0.029680853171297025, None, 0.13110007530113085, None, 0.055416928281966663, 0.066345573350012677, None, 0.11395960586085771, None, 0.079438544471658351, 0.064210071948445219, 0.063995466359721184, 0.058755076446370007, 0.06960783712536886, 0.079202821774062071, 0.055639087817357311, 0.044727670551887241, 0.054122883235643848, 0.039242551779018732, 0.042620700259960162, 0.044970961360827032, 0.16191971307506142, 0.03075410906877173, 0.029862890782436795, 0.020403875440027055, 0.027212286424039007, 0.030489671728569135, 0.036801376842568193, 0.04239547098051423, 0.031102853835183651, 0.019647495159139456, None, 0.018633796971680151, None, 0.016649721653701773, 0.021020898014190763, None, 0.038324025574230064, 0.039477530263583097, 0.073251142306895001, 0.029252551207069242, 0.029800820512347403, 0.04190589192257109, None, 0.051973164180429951, 0.037885698528167658, None, 0.028795497444627904, None, 0.038102768163308702, 0.047105957099339957, 0.031888501753176597, None, 0.037573735892664904, None, 0.045323274177265373, 0.067437069694904428, 0.077974178652576179, 0.047904023844685867, None, 0.046470703715260887, 0.056734780619811562, 0.040848702413964474, 0.031770841283563625, 0.045827271513353023, 0.062189928910417011, 0.037543295138971443, 0.039174104595193118, 0.0406911452975608, 0.026051431683394789, None, 0.033339638549660086, 0.028434080259488268]


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_read(self):
        """Test the reading of relaxation data.

        The functions tested are both specific_fns.relax_data.read() and prompt.relax_data.read().
        """

        # First read the residue sequence out of the Ap4Aase 600 MHz NOE data file.
        sequence.read(file='Ap4Aase.Noe.600.bz2', dir=__main__.install_path+sep+'test_suite'+sep+'shared_data'+sep+'relaxation_data', res_num_col=1, res_name_col=2)

        # Then read the data out of the same file.
        self.relax_data_fns.read(ri_label='NOE', frq_label='600', frq=600e6, file='Ap4Aase.Noe.600.bz2', dir=__main__.install_path+sep+'test_suite'+sep+'shared_data'+sep+'relaxation_data', res_num_col=1, res_name_col=2, data_col=3, error_col=4)

        # Test the pipe data structures.
        self.assertEqual(cdp.frq, [600e6])
        self.assertEqual(cdp.frq_labels, ['600'])
        self.assertEqual(cdp.noe_r1_table, [None])
        self.assertEqual(cdp.num_frq, 1)
        self.assertEqual(cdp.num_ri, 1)
        self.assertEqual(cdp.remap_table, [0])
        self.assertEqual(cdp.ri_labels, ['NOE'])

        # Test the spin specific data.
        for i in xrange(len(cdp.mol[0].res)):
            # The spin container.
            spin = cdp.mol[0].res[i].spin[0]

            # No relaxation data.
            if self.Ap4Aase_600_NOE_val[i] == None or self.Ap4Aase_600_NOE_err[i] == None:
                # Auxillary data.
                self.failIf(hasattr(spin, 'frq'))
                self.failIf(hasattr(spin, 'frq_labels'))
                self.failIf(hasattr(spin, 'noe_r1_table'))
                self.failIf(hasattr(spin, 'num_frq'))
                self.failIf(hasattr(spin, 'num_ri'))
                self.failIf(hasattr(spin, 'remap_table'))
                self.failIf(hasattr(spin, 'ri_labels'))

                # Relaxation data.
                self.failIf(hasattr(spin, 'relax_data'))
                self.failIf(hasattr(spin, 'relax_error'))

            # Data exists
            else:
                # Auxillary data.
                self.assertEqual(spin.frq, [600e6])
                self.assertEqual(spin.frq_labels, ['600'])
                self.assertEqual(spin.noe_r1_table, [None])
                self.assertEqual(spin.num_frq, 1)
                self.assertEqual(spin.num_ri, 1)
                self.assertEqual(spin.remap_table, [0])
                self.assertEqual(spin.ri_labels, ['NOE'])

                # Relaxation data.
                self.assertEqual(spin.relax_data, [self.Ap4Aase_600_NOE_val[i]])
                self.assertEqual(spin.relax_error, [self.Ap4Aase_600_NOE_err[i]])
