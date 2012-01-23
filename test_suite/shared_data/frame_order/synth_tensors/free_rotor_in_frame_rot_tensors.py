# Rotation matrix:
# [[ 0.86008934 -0.19866933  0.46986895]
#  [ 0.17434874  0.98006658  0.09524715]
#  [-0.47942554  0.          0.87758256]]
# Euler angles:
# alpha: 0.0
# beta: 0.5
# gamma: 0.2


# Tensor name lists.
full_list = ['0 full', '1 full', '2 full', '3 full', '4 full', '5 full', '6 full', '7 full', '8 full', '9 full']
red_list = ['0 red', '1 red', '2 red', '3 red', '4 red', '5 red', '6 red', '7 red', '8 red', '9 red']

# Error.
error = 1.47411211147e-05





# Create the data pipe.
pipe.create(pipe_name='free_rotor', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(-9.6319199079196427e-08, -1.4580111158375752e-06, 1.4567616692517743e-07, 1.4092256277439981e-06, -8.7464302032954907e-08), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-9.1255795989384343e-05, -0.00026261389260042963, 3.6341923183820618e-05, 0.00033371749998808439, 6.7735880101299525e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-8.4738494188875437e-05, -0.00024396761858571668, 3.3659633345294488e-05, 0.00030999148589487877, 6.2818142403692741e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(1.5652620486094242e-05, 4.5301402945236319e-05, -6.0153035894654802e-06, -5.7664229852436992e-05, -1.1606228463560668e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(7.9832998445936949e-05, 0.00023006855349087162, -3.1969332912105278e-05, -0.00029271015608155031, -5.9247459644778087e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(2.3599750613565622e-05, 6.9458077821200179e-05, -9.3772702969190382e-06, -8.8363710940035745e-05, -1.7736470599834432e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(1.4987154109428642e-05, 4.2980328666109816e-05, -5.701444964766842e-06, -5.4618594323391321e-05, -1.0980993679370563e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.00010028889404075495, -0.00028896914068671041, 4.0234611700308897e-05, 0.0003672132349190442, 7.4616394354149005e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-0.00018993412614009479, -0.00054579630094145424, 7.541160605713853e-05, 0.00069436752580637976, 0.00014076514350235914), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(4.2082238858792765e-05, 0.00012084307529486883, -1.6685134893995578e-05, -0.00015370711561316016, -3.1440664639615748e-05), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])
