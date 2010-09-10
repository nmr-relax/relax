from math import acos, atan2
from numpy import array, float64
from numpy.linalg import norm

# Create a data pipe.
pipe.create('mapping test', 'frame order')

# Tensor name lists.
full_list = ['0 full', '1 full', '2 full', '3 full', '4 full', '5 full', '6 full', '7 full', '8 full', '9 full']
red_list = ['0 red', '1 red', '2 red', '3 red', '4 red', '5 red', '6 red', '7 red', '8 red', '9 red']

# Error.
error = 1.47411211147e-05

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(-0.00011836046893869115, 4.9498248427100159e-05, 0.00022159831770147845, 0.00020686032111030312, -0.00014457684371200341), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00011073308524437112, -4.4908472564489152e-05, -0.00020840952358029579, -0.00019367496447130476, 0.00013375699704776413), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(7.630988785196044e-05, -3.0574715776622166e-05, -0.00014400791235828983, -0.0001334408398573033, 9.2148652459171122e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(4.2495561808229555e-05, -1.7906536047563611e-05, -8.0120582739316314e-05, -7.5236323367401401e-05, 5.1448157890645449e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-3.3582069426662544e-05, 1.4153435527285773e-05, 6.2770118279639972e-05, 5.7554234327991369e-05, -3.9371819354409813e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00016006323213470073, -6.6354800338631775e-05, -0.00030263172118385909, -0.00028275128737240135, 0.00019562910358850546), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-1.0290161178095163e-06, -1.0740699191825727e-07, 2.585758891502495e-06, 1.8893164051028607e-06, -1.8539717316651138e-06), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.0001165645504013804, -4.7668554763300502e-05, -0.00021855196591591533, -0.00020346516952570335, 0.00013983261485280346), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00021523501993235588, -8.8473909338291167e-05, -0.00040513799931943815, -0.00037529600509393239, 0.00026060767644550816), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-8.6383945323905177e-05, 3.5327511625355711e-05, 0.00016146557018549071, 0.00015052498960728088, -0.00010484022540546174), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])

# Select the Frame Order model.
frame_order.select_model(model='iso cone, free rotor')

# Set the reference domain.
frame_order.ref_domain('full')

# Set the exact cone axis.
axis = array([2, 1, 3], float64)
axis = axis / norm(axis)
cdp.axis_theta = acos(axis[2])
cdp.axis_phi = atan2(axis[1], axis[0])
cdp.cone_theta = 40.0 / 360.0 * 2 * pi

# Map the Euler angle space.
dx.map(['ave_pos_alpha', 'ave_pos_beta', 'ave_pos_gamma'], lower=[0, 0, 0], upper=[2*pi, 2*pi, 2*pi], inc=3, file_prefix='devnull', point_file='devnull')
