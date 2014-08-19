###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""Short python script, to produce model information.  This script file could be extended to produce up-to-date Latex tables."""

# relax module imports.
from specific_analyses.relax_disp.variables import MODEL_LIST_FULL
from specific_analyses.relax_disp.model import models_info

# Get info for all models.
all_models_info = models_info(models=MODEL_LIST_FULL)

# Print the nested list for each model.
print("Printing the listed models for each model")
print("#########################################")
for model_info in all_models_info:
    print("%s"%model_info.model),
    print("<-"),
    nest_list = model_info.nest_list
    if nest_list == None:
        nest_list = ["None"]
    #print("%s"%model_info.nest_list)
    print(', '.join(map(str, nest_list)))
