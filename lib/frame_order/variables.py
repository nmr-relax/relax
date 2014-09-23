###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
"""Variables for the frame order analysis."""


# The models.
MODEL_RIGID = 'rigid'
MODEL_ROTOR = 'rotor'
MODEL_FREE_ROTOR = 'free rotor'
MODEL_ISO_CONE_TORSIONLESS = 'iso cone, torsionless'
MODEL_ISO_CONE = 'iso cone'
MODEL_ISO_CONE_FREE_ROTOR = 'iso cone, free rotor'
MODEL_PSEUDO_ELLIPSE_TORSIONLESS = 'pseudo-ellipse, torsionless'
MODEL_PSEUDO_ELLIPSE = 'pseudo-ellipse'
MODEL_PSEUDO_ELLIPSE_FREE_ROTOR = 'pseudo-ellipse, free rotor'
MODEL_DOUBLE_ROTOR = 'double rotor'

# The model lists.
MODEL_LIST = [MODEL_RIGID, MODEL_ROTOR, MODEL_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS, MODEL_ISO_CONE, MODEL_ISO_CONE_FREE_ROTOR, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_FREE_ROTOR, MODEL_DOUBLE_ROTOR]
MODEL_LIST_SINGLE = [MODEL_RIGID, MODEL_ROTOR, MODEL_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS, MODEL_ISO_CONE, MODEL_ISO_CONE_FREE_ROTOR, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_FREE_ROTOR]
MODEL_LIST_DOUBLE = [MODEL_DOUBLE_ROTOR]
MODEL_LIST_NONREDUNDANT = [MODEL_RIGID, MODEL_ROTOR, MODEL_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS, MODEL_ISO_CONE, MODEL_ISO_CONE_FREE_ROTOR, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_PSEUDO_ELLIPSE, MODEL_DOUBLE_ROTOR]

# Model category lists.
MODEL_LIST_NO_TORSION = [MODEL_RIGID, MODEL_ISO_CONE_TORSIONLESS, MODEL_PSEUDO_ELLIPSE_TORSIONLESS]
MODEL_LIST_RESTRICTED_TORSION = [MODEL_ROTOR, MODEL_ISO_CONE, MODEL_PSEUDO_ELLIPSE]
MODEL_LIST_FREE_ROTORS = [MODEL_FREE_ROTOR, MODEL_ISO_CONE_FREE_ROTOR, MODEL_PSEUDO_ELLIPSE_FREE_ROTOR]

# Motion category lists.
MODEL_LIST_ISO_CONE = [MODEL_ISO_CONE, MODEL_ISO_CONE_TORSIONLESS, MODEL_ISO_CONE_FREE_ROTOR]
MODEL_LIST_PSEUDO_ELLIPSE = [MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_PSEUDO_ELLIPSE_FREE_ROTOR]
