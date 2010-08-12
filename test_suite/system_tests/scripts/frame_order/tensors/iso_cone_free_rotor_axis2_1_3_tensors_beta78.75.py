# Rotation matrix:
# [[ 0.19509032 -0.          0.98078528]
#  [ 0.  1.  0.]
#  [-0.98078528  0.          0.19509032]]
# Euler angles:
# alpha: 0.0
# beta: 1.37444678595
# gamma: 0.0


# Tensor name lists.
full_list = ['0 full', '1 full', '2 full', '3 full', '4 full', '5 full', '6 full', '7 full', '8 full', '9 full']
red_list = ['0 red', '1 red', '2 red', '3 red', '4 red', '5 red', '6 red', '7 red', '8 red', '9 red']

# Error.
error = 1.47411211147e-05





# Create the data pipe.
pipe.create(pipe_name='cone_10.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(-0.00040448999843536413, 0.00022991438621179725, -0.00020861842591866483, 0.00028815161598076157, 8.6762078738789462e-05), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00037892689778071481, -0.00021578213028986904, 0.00019617729058758496, -0.00026965256551591372, -8.0771358908094315e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00026123727739574227, -0.00014886493071503991, 0.00013548786798795316, -0.00018595321986810759, -5.5723444110746586e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(0.00014648929770095183, -8.3481135154379058e-05, 7.5528823229628224e-05, -0.0001041781057469763, -3.0923028101754026e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00011378293809551907, 6.5026044097602208e-05, -5.8771848159850123e-05, 8.0361792341660218e-05, 2.4446641750867094e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00055129741499748133, -0.0003141435163491181, 0.0002849686255651539, -0.00039290788719831515, -0.00011732559004071875), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-3.8103971932408651e-06, 2.2504933874326989e-06, -2.3307146885164117e-06, 3.0245640234859198e-06, 1.0337191201265565e-06), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00039818471507894007, -0.00022665379871182441, 0.00020582038327074761, -0.00028293408609173784, -8.4644414976034937e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00073574456880284302, -0.00041927735860649261, 0.00038072453914969194, -0.00052345370219897594, -0.00015778407772064015), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00029449646634691448, 0.00016727550333978163, -0.0001521247757735895, 0.00020971915256145663, 6.3014395776592329e-05), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_20.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(-0.000376840673033265, 0.00021446009694652275, -0.00019482163685381951, 0.00026846831826782866, 8.1445850785562312e-05), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00035345370712250231, -0.00020119943089480676, 0.00018279563500397697, -0.00025160735863594033, -7.5169922471602941e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00024386309948179244, -0.00013879665137100428, 0.00012623769531726461, -0.00017348620284677937, -5.1719100923200323e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(0.00013625116506036167, -7.7677685343277933e-05, 7.0388155468603111e-05, -9.7332777083406719e-05, -2.8907144875406559e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00010602583694703559, 6.0972081167856485e-05, -5.4652280317376107e-05, 7.5216747815616986e-05, 2.2438741308797819e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00051361489533458828, -0.00029236654134965939, 0.0002660147729502945, -0.00036637197773888475, -0.00010967101318496312), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-3.8798726124858319e-06, 2.0477771483383751e-06, -2.3005263322761853e-06, 2.6102625802815648e-06, 8.8822154586048228e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00037113577888304831, -0.00021145328301311542, 0.0001915768087616592, -0.0002642710105044389, -7.8781519201843428e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00068624586430397847, -0.00039131762875547116, 0.00035516554771168087, -0.00048814404280193087, -0.00014674620938924881), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.000274605702181578, 0.00015607517955072196, -0.00014184858221902522, 0.00019549358666964728, 5.9032723131197893e-05), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_30.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(-0.00033396300979013143, 0.00019103571556309406, -0.00017285790828154115, 0.00023803055026956889, 7.2861847782560048e-05), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00031312568571107726, -0.00017804324787146187, 0.00016203439295438041, -0.00022328410599175907, -6.6471911266102583e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.0002159073325476954, -0.00012258451631060385, 0.00011183666244822155, -0.00015395471303226424, -4.5641578869982505e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(0.00012099841440863181, -6.8923058088219162e-05, 6.2455107826089526e-05, -8.648810465535379e-05, -2.5468163875577734e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-9.4094844151869714e-05, 5.4360387856145036e-05, -4.8707284868631972e-05, 6.6964495519338741e-05, 1.9230962847863485e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00045526204245163591, -0.00025920871892186955, 0.00023573706264735773, -0.00032515513550394502, -9.7288877865318139e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-3.1328070651174703e-06, 1.5557128604871996e-06, -1.8943893756044729e-06, 2.2125090978067682e-06, 9.1196406862666283e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00032909671351951807, -0.00018732211011989196, 0.0001699840398208462, -0.00023464229912610127, -6.9463287620844563e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00060782667864438472, -0.00034734816633132733, 0.00031508021707007667, -0.00043323909420769436, -0.0001295740815647452), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00024326771888408827, 0.00013857104409978596, -0.00012578288499173057, 0.00017329240942558173, 5.2800264319813435e-05), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_40.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(-0.00027957030241172585, 0.00015909664027981285, -0.00014493804445315993, 0.00019933582995364536, 5.9860738458718578e-05), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00026228572489509449, -0.00014912727129215984, 0.00013612177708625036, -0.00018639432174421384, -5.623242756026001e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00018069100462031582, -0.00010274933332203665, 9.397565601829613e-05, -0.00012854610665525627, -3.8761687787001076e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(0.00010185376398914776, -5.7784510202368893e-05, 5.2317416162852491e-05, -7.1973244995838229e-05, -2.175204530364511e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-7.9124765753981814e-05, 4.4999346625168551e-05, -4.0684164434040012e-05, 5.5856361167563638e-05, 1.6826832212804818e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00038170964818810149, -0.0002168719446897316, 0.00019749865257958309, -0.00027158519148104182, -8.1664757956571784e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-2.1421773368902117e-06, 1.2915461932948202e-06, -1.6014865828680801e-06, 2.1066615499034998e-06, 5.1145326579541294e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00027616150251999152, -0.00015694934565410314, 0.00014284819221593598, -0.00019556029595934417, -5.9167681964807594e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00050880063894743089, -0.00028947664279851731, 0.00026404741601784105, -0.00036243555478684806, -0.00010886778295939109), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00020354615635516824, 0.00011584034085731975, -0.00010578149819048565, 0.0001449280590112333, 4.369453489735699e-05), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_50.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(-0.00021782411238786869, 0.00012445453899480747, -0.00011279046331879585, 0.00015562110305202722, 4.6388898043256238e-05), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00020458237909890147, -0.00011627367879862086, 0.00010615867749843566, -0.00014548517016077468, -4.4273889194188164e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00014098726296138753, -8.0152063289066832e-05, 7.338350688901645e-05, -0.00010039982579710034, -3.0611685281345079e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(7.9395243154769223e-05, -4.4764555584638795e-05, 4.0573238512739852e-05, -5.6035555960948239e-05, -1.7020118364283611e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-6.1623448110303844e-05, 3.4719134142139444e-05, -3.1663736193916299e-05, 4.3423898736349509e-05, 1.3068434951776047e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00029761597713941494, -0.00016898292124632703, 0.00015360392920431848, -0.00021200225514170405, -6.3747978944717239e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-1.7299386416977875e-06, 1.2792203198525451e-06, -1.4087571523542683e-06, 1.8411461569574329e-06, 4.3089103363719626e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00021535739905869831, -0.00012207013217151554, 0.00011127896112355725, -0.00015241793782610943, -4.6626667720789166e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00039664538623854944, -0.00022579304269469458, 0.0002058484516214034, -0.00028297219683584064, -8.4911108150438597e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00015868986684412122, 9.067295761124547e-05, -8.2483676625957469e-05, 0.00011315324473493955, 3.4225476977825446e-05), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_60.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(-0.00015521471335057949, 8.8554764892827346e-05, -8.0326021419659764e-05, 0.00011001512106558958, 3.2897239761457846e-05), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00014524156863952081, -8.262453669099392e-05, 7.5550325749805609e-05, -0.00010329944521458888, -3.1367973686099663e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(9.9985695900641175e-05, -5.6860661203058066e-05, 5.2144462285152854e-05, -7.135278313106983e-05, -2.1694453236889615e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(5.6442401906931698e-05, -3.1993335472271155e-05, 2.9036701675696819e-05, -3.9663450078289067e-05, -1.2105228735202137e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-4.380880166932377e-05, 2.4723007926979894e-05, -2.2727038648423957e-05, 3.0861152740593287e-05, 9.2375023850264153e-06), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.0002115358397411897, -0.00012022704776991976, 0.00010936871890012322, -0.00014998809809837427, -4.5376756046084266e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-1.1343632059482355e-06, 7.0782993682877344e-07, -7.9632487325651082e-07, 1.3136141608278452e-06, 3.333695886000597e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00015295491897520069, -8.6945884169805447e-05, 7.941616783986855e-05, -0.00010828408393103784, -3.2980908400752561e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00028192626574085038, -0.00016029523883795326, 0.00014650079938991782, -0.00020056537393858625, -6.0240874289604437e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00011290688878585491, 6.4480184966218061e-05, -5.8689113560786263e-05, 8.0233011412907161e-05, 2.4197561570252843e-05), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_70.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(-9.5427234386953713e-05, 5.4214762537680656e-05, -4.8777473666497502e-05, 6.7358304823754862e-05, 2.0121335641135374e-05), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(8.8526550946495212e-05, -5.022303980398801e-05, 4.6293590228725356e-05, -6.306434826911265e-05, -1.9291492783811358e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(6.0788814762866009e-05, -3.4413436232635895e-05, 3.1914960871786339e-05, -4.3508396119113494e-05, -1.3387445034090843e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(3.4569507075799529e-05, -1.9672642490712373e-05, 1.7992867943147397e-05, -2.4290969952184478e-05, -7.4137575126617056e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-2.6573606866824725e-05, 1.5029023491646064e-05, -1.4095248459476317e-05, 1.8630435938382519e-05, 5.6098896464721558e-06), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00012952743420047817, -7.3370720529718122e-05, 6.6898721342771263e-05, -9.1789811831508361e-05, -2.7960463076403615e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-5.919358499590066e-07, 1.9055633811714596e-07, -2.4156162416294321e-07, 7.6884075311564199e-07, 2.9161551832544155e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(9.3251775416895602e-05, -5.3071520786810954e-05, 4.8957713603639991e-05, -6.6111726425366763e-05, -2.0184679846603348e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00017208913777619993, -9.7328726126202461e-05, 8.9334176196477814e-05, -0.00012222158450768078, -3.7029069591183443e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-6.9170226912936754e-05, 3.9379205472841585e-05, -3.5739191520292123e-05, 4.9113949723512448e-05, 1.480748033201772e-05), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_80.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(-4.2200141872748869e-05, 2.4165650429831078e-05, -2.1683202821521157e-05, 2.9653115070042805e-05, 9.1152794772041694e-06), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(3.9257006506452272e-05, -2.2508029955017699e-05, 2.0494329849610113e-05, -2.7749703234465426e-05, -8.6677369267234724e-06), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(2.6886695606396966e-05, -1.53946153831794e-05, 1.4139338370557401e-05, -1.9105534892490473e-05, -5.9978928606282585e-06), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(1.5382619455098222e-05, -8.7581870500242426e-06, 7.9627343934013104e-06, -1.0801405064904332e-05, -3.3038181962325393e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-1.1724925404672994e-05, 6.8415246382312581e-06, -6.315325197473207e-06, 7.9653523133324512e-06, 2.4016493224453051e-06), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(5.7118881110301167e-05, -3.238415370501987e-05, 2.9734280575502383e-05, -4.0608303002663882e-05, -1.2507084380510665e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-6.8708054919754332e-08, -3.982972123966483e-08, -1.4694883229127078e-07, 2.8712563739097586e-07, 1.3106533722101659e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(4.1599385013669871e-05, -2.3978773499672055e-05, 2.1616870006777322e-05, -2.9118940564250591e-05, -9.0708281760521706e-06), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(7.5747134993311334e-05, -4.3381131393530018e-05, 3.9816212313393367e-05, -5.3384324139660522e-05, -1.647900145528176e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-3.0785680338749168e-05, 1.7726928878549896e-05, -1.5793058786671446e-05, 2.1653962809152867e-05, 6.7631018219675363e-06), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_90.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(-3.584055417842233e-07, 4.4072215625989361e-07, 1.1205010229029206e-07, -3.0827448115035046e-07, -6.574441630036864e-08), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-7.1836901648381614e-08, -2.003372983688717e-07, 2.2720266126671748e-07, 3.1752823664621702e-07, -2.8030583847318679e-07), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-2.990377494384207e-07, 4.1980263906518063e-08, 1.8337390512297003e-07, 2.0679654883068616e-07, -2.4039538991336908e-07), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(2.7037848124277718e-07, -2.5646042583026362e-07, 1.3748335961931758e-07, 1.4016581158905322e-07, -8.633902821237698e-08), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-1.1636343314442968e-07, 1.7555722638755443e-07, -2.0651467206931442e-07, -3.1293725450686519e-07, -3.2245457466273637e-09), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-1.2365439936440379e-07, -7.1830960552232676e-08, 2.0187109255257146e-07, 3.4756631943308506e-07, -2.3429397384792667e-07), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(4.8875886891419997e-07, -3.7954843217304646e-07, 6.1897359335599807e-08, 6.9996604621929237e-08, 2.0042691173676572e-08), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(4.5138436733777421e-07, -6.4683631348239575e-07, 3.3357439173955827e-07, 4.3035255908485359e-07, -3.0128268200938274e-07), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-4.9279981631081486e-07, -9.6775187762569827e-09, 3.1391178948746303e-07, 7.9381609881801305e-07, -1.7884943950936236e-07), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-2.6700181658739122e-07, 4.0813926544664601e-07, 2.4789537667025301e-08, -1.9687320166440426e-07, 9.7148748057532242e-08), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_100.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(2.9434782181510354e-05, -1.6690846469511439e-05, 1.5363659631632094e-05, -2.1519361943831194e-05, -6.3808739022158153e-06), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-2.7846845039999598e-05, 1.5216853124405557e-05, -1.4152655759882242e-05, 2.027479203363873e-05, 5.6311817548540066e-06), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-1.9371097261118228e-05, 1.0498548778004569e-05, -9.7169503583346441e-06, 1.3961884108296837e-05, 3.9425575735659234e-06), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-1.0551030199581122e-05, 5.9991321589661959e-06, -5.518302262856635e-06, 7.8505512077346914e-06, 1.9748318503405499e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(8.1217338166733119e-06, -4.1463071484080731e-06, 3.9868117548307087e-06, -6.3393355418345473e-06, -1.6160734820943661e-06), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-4.0563165640529692e-05, 2.3138710472902292e-05, -2.0873445133230716e-05, 2.9239966669629237e-05, 8.3244018192736181e-06), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(6.4510866486534152e-07, -3.7637919830878781e-07, 1.6596302474156442e-07, -8.8343048782359693e-08, -3.2298036620078292e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-2.8860925850301937e-05, 1.5622615767435855e-05, -1.4805303731649194e-05, 2.146604760745395e-05, 5.6022345933482914e-06), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-5.4144334065626746e-05, 2.97502789820516e-05, -2.7319055814356921e-05, 3.9437682699445074e-05, 1.1512768195137545e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(2.146494766393649e-05, -1.186663203253355e-05, 1.115360588485924e-05, -1.5698813558216645e-05, -4.5089909254081178e-06), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_110.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(4.6207706449223515e-05, -2.6570592667940737e-05, 2.3995617970759888e-05, -3.3045688916509722e-05, -9.7577661727296999e-06), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-4.3614448904250651e-05, 2.4339768950464465e-05, -2.2312948125893584e-05, 3.1630053267840761e-05, 8.772672382338553e-06), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-3.0263610824939123e-05, 1.6804008334939655e-05, -1.5306746242857854e-05, 2.1874988673448209e-05, 6.1717865122777634e-06), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-1.6635057149805788e-05, 9.461303827455951e-06, -8.8589539787670594e-06, 1.2199829260601413e-05, 3.1031190936437066e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(1.2807306405774233e-05, -6.7144278221707474e-06, 6.7474358949997326e-06, -9.7848983522223708e-06, -2.433766870721023e-06), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-6.3540295808948603e-05, 3.6507629428163881e-05, -3.2928295899191468e-05, 4.5448232469927608e-05, 1.3039735888233234e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(8.4705521162273254e-07, -5.7601911755608662e-07, 8.9959700999530684e-08, -2.2058930217503809e-07, -5.3354557412635148e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-4.5379130403335984e-05, 2.5074643167274973e-05, -2.3541421224482957e-05, 3.3426697115588577e-05, 8.6898432489108302e-06), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-8.4729231993848375e-05, 4.7479425900657349e-05, -4.3387057593484963e-05, 6.1149554241405436e-05, 1.776290185836257e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(3.3682508402163759e-05, -1.9048929104078956e-05, 1.7302440742227746e-05, -2.4266777340868359e-05, -6.9220542420699378e-06), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_120.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(5.121445995542075e-05, -2.9336689155301536e-05, 2.692754469243886e-05, -3.675032765483056e-05, -1.102354959114522e-05), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-4.8307777211059403e-05, 2.7203540926631982e-05, -2.4934069683966617e-05, 3.488717892281851e-05, 9.8744400390449028e-06), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-3.3516026540070328e-05, 1.8820336383492973e-05, -1.7024089249290421e-05, 2.4092746977456898e-05, 6.9414171968029223e-06), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-1.8455069059799473e-05, 1.0523307269728198e-05, -1.0020914096852667e-05, 1.3504603257602019e-05, 3.4364902073109024e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(1.4282450096055336e-05, -7.7126497841868282e-06, 7.5735966512488952e-06, -1.0715068110352558e-05, -2.7114613560837082e-06), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-7.0450321894912626e-05, 4.0410405118207455e-05, -3.683872880275262e-05, 5.0432404079815114e-05, 1.4530984194614822e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(9.2316140321366774e-07, -5.9541967570801807e-07, -6.3671783153526028e-08, -2.635082760560513e-07, -6.03272295810133e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-5.0272120074150244e-05, 2.8131558826928778e-05, -2.6479579380090418e-05, 3.6806042580041137e-05, 9.7921032577046925e-06), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-9.4013042583927618e-05, 5.3010510756817979e-05, -4.8336467292707024e-05, 6.760680762406195e-05, 1.9942828129863173e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(3.7266853644791782e-05, -2.114119925144225e-05, 1.9413449749454925e-05, -2.6864294602737773e-05, -7.8741738534902261e-06), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_130.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(4.7157129326543265e-05, -2.7038263585741813e-05, 2.4834014380983403e-05, -3.3807669759496449e-05, -1.0492867929428066e-05), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-4.420148888256247e-05, 2.4770037548932251e-05, -2.3108739032276273e-05, 3.2079505601780362e-05, 9.0239776365689606e-06), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-3.0619244674438302e-05, 1.7038701952427806e-05, -1.5745825263272219e-05, 2.2190759393572445e-05, 6.3222162177523254e-06), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-1.6967986407836531e-05, 9.7578266851432054e-06, -9.3320804439415232e-06, 1.2233993820241816e-05, 3.0253098157430785e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(1.3031386409287442e-05, -7.0213543364834108e-06, 7.0757401653830899e-06, -9.7116494825924928e-06, -2.5821789876909757e-06), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-6.4777097075389116e-05, 3.7145731421410063e-05, -3.3957950478878749e-05, 4.6080992375584905e-05, 1.3230910146855274e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(8.2579150453788137e-07, -4.067792765010596e-07, -1.8147266633987867e-07, -3.5618931501406172e-07, -6.0798863429733514e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-4.5978485519121698e-05, 2.5718122974322958e-05, -2.4698186709764308e-05, 3.3747316285253495e-05, 8.8835915308619834e-06), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-8.61795844397379e-05, 4.8312301152972738e-05, -4.4565770116510613e-05, 6.2073163662929278e-05, 1.8721048855849493e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(3.4184023960809021e-05, -1.9355122760037189e-05, 1.7990948842202487e-05, -2.4837566173060891e-05, -7.3963206948946435e-06), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_140.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(3.6514041052553016e-05, -2.0867947354847688e-05, 1.9146533051581952e-05, -2.6506377841659826e-05, -8.4027810585605308e-06), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-3.4406850400647235e-05, 1.9130039929581859e-05, -1.808417097737001e-05, 2.5263094555453957e-05, 7.1498956905375103e-06), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-2.3834565805258754e-05, 1.3146769283814114e-05, -1.2319329049180547e-05, 1.7491732361962713e-05, 5.0132601605732577e-06), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-1.3272321270139712e-05, 7.6948310171481221e-06, -7.4045853156191832e-06, 9.6214217036340723e-06, 2.357462222711956e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(1.026672843018228e-05, -5.2422622233946297e-06, 5.548987430319384e-06, -7.7303487219618842e-06, -2.0338279314713795e-06), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-5.0372744077241409e-05, 2.9140948285336467e-05, -2.6554909030896259e-05, 3.6185635301347316e-05, 1.0484310211147456e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(5.6609776520186067e-07, -3.1133458740381082e-07, -2.3630990758875885e-07, -2.7056363624473706e-07, -5.1973250582646512e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-3.5886136487352624e-05, 1.9814814066123028e-05, -1.9440315440794047e-05, 2.6602668593946294e-05, 6.9946277807881001e-06), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-6.7023456496880253e-05, 3.711964165781886e-05, -3.4561620917905555e-05, 4.8903847403734093e-05, 1.4930609606622883e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(2.6483706236696721e-05, -1.4863220805605174e-05, 1.3938978396172313e-05, -1.9495834008438159e-05, -5.9065020709987156e-06), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_150.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(2.3588627067513012e-05, -1.3619994696722308e-05, 1.234939762518536e-05, -1.7254120598206325e-05, -5.7323374297245836e-06), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-2.2137406675704215e-05, 1.2183502149175611e-05, -1.1872375936549385e-05, 1.648079976197436e-05, 4.7417416365980024e-06), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-1.5302494015246188e-05, 8.3312857509616284e-06, -8.0548394430336183e-06, 1.1416044766096431e-05, 3.3635965514583382e-06), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-8.6866416377444769e-06, 5.0493570469721572e-06, -4.9598160535553064e-06, 6.2094917848718615e-06, 1.3781020289986744e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(6.6987905833075386e-06, -3.31238670077465e-06, 3.7409524908381036e-06, -5.1402556772664577e-06, -1.3021297136843894e-06), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-3.274807275523425e-05, 1.9140671232627843e-05, -1.7289019662640057e-05, 2.3360662408713449e-05, 6.7889261131154138e-06), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(3.0117600044546908e-07, -2.0365262267910314e-07, -3.1532615422208704e-07, -1.6072440047234882e-07, -4.9157503523530538e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-2.3121927085712013e-05, 1.2544183147091863e-05, -1.2959993487074382e-05, 1.7400417231484299e-05, 4.4908032582063855e-06), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-4.3300961027399501e-05, 2.3939475691108017e-05, -2.241167572874135e-05, 3.1950764255922217e-05, 1.0130383217014727e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(1.6959501371205855e-05, -9.4710561143283207e-06, 9.0726244718443899e-06, -1.2742959863107397e-05, -4.0459805697341785e-06), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_160.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(1.1471166479457785e-05, -6.7822516557464613e-06, 5.9357400409865327e-06, -8.6117725834607779e-06, -3.0162229230057398e-06), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-1.0440843742946848e-05, 5.5855067515505839e-06, -5.8955264790702704e-06, 8.3522866446851513e-06, 2.4523459019739843e-06), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-7.207987811575892e-06, 3.7747502228432974e-06, -3.9854143123998599e-06, 5.7669070954019e-06, 1.8061900247726613e-06), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-4.1730833375365919e-06, 2.497352893503673e-06, -2.53421334706829e-06, 3.1409046887120709e-06, 5.4041579340761486e-07), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(3.0777264651820138e-06, -1.3664230224590531e-06, 1.8541750683039956e-06, -2.7674085924015989e-06, -6.005746284028297e-07), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-1.6016543822742762e-05, 9.7022519824653717e-06, -8.5148279520583453e-06, 1.1529591917555521e-05, 3.4275869571531809e-06), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(2.3820481815513065e-07, -1.7481184222355828e-07, -2.4916802399551817e-07, 2.9518761669818108e-08, -4.39700188688785e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-1.0730242512402918e-05, 5.5486319066797948e-06, -6.548870385987126e-06, 8.9782201281807687e-06, 2.1261791701656556e-06), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-2.0793458354307761e-05, 1.1406619804447968e-05, -1.0835050477759017e-05, 1.6112041349436629e-05, 5.4468884749949721e-06), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(8.0162769125260438e-06, -4.3838214916865359e-06, 4.440274619503617e-06, -6.4466097795694893e-06, -2.1332457069616532e-06), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_170.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(2.7911771270814098e-06, -1.9187185740122885e-06, 1.540144710551895e-06, -2.3500846027941756e-06, -1.2895503280720149e-06), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-2.3844838190697922e-06, 1.0168669225081351e-06, -1.6971084835176053e-06, 2.6016658777314792e-06, 7.7240663305978521e-07), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-1.6608029225065961e-06, 6.4116757069379091e-07, -1.1061491243179899e-06, 1.8156484393366656e-06, 6.390808721895319e-07), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-1.0950807147963226e-06, 6.7385444415350031e-07, -8.5154425981359733e-07, 9.3972756069993604e-07, -1.116045462066678e-07), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(6.8822876571007787e-07, -5.521805638813603e-08, 5.4012104292326222e-07, -1.0266951729133164e-06, -1.5480073398720355e-07), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-4.3475731796218712e-06, 2.9641791453309277e-06, -2.4171258887136545e-06, 3.1736826493042655e-06, 9.7994641353574182e-07), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(1.4551924503327935e-07, -1.6117790640978979e-07, -2.2104254560347947e-07, 8.9946424333961486e-08, -4.119088650701383e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-2.2742250822668564e-06, 7.228806539051246e-07, -2.0560628035581083e-06, 2.9398272608903926e-06, 3.7257982970883421e-07), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-5.1435301709701805e-06, 2.6730543773257408e-06, -2.7700937895890718e-06, 4.8499849071911886e-06, 2.2982087991875362e-06), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(1.6823221715605927e-06, -8.3837667888842542e-07, 1.2274427211917163e-06, -1.9092811509979057e-06, -8.4589499589333238e-07), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])




# Create the data pipe.
pipe.create(pipe_name='cone_180.0_deg', pipe_type='frame order')

# Load tensor 0.
align_tensor.init(tensor='0 full', params=(0.00014221982216882766, -0.00014454300156652134, -0.00070779621164871397, -0.00060161949408277324, 0.00020200800707295083), param_types=0)
align_tensor.init(tensor='0 red', params=(-3.6193143049957629e-07, -1.2364511559434247e-07, -7.2569462709506853e-08, -1.1059429590466985e-07, -6.0731679991732212e-07), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(4.8307140359097214e-07, -6.1536391100192014e-07, -1.972353551540971e-07, 5.6080062130170956e-07, 1.1380379233439697e-07), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(2.9669886931242173e-07, -4.702433468058182e-07, -7.2694272316509143e-08, 4.0594620496465374e-07, 1.8513162542261381e-07), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(3.9331842069610935e-08, 2.632449132044197e-08, -2.6597408781499673e-07, 1.6563865455694423e-07, -3.5925446873608508e-07), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-1.5244590109098534e-07, 3.6071857219741667e-07, 9.6676904313713523e-08, -4.598319201794203e-07, 8.9975557008302e-08), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-9.757934276265887e-08, 5.3427047756007488e-07, -2.0630798203008977e-07, 1.5539712873486724e-07, 8.0195295666558704e-08), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(1.3208411641623229e-07, -1.5012398793975577e-07, -2.3943752557469333e-07, 1.4256359116892778e-07, -4.1945049191062849e-07), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(7.4506660321059013e-07, -9.8970959023968902e-07, -4.8700186168721332e-07, 8.377766117346499e-07, -3.4247006991209853e-07), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(4.3846633561057044e-07, -4.1323931644339286e-07, 1.503528428651337e-07, 8.5881227950739858e-07, 9.9466585550403828e-07), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-5.8543363575056137e-07, 4.7370461670207181e-07, 6.2624916535254618e-08, -2.9375454629879852e-07, -3.4213318467975671e-07), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])
