###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""Script of testing out the pipe bundle concepts."""

# Create some data pipe with no bundle.
self._execute_uf(uf_name='pipe.create', pipe_name='test pipe 1', pipe_type='mf', bundle=None)
self._execute_uf(uf_name='pipe.create', pipe_name='test pipe 2', pipe_type='mf', bundle=None)
self._execute_uf(uf_name='pipe.create', pipe_name='test pipe 3', pipe_type='mf', bundle=None)

# Bundle the pipes.
self._execute_uf(uf_name='pipe.bundle', bundle='test bundle 1', pipe='test pipe 1')
self._execute_uf(uf_name='pipe.bundle', bundle='test bundle 1', pipe='test pipe 2')
self._execute_uf(uf_name='pipe.bundle', bundle='test bundle 1', pipe='test pipe 3')

# Create some data pipes in a new bundle.
self._execute_uf(uf_name='pipe.create', pipe_name='test pipe 4', pipe_type='mf', bundle='test bundle 2')
self._execute_uf(uf_name='pipe.create', pipe_name='test pipe 5', pipe_type='mf', bundle='test bundle 2')
self._execute_uf(uf_name='pipe.create', pipe_name='test pipe 6', pipe_type='mf', bundle=None)
self._execute_uf(uf_name='pipe.bundle', bundle='test bundle 2', pipe='test pipe 6')

# Create the third set to delete.
self._execute_uf(uf_name='pipe.create', pipe_name='test pipe 7', pipe_type='mf', bundle='test bundle 3')
self._execute_uf(uf_name='pipe.create', pipe_name='test pipe 8', pipe_type='mf', bundle='test bundle 3')
self._execute_uf(uf_name='pipe.delete', pipe_name='test pipe 7')
self._execute_uf(uf_name='pipe.delete', pipe_name='test pipe 8')

# Display everything.
self._execute_uf(uf_name='pipe.display')
