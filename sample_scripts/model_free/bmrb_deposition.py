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

"""Script for creating a NMR-STAR 3.1 formatted file for BMRB deposition of model-free results."""


# Create a data pipe to hold the final model-free results.
pipe.create(pipe_name='final_results', pipe_type='mf')

# Read the results.
results.read(file='results.bz2', dir='final')

# Set up the molecule information.
molecule.name(name='Ap4Aase')
molecule.type(type='protein')
bmrb.thiol_state(state='reduced')

# Temperature control and peak intensity type.
ri_ids = ['R1_600', 'R2_600', 'NOE_600', 'R1_800', 'R2_800', 'NOE_800']
for i in range(len(ri_ids)):
    relax_data.temp_calibration(ri_id=ri_ids[i], method='methanol')
    relax_data.temp_control(ri_id=ri_ids[i], method='single fid interleaving')
    relax_data.peak_intensity_type(ri_id=ri_ids[i], type='height')

# The software used for the analysis.
bmrb.software_select('NMRPipe')
bmrb.software_select('Sparky', version='3.106')
bmrb.software(name='X', url='http://www.nmr-relax.com', vendor_name='me', cite_ids=['dAuvergneGooley07'], tasks=['procrastinating', 'nothing much', 'wasting time'])

# All relevant citations.
bmrb.citation(cite_id='dAuvergneGooley07', authors=[["Edward", "d'Auvergne", "E.", "J."], ["Paul", "Gooley", "P.", "R."]], doi="10.1039/b702202f", pubmed_id="17579774", full_citation="d'Auvergne E. J., Gooley P. R. (2007). Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm. Mol. Biosyst., 3(7), 483-494.", title="Set theory formulation of the model-free problem and the diffusion seeded model-free paradigm.", status="published", type="journal", journal_abbrev="Mol. Biosyst.", journal_full="Molecular Biosystems", volume=3, issue=7, page_first=483, page_last=498, year=2007)

# Add the scripts used in the relaxation data and model-free analyses.
bmrb.script(file='noe.py', dir='relax_data', analysis_type='noe', engine='relax')
bmrb.script(file='relax_fit.py', dir='relax_data', analysis_type='relax_fit', engine='relax')
bmrb.script(file='dauvergne_protocol.py', dir='model_free', analysis_type='mf', model_selection='AIC', engine='relax', model_elim=True, universal_solution=True)

# Write out the BMRB NMR-STAR file.
bmrb.write(file='bmrb.star', dir=None, version='3.1', force=True)
