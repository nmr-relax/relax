"""Create a table of the total number of Sobol' points used in the PCS integration."""

# relax module imports.
from auto_analyses.frame_order import count_sobol_points

# The table.
count_sobol_points(file_name='sobol_point_count')
