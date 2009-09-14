# Random rotation matrix:
# [[ 0.33282568, -0.83581125,  0.43663098],
#  [-0.92326661, -0.19462612,  0.33120905],
#  [-0.19184846, -0.51336169, -0.83645319]]
# Euler angles:
# alpha: 5.0700283197712777
# beta: 2.5615753919522359
# gamma: 0.64895449611163691


# The error value.
error = 1.4741121114678945e-05

# Load tensor 0.
align_tensor.init(tensor='a 0', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='b 0', params=(-1.3288330878574132e-05, 0.00020354043164217626, -0.00046409902800134087, 0.0002493202418302213, -0.00077964218698160488), param_types=0)
align_tensor.init(tensor='a 0', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='b 0', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='a 0', domain='a')
align_tensor.set_domain(tensor='b 0', domain='b')

# Load tensor 1.
align_tensor.init(tensor='a 1', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='b 1', params=(-9.738292410013338e-05, -0.00038634774864149617, -0.00027912458757344276, -0.00038171766743202567, -0.00011588335825493787), param_types=0)
align_tensor.init(tensor='a 1', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='b 1', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='a 1', domain='a')
align_tensor.set_domain(tensor='b 1', domain='b')

# Load tensor 2.
align_tensor.init(tensor='a 2', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='b 2', params=(-0.00017932499024246612, -0.00033064833984871618, -0.00019167049464976276, -0.00018228662361670689, -0.00024786515322241842), param_types=0)
align_tensor.init(tensor='a 2', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='b 2', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='a 2', domain='a')
align_tensor.set_domain(tensor='b 2', domain='b')

# Load tensor 3.
align_tensor.init(tensor='a 3', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='b 3', params=(3.2029991098699158e-05, 0.0001030927713217096, -0.00040609134800855906, -0.00027871118513542376, 0.00018429705265751148), param_types=0)
align_tensor.init(tensor='a 3', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='b 3', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='a 3', domain='a')
align_tensor.set_domain(tensor='b 3', domain='b')

# Load tensor 4.
align_tensor.init(tensor='a 4', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='b 4', params=(0.00023041655343338213, -0.00028914097123516663, 8.5942868106736884e-05, 0.00057733961469646491, 0.00023383246814246303), param_types=0)
align_tensor.init(tensor='a 4', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='b 4', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='a 4', domain='a')
align_tensor.set_domain(tensor='b 4', domain='b')

# Load tensor 5.
align_tensor.init(tensor='a 5', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='b 5', params=(-0.00034205987160777676, -5.6563966889313711e-05, -0.00048729767346789097, -0.00020195965056872761, 0.00064352392049120096), param_types=0)
align_tensor.init(tensor='a 5', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='b 5', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='a 5', domain='a')
align_tensor.set_domain(tensor='b 5', domain='b')

# Load tensor 6.
align_tensor.init(tensor='a 6', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='b 6', params=(0.00020255575866227554, 0.00015766165657592193, -0.00022547338964377635, -0.00031137881231040781, 9.8269840241030186e-05), param_types=0)
align_tensor.init(tensor='a 6', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='b 6', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='a 6', domain='a')
align_tensor.set_domain(tensor='b 6', domain='b')

# Load tensor 7.
align_tensor.init(tensor='a 7', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='b 7', params=(0.00013226613079678079, -0.00028875805425577231, -0.00055280116463899331, -0.00079483102252618661, -0.00012673098706816532), param_types=0)
align_tensor.init(tensor='a 7', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='b 7', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='a 7', domain='a')
align_tensor.set_domain(tensor='b 7', domain='b')

# Load tensor 8.
align_tensor.init(tensor='a 8', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='b 8', params=(-0.00082779604132576475, -0.0001229250183977039, 0.00026827297822125086, -0.00076816617763492308, 1.787549543771558e-05), param_types=0)
align_tensor.init(tensor='a 8', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='b 8', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='a 8', domain='a')
align_tensor.set_domain(tensor='b 8', domain='b')

# Load tensor 9.
align_tensor.init(tensor='a 9', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='b 9', params=(-0.00019129846420341554, 0.00047556140822968502, -0.0001921404751338773, 0.00021386940177866865, -0.00026418197641736997), param_types=0)
align_tensor.init(tensor='a 9', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='b 9', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='a 9', domain='a')
align_tensor.set_domain(tensor='b 9', domain='b')
