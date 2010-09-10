# relax module imports.
from generic_fns.pipes import get_pipe
from physical_constants import dipolar_constant, g1H, g15N, NH_BOND_LENGTH_RDC

# Grid increments.
GRID_INCS = 3

# The dipolar constant.
d = dipolar_constant(g1H, g15N, NH_BOND_LENGTH_RDC)

# 1 Hz error.
error = 1.0 / d
print(error)

# Create the data pipe.
pipe.create(pipe_name='rigid - no rotation', pipe_type='frame order')

# Load the 'a' domain tensors.
align_tensor.init(tensor='a 0', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295086), param_types=0)
align_tensor.init(tensor='a 1', params=(-0.00014307694949297205, -0.00039671919293883545, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777639), param_types=0)
align_tensor.init(tensor='a 2', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477705, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='a 3', params=(0.00043690692358615301, -0.00034379559287467062, -0.0001935969517168339, 0.00030194133983804048, -6.3141622501644874e-05), param_types=0)
align_tensor.init(tensor='a 4', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='a 5', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736054, 0.00070350646902989675, 0.00037537667271407202), param_types=0)
align_tensor.init(tensor='a 6', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.0001718737155150645, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='a 7', params=(0.00017061308478202151, -0.00076455273118810512, -0.00052048809712606505, 0.00049258369866413403, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='a 8', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='a 9', params=(0.00037091020965736581, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397532e-05), param_types=0)

# Set the errors and domain.
for i in range(10):
    # Errors.
    align_tensor.init(tensor='a '+repr(i), params=(error, error, error, error, error), param_types=0, errors=True)

    # Domain.
    align_tensor.set_domain(tensor='a '+repr(i), domain='a')

# Load the 'b' domain tensors.
align_tensor.init(tensor='b 0', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295086), param_types=0)
align_tensor.init(tensor='b 1', params=(-0.00014307694949297205, -0.00039671919293883545, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777639), param_types=0)
align_tensor.init(tensor='b 2', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477705, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='b 3', params=(0.00043690692358615301, -0.00034379559287467062, -0.0001935969517168339, 0.00030194133983804048, -6.3141622501644874e-05), param_types=0)
align_tensor.init(tensor='b 4', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='b 5', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736054, 0.00070350646902989675, 0.00037537667271407202), param_types=0)
align_tensor.init(tensor='b 6', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.0001718737155150645, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='b 7', params=(0.00017061308478202151, -0.00076455273118810512, -0.00052048809712606505, 0.00049258369866413403, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='b 8', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='b 9', params=(0.00037091020965736581, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397532e-05), param_types=0)

# Set the errors and domain.
for i in range(10):
    # Errors.
    align_tensor.init(tensor='b '+repr(i), params=(error, error, error, error, error), param_types=0, errors=True)

    # Domain.
    align_tensor.set_domain(tensor='b '+repr(i), domain='b')

# The tensor reductions.
for i in range(10):
    align_tensor.reduction(full_tensor='a '+repr(i), red_tensor='b '+repr(i))

# Select the model.
frame_order.select_model('rigid')

# Set the reference domain.
frame_order.ref_domain('a')

# Optimise.
grid_search(inc=GRID_INCS, constraints=False)
minimise('simplex', constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(3)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', constraints=False)
monte_carlo.error_analysis()

# Print out.
print("\n# Min details #")
print(("grid increments: %s" % GRID_INCS))
print("\n# Euler angles (deg) #")
print(("ave_pos_alpha:      %20.8f+/-%-20.8f" % (cdp.ave_pos_alpha /2/pi*360, cdp.ave_pos_alpha_err /2/pi*360)))
print(("ave_pos_beta:       %20.8f+/-%-20.8f" % (cdp.ave_pos_beta /2/pi*360, cdp.ave_pos_beta_err /2/pi*360)))
print(("ave_pos_gamma:      %20.8f+/-%-20.8f" % (cdp.ave_pos_gamma /2/pi*360, cdp.ave_pos_gamma_err /2/pi*360)))

# Write the results.
results.write('devnull', dir=None, force=True)
