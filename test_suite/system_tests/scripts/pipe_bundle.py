# Script of testing out the pipe bundle concepts.

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
