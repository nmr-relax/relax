###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


class Skin:
    def __init__(self, relax):
        """The class accessible to the interpreter.

        The purpose of this class is to hide the variables and functions found within the namespace
        of the macro class, found below, except for those required for interactive use.  This is an
        abstraction layer designed to avoid user confusion as none of the macro class data
        structures are accessible.  For more flexibility use the macro class directly.
        """

        # Load the macro class into the namespace of this __init__ function.
        x = Macro_class(relax)

        # Place references to the interactive functions within the namespace of this skin class.
        self.set = x.set


class Macro_class:
    def __init__(self, relax):
        """Class containing the macro for selecting which model selection method should be used."""

        self.relax = relax


    def set(self, type=None):
        """Macro for selecting which model selection method should be used.

        !!!Remove references to model-free!!!

        The following types are supported:

        AIC:        Method of model-free analysis based on model selection using the Akaike
        Information Criteria.

        AICc:       Method of model-free analysis based on model selection using the Akaike
        Information Criteria corrected for finit sample size.

        BIC:        Method of model-free analysis based on model selection using the Schwartz
        Information Criteria.

        Bootstrap:  Modelfree analysis based on model selection using bootstrap methods to estimate
        the overall discrepancy.

        CV:         Modelfree analysis based on model selection using cross-validation methods to
        estimate the overall discrepancy.

        Expect:     Calculate the expected overall discrepancy (real model-free parameters must be
        known).

        Farrow:     The method given by Farrow et al., 1994.

        Palmer:     The method given by Mandel et al., 1995.

        Overall:    Calculate the realised overall discrepancy (real model-free parameters must be
        known).
        """

        if not type:
            print "No model selection method given."
            return

        self.relax.data.modsel = type
