# Rotation matrix:
# [[-0.54462264 -0.83474246 -0.08118622]
#  [-0.83203088  0.52560021  0.17739513]
#  [-0.10540775  0.16416285 -0.98078528]]
# Euler angles:
# alpha: 0.0
# beta: 2.94524311274
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
align_tensor.init(tensor='0 red', params=(-0.00066562099261778594, 0.00058422606984534834, -7.6750931537371771e-05, -2.7351592712263353e-05, -0.0002560548567647965), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-0.00047747600454968767, 0.00012797226549932778, -0.00010973560179854438, 0.00034812936764253054, 6.1366146576969564e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00041465856245328977, 0.0001221410873670269, -0.00014644397075319469, 0.00028688086069155816, -4.8117543632028459e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-0.0002218612480582255, 0.00022722339855973798, 0.00016735584157545434, 0.00019749532669375785, 0.00015561184864573113), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00044102632453502398, -0.00012165794741553538, -0.00032046757083614355, 5.0951531785485934e-05, 0.00011033518349713829), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(7.8570699845995e-05, 0.00010907943736135903, 0.00018410867077634429, 0.0006296448763525559, 0.00024571253483647538), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-0.00019128082463949891, 0.00014561582598510947, 0.00016726534543814244, -3.8337591630714393e-05, 0.0001372873775354124), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.00083128616692695651, 0.00032218748985933429, 3.1828829181664086e-05, 0.00032042801233110255, 0.0001916408844924408), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-0.00019567435572742618, -0.00030880351638442157, 0.00026383735157734509, 0.00031451998113219055, -0.00016928561134220278), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00011926708088364071, 0.00028658799619885847, 0.00019099956753972376, -8.6136019394129914e-05, -0.00019225435931751771), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.00065632999432191396, 0.00057823012290253765, -7.6372609218040009e-05, -2.4593113661859577e-05, -0.00025948273528672881), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-0.0004596903024770083, 0.00012210953799266921, -0.00010717245713173162, 0.00033599398043982924, 5.0577197670210062e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00040225874033172893, 0.00011891495364440236, -0.000144243541354642, 0.00027969015549714877, -5.5342005980908944e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-0.00021214748164646161, 0.00021770957250462694, 0.00016285389785652409, 0.0001833900749365862, 0.00014831122711310253), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00043152730056252275, -0.00011805199089575861, -0.0003180119156196427, 5.5501284071095947e-05, 0.00011169028834245875), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(8.2399268184127475e-05, 9.6756445746826853e-05, 0.0001714233610506466, 0.00060114170852306186, 0.00023700785707097074), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-0.00018262955555221463, 0.00013980883756278199, 0.00016668645883615208, -4.4148596908891603e-05, 0.00013271594694011697), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.00079987051014534692, 0.00030968454180691515, 3.5657602212949132e-05, 0.00030206826382286249, 0.00017412752471861396), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-0.0001912696320441639, -0.00030692315991575958, 0.00025889715131040617, 0.00030294615354966052, -0.00016890293308706938), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00012469910212398489, 0.00028354780211348592, 0.000184144205357422, -8.5070571234166641e-05, -0.00018818996469704537), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.00064177696841674473, 0.00056849095805564204, -7.4813058232541134e-05, -1.9507362258606916e-05, -0.00026275440815817308), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-0.00043105336912022758, 0.0001136914164556466, -0.0001031300351193531, 0.00031743862718729095, 3.292694654528235e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00038230930790892942, 0.00011494848650462132, -0.00014081962154764466, 0.00026861096306257084, -6.6722272873087179e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-0.00019609252028698391, 0.00020150553876426745, 0.00015593862420894039, 0.00016185606116942577, 0.00013610880349634738), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00041578298869744988, -0.00011250435582899464, -0.00031412752677677903, 6.1160660382797942e-05, 0.00011426837670729185), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(9.0009592227983937e-05, 7.6305103253823632e-05, 0.0001507069643587054, 0.00055587559813311275, 0.00022196884691210613), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-0.00016871794340369141, 0.00012949918759601195, 0.00016617162146210449, -5.2360513041524615e-05, 0.00012483088136319825), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.00074946079319298186, 0.00028983360911229535, 4.2228778696321985e-05, 0.00027495278714158625, 0.00014516697524707143), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-0.00018285044561260175, -0.00030147435214600228, 0.000249681620060197, 0.00028526663572156361, -0.00016972690955704652), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00013300853750970544, 0.00027795620697265098, 0.00017354479806807457, -8.3143587428991287e-05, -0.00018050877839080354), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.00062235085014052246, 0.00055481752748385801, -7.3032618510594292e-05, -1.2841062145608602e-05, -0.00026677072629392322), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-0.00039447863811175232, 0.0001032965788315144, -9.8205598923379627e-05, 0.00029308480784305546, 1.0577766978665234e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00035679812777507488, 0.00011013302566395597, -0.00013656906454034899, 0.00025393607057614477, -8.0991212610229238e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-0.00017558280027260247, 0.00018064162974017499, 0.00014678424525892779, 0.00013419199641423346, 0.00012043706221456169), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00039520414511985008, -0.00010561002835665119, -0.0003085884150902309, 6.8722868752834249e-05, 0.00011717008241275047), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(9.8874130609686439e-05, 5.0688669776816481e-05, 0.00012409123252835362, 0.00049760013491187156, 0.00020276630972718924), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-0.00015069857459847725, 0.00011607703793911326, 0.00016519626766366702, -6.2848940492983031e-05, 0.0001146062207747647), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.00068468437672879038, 0.00026456292819949169, 4.9980428205222778e-05, 0.00023955830093669967, 0.00010826040990231592), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-0.00017247008229610494, -0.00029276724129087545, 0.00023750260352954254, 0.00026163451090222565, -0.00016989992100069899), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00014329506175843774, 0.00027013846037894006, 0.00015986173084495556, -8.0367819483983125e-05, -0.00017055495801594536), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.00059886142700303776, 0.00053819983103041652, -7.1104630838667764e-05, -4.7783247159471078e-06, -0.00027128690377340901), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-0.0003522523221965817, 9.1658833663510683e-05, -9.3296533858522462e-05, 0.0002644722126699638, -1.4832312732558724e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00032734891739932787, 0.00010500331426332977, -0.00013221008361318927, 0.00023643299629174703, -9.7200806525402214e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-0.00015171042404239082, 0.00015632324443541956, 0.00013578382796112769, 0.00010264323843666393, 0.00010272966728666578), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.0003706680419021862, -9.7796035434576724e-05, -0.00030120312066552824, 7.7372011364200709e-05, 0.00012036570201547783), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00010829360227043997, 2.1944844657605718e-05, 9.3024612176497573e-05, 0.00043027352167254626, 0.00018125163085709459), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-0.00012944241366535082, 0.00010002203348436331, 0.00016370120827649375, -7.4445229826608058e-05, 0.00010297886178811314), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.00060927872908072655, 0.000235120924927208, 5.7582242939120188e-05, 0.00019865790103679791, 6.6266412717292585e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-0.00016083004155500753, -0.00028068188442831467, 0.00022211575920750624, 0.00023315327552842237, -0.00016988222538935393), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00015462857277116776, 0.0002608302470971415, 0.00014416715596430194, -7.6679797373878204e-05, -0.00015906012345737278), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.00057240398200218354, 0.00051776113656336244, -7.0377726226979832e-05, 4.4816521711611015e-06, -0.00027573035694467501), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-0.00030717930680814549, 7.9983842631354418e-05, -8.7554986380324488e-05, 0.00023335443434345523, -4.1494383584560965e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00029560603307623328, 9.9893710555915498e-05, -0.00012729402219684304, 0.00021744809644476401, -0.00011398997050595862), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-0.00012667413566599766, 0.00013013451753010992, 0.00012417325153450833, 6.8593665045072559e-05, 8.3567694536624198e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00034425357426981924, -8.9548148706954157e-05, -0.00029257702639419838, 8.6757964545319872e-05, 0.00012233131220376687), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00011711783527623226, -7.943837031469769e-06, 6.1095049973865727e-05, 0.00035757813857900358, 0.00015734396761599875), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-0.00010703648052496221, 8.2648049967211845e-05, 0.00016191619209332119, -8.7030654072559459e-05, 9.0570511538503812e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.00052893175870734636, 0.00020421101734968523, 6.5933912262282256e-05, 0.00015416226165302702, 2.2148658968934933e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-0.00014867574247924868, -0.00026510523170711586, 0.00020614188262282174, 0.00020200289145497452, -0.00016779602300593652), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00016617765650152596, 0.00024912459208269064, 0.00012641599593876242, -7.2208921944987567e-05, -0.00014665544686366254), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.00054472635920494871, 0.00049493962251867367, -7.0055046704538409e-05, 1.5181364900986207e-05, -0.00028072534522370119), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-0.00026151034291534223, 6.8923948505453342e-05, -8.1161626702646325e-05, 0.0002025769244807126, -6.7186481401501172e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00026317931909654367, 9.5051862618287044e-05, -0.00012202391318473157, 0.00019873824151468968, -0.00013011760271016058), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-0.00010121465100921307, 0.00010376449868182419, 0.00011320546252559123, 3.4972626085016482e-05, 6.4575917574084216e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00031654922963613325, -8.0888959351366836e-05, -0.00028340008648250307, 9.5450554497924847e-05, 0.00012284845541041289), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00012651912833917434, -3.7006378690386779e-05, 3.0706502076459306e-05, 0.00028438400298530899, 0.00013331329829739574), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-8.4557748339195282e-05, 6.503302586909388e-05, 0.00016031712465758581, -9.9081748015376116e-05, 7.8504346373051571e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.00044777617897376858, 0.00017364495356142384, 7.5111976191530829e-05, 0.0001107707816519045, -2.0371354523751005e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-0.00013489012477392305, -0.00024788788132381749, 0.00018989102532907071, 0.00017025087176793233, -0.0001632286222222419), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00017678519533933574, 0.00023574061257582659, 0.00010817079253551739, -6.719061189927551e-05, -0.00013485427615217435), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.00051581999168768742, 0.00047057155554035496, -6.9998444576584303e-05, 2.6482573709649769e-05, -0.00028653386796007339), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-0.00021798297833271551, 5.895818316474345e-05, -7.6356199003897534e-05, 0.00017248437825947925, -9.0208111888417084e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.0002322322212688758, 9.0919312306564996e-05, -0.00011787172568218852, 0.00018003104410823463, -0.00014465706888814979), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-7.6474232041549536e-05, 7.8472778591551681e-05, 0.00010213472168288539, 3.7824972483603197e-06, 4.7511032986612383e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00028795038039703227, -7.2267506189344378e-05, -0.00027248304324251359, 0.0001038504561601987, 0.00012258207737009941), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00013374249030872204, -6.2259697832856524e-05, 1.8961515917092088e-06, 0.0002147343291894894, 0.00011234819463310894), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-6.2122945755064161e-05, 4.7346105585314855e-05, 0.00015798862298761415, -0.0001096203585527546, 6.7620572783386564e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.00036903857982341766, 0.00014391482287425737, 8.1328055166594672e-05, 6.9525267996282022e-05, -5.8628988338508123e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-0.00012186411331050083, -0.00022815741879974395, 0.00017188056348873239, 0.00013722445377392889, -0.00015693705251996443), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00018537969125219763, 0.0002219250283169866, 9.1000588724311071e-05, -6.143347239075819e-05, -0.0001245411021776654), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.00048725720552835286, 0.0004460748242700864, -7.1286624120083395e-05, 3.739799144626813e-05, -0.00029049357364013118), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-0.00017981635958669792, 5.1763242712206052e-05, -7.2172769492556113e-05, 0.00014531205776821069, -0.00010966702744577802), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00020482513246130159, 8.8727388165375798e-05, -0.00011444786039436751, 0.00016281968251366264, -0.00015685279988408447), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-5.4391781871956158e-05, 5.5327096672119678e-05, 9.2484284967846037e-05, -2.3048047093098057e-05, 3.3102240063666817e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00026138372546549975, -6.5244861964782469e-05, -0.00026132990554631754, 0.0001108101186301829, 0.00012052537376106836), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00013880341613871068, -8.3342223356251411e-05, -2.2295756848135673e-05, 0.00015318121483288988, 9.3580371057515289e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-4.189975463200562e-05, 3.05212608531697e-05, 0.00015575270438301881, -0.00011806869172420292, 5.8776397685322743e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.00029915620403447824, 0.00011813699483592617, 8.6355102415577493e-05, 3.3336745048779013e-05, -9.0411231782914136e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-0.00011119514405248299, -0.00020495839517378365, 0.00015492816274839837, 0.00010649477422541112, -0.00015011299192262161), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00019102041939618239, 0.00020771967636263521, 7.4959591482453631e-05, -5.5392445433291259e-05, -0.00011496862330762284), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.00045989561644945202, 0.00042162696050711311, -7.3378589115117828e-05, 4.8437042088732711e-05, -0.00029263494882884698), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-0.00014744354660355873, 4.7261872072880062e-05, -6.8353558445964765e-05, 0.00012192706403735433, -0.0001250193467395545), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00018108557492585214, 8.8286512973172079e-05, -0.00011160240346494308, 0.00014784770136151817, -0.00016632653973070038), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-3.5570665775729049e-05, 3.4590825062541392e-05, 8.4859978248185834e-05, -4.4968013435309804e-05, 2.1657071831602809e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00023703937045663084, -5.9236921146709203e-05, -0.00025067676329064561, 0.00011563844760367932, 0.00011629118573839701), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00014209447097250329, -0.00010013548603811904, -4.1201162690239855e-05, 0.00010075109001740295, 7.7455771121891462e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-2.4698011590854849e-05, 1.4822317228978866e-05, 0.00015401944002845313, -0.00012428705761838288, 5.2159114938510003e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.00023961404451084491, 9.6485355312083109e-05, 9.09160238425315e-05, 3.3462012357368803e-06, -0.00011488221705841698), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-0.0001014276673269409, -0.00017977765142448702, 0.00013947526775129655, 7.9281139895657276e-05, -0.0001420748490617576), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00019360908647865491, 0.00019302142386325909, 6.0580018921847683e-05, -4.8855828897938025e-05, -0.00010631534659961017), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.00043543930783597663, 0.00039714113019875249, -7.6190867190928388e-05, 5.8724991305896191e-05, -0.00029463582904845772), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-0.00012227833563703606, 4.5135595946894874e-05, -6.587781299892848e-05, 0.0001030402319808153, -0.00013479363748177984), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00016205532744020481, 8.8768611402545075e-05, -0.00010995300057318556, 0.0001355859101358064, -0.00017209688387135759), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-2.140628161904707e-05, 1.8004351867341679e-05, 7.9152741513441636e-05, -6.1362059652159771e-05, 1.3529185828456903e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.0002160451247340707, -5.3717598216410301e-05, -0.00024014007921146428, 0.00011874511689815296, 0.00011034738961405663), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00014228743674307015, -0.00011017221203991524, -5.4083772774573875e-05, 5.9717739175330175e-05, 6.5698942609633109e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-1.1413584782633488e-05, 1.4963313933188522e-06, 0.00015235233580834708, -0.00012837574092807282, 4.7657576403945422e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.00019305976187774095, 7.9657770336002791e-05, 9.3242387509150323e-05, -1.9945488695340867e-05, -0.00013057662951363369), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-9.2828800710792808e-05, -0.00015507143228759928, 0.00012530900133184001, 5.6492302443705978e-05, -0.00013128518296850667), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00019371088018645875, 0.00017832246462805951, 4.8866200297135712e-05, -4.2260046990974709e-05, -0.00010027244953824935), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.0004127331813106144, 0.00037406197367923584, -8.0025767952335533e-05, 6.8574501270254483e-05, -0.00029576986025575745), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-0.00010346693424099605, 4.5398739953600645e-05, -6.4264567735817255e-05, 8.8105665115646381e-05, -0.00014038345488838754), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00014751130710133838, 9.0661469845938758e-05, -0.00010907794629687155, 0.00012539229067755543, -0.00017532264987279338), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-1.0061671491503566e-05, 4.7777700617198441e-06, 7.4850774851964563e-05, -7.2190062351497255e-05, 8.5912023326102165e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00019752253702598227, -5.0111614896033202e-05, -0.00022977306817841103, 0.00012039524042775826, 0.00010332176164936743), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00014080336589690923, -0.00011526930021514767, -6.2048412911566632e-05, 2.894258102997666e-05, 5.7332847696663555e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-4.7045591518158126e-07, -9.9288636093033483e-06, 0.00015058738575975361, -0.00012979037779432749, 4.5494318128712658e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.00015682233573925298, 6.740851311306464e-05, 9.3858628538723044e-05, -3.649579932777916e-05, -0.00013886384015500438), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-8.6597397529624749e-05, -0.00012905030303360469, 0.00011293485142150592, 3.6074936862880684e-05, -0.00012043827391241998), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00019088459284782668, 0.00016453635449904726, 3.8966305418233367e-05, -3.5627603274404203e-05, -9.5981992818679524e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.00039306701024645086, 0.00035252450711585669, -8.3632320582552354e-05, 7.7471914911348401e-05, -0.00029605451163763213), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-9.0638420168335409e-05, 4.7669951481201127e-05, -6.3372376385849099e-05, 7.7270134434321555e-05, -0.00014191554058474857), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00013706413347931403, 9.3567989385768619e-05, -0.00010876854428938307, 0.00011759931572883625, -0.00017579372898250938), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-2.0947433226359971e-06, -5.1304674612095558e-06, 7.2179338260567398e-05, -7.8205438438750137e-05, 6.1667966807371472e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00018225560832164418, -4.7553725708106425e-05, -0.00022014731642790766, 0.00012054094887959814, 9.5760765487874807e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00013802617675077702, -0.00011585102737713868, -6.5440397994526506e-05, 7.8212319348308061e-06, 5.2202864783629796e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(7.4010330513103703e-06, -1.9330405178538608e-05, 0.00014896125619993388, -0.00012918624546274843, 4.4834313851605334e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.00013132754210504964, 5.9432675245125415e-05, 9.3275298075358752e-05, -4.6787366057430107e-05, -0.0001408065709576127), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-8.172249292165609e-05, -0.00010365845816136622, 0.00010211271317721883, 1.9439164137120438e-05, -0.00010908035131496286), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00018616775087684228, 0.00015151029688096864, 3.1549190318812649e-05, -2.9385278674683628e-05, -9.3421071727389936e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.00037602281132214412, 0.00033319604399222264, -8.7323502345920602e-05, 8.4932379759656819e-05, -0.00029556225326764966), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-8.2838504218436815e-05, 5.1251751063302156e-05, -6.3608394676561986e-05, 6.901512834941305e-05, -0.00014079668229746066), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00013016996887647053, 9.7295453852197966e-05, -0.0001093033018597046, 0.00011116274642550388, -0.0001746349027449434), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(2.9158998132126404e-06, -1.2660473409103957e-05, 7.0253763810394985e-05, -8.0646721220079711e-05, 6.0198315184991969e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00016985308512371339, -4.6128916994834418e-05, -0.00021097448279066211, 0.0001195868987519801, 8.8105443521959404e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00013333842904730229, -0.00011341808070019978, -6.6173955304527044e-05, -5.578662783161031e-06, 5.0032403767056829e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(1.2915535473618096e-05, -2.7362629990239646e-05, 0.00014722975681792533, -0.00012717317437225376, 4.5583037156095787e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.00011453404236367372, 5.432957932675836e-05, 9.0910736967298245e-05, -5.3178245654912466e-05, -0.00013822643664836661), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-7.8726600989041917e-05, -7.8735788956984986e-05, 9.2332613232924208e-05, 6.0757051465593534e-06, -9.8444648142067138e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00018028388441500021, 0.00013986586962781933, 2.6054638478692366e-05, -2.3294116579586978e-05, -9.179155049147554e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.0003622291711403315, 0.00031705852721102776, -9.055227440558835e-05, 9.1177106344280019e-05, -0.000295262735877091), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-7.8552313997155008e-05, 5.5044367423274846e-05, -6.3837619574295913e-05, 6.3727755509077644e-05, -0.00013783190500359395), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00012584799449401636, 0.00010069911143563742, -0.00010979670205015886, 0.00010667172631287894, -0.00017243221457428451), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(5.978279086901585e-06, -1.7510809815523999e-05, 6.9419143556434678e-05, -8.0540005748725441e-05, 7.2639326245679828e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00016039896282611169, -4.5492074065902463e-05, -0.00020344675434860333, 0.00011823224158858631, 8.1043370322627127e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00012899592374225293, -0.0001092448416902187, -6.446478540890512e-05, -1.2910813350707172e-05, 4.9841997314043984e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(1.6417055279598311e-05, -3.3153091331157141e-05, 0.00014580195317939076, -0.00012445597127461888, 4.7207216419956802e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-0.0001044487829869448, 5.1845134496770013e-05, 8.8671480063713437e-05, -5.5793946424667646e-05, -0.00013263372408209214), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-7.6699748437375435e-05, -5.7705043855704987e-05, 8.4966562913455743e-05, -4.2757610299206467e-06, -8.8769671336018748e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00017413444311551083, 0.00013023382082093517, 2.2231134516149438e-05, -1.8186685971583225e-05, -9.1502053633413865e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.00035114126491449607, 0.00030320088777147363, -9.2656240650824506e-05, 9.589808668054105e-05, -0.00029449666456655364), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-7.6488145241477459e-05, 5.8795742276865707e-05, -6.4302720775739205e-05, 6.0027087719624126e-05, -0.00013402702108237453), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00012318078624635974, 0.00010380855739534388, -0.00011028415872943796, 0.0001031100840007159, -0.00016954467106374392), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(7.5176192653996654e-06, -2.0773151452937247e-05, 6.8944005412037703e-05, -7.8999177673119632e-05, 8.9143395925141312e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00015337306939410716, -4.5448326521364677e-05, -0.00019716713893237371, 0.00011675066270572895, 7.5117352482262324e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.000124718991784238, -0.00010430474742767411, -6.2197300492457578e-05, -1.6420684868401264e-05, 5.0680461469714786e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(1.8430327366889061e-05, -3.7551575272335709e-05, 0.00014444031745204048, -0.00012137385352116933, 4.8755450283947651e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-9.8851061132478209e-05, 5.0816216660065278e-05, 8.6205067479411807e-05, -5.6487463151670895e-05, -0.00012620375685134741), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-7.5473011323973308e-05, -3.9257395121476269e-05, 7.8832915093438491e-05, -1.2485741066916997e-05, -8.0403601008908422e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00016841806484191096, 0.0001220939048302817, 1.9916236842901709e-05, -1.3947673697956216e-05, -9.1695366766638174e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.00034293640899234077, 0.00029248112363204165, -9.4358709361288574e-05, 9.9627125338698066e-05, -0.00029388536679892871), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-7.5915557087959253e-05, 6.2108617047647701e-05, -6.4575819513803441e-05, 5.7796139864020993e-05, -0.00013028358905952644), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.0001217923334824886, 0.00010643781580675989, -0.00011054744883722577, 0.00010066550468032833, -0.00016681874876248336), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(8.1561064974706978e-06, -2.2811512147366893e-05, 6.8809048656659293e-05, -7.6803791576730084e-05, 1.0751054750436763e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00014839670257300522, -4.5811190692308223e-05, -0.00019227378529333369, 0.00011520094393851571, 7.0278470618574608e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00012121963358777767, -9.9776160522661056e-05, -5.9431918176464785e-05, -1.747239214902776e-05, 5.1998586825155037e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(1.9458256239745404e-05, -4.0643002764802273e-05, 0.00014324889412204326, -0.00011844360043931721, 5.0350510946332204e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-9.6361580863809628e-05, 5.0800668776114445e-05, 8.4144760664008967e-05, -5.5812571985716732e-05, -0.00011987265936859207), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-7.4672895073241524e-05, -2.451824189953452e-05, 7.4589578203726963e-05, -1.8467028342563422e-05, -7.3669575221838331e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.00016353591200165974, 0.00011579903013826876, 1.8372927520379592e-05, -1.0530177640009902e-05, -9.2225513719162836e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(-0.00033716285278150086, 0.00028473949596730835, -9.4440144498771073e-05, 0.00010160170344332741, -0.00029357757435607843), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(-7.5146040521843803e-05, 6.4104691135398906e-05, -6.4669184823811854e-05, 5.5870304419826172e-05, -0.00012749989897947419), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(-0.00012042906772632774, 0.00010790620100221561, -0.00011047486923201761, 9.8634578048176807e-05, -0.0001646678857237941), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(8.4334985074058215e-06, -2.4152792020267772e-05, 6.8646987084629535e-05, -7.563512460691664e-05, 1.1865121368512043e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(0.00014542385848424633, -4.6018896809168274e-05, -0.00018904145790095151, 0.00011444384835924146, 6.7332692725594482e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(0.00011885194149282614, -9.6640887400034839e-05, -5.7999536189198637e-05, -1.8629976094967837e-05, 5.3248222755834261e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(1.9875660352870294e-05, -4.2614068500694045e-05, 0.00014235174159244322, -0.00011656470168512263, 5.1092445441578335e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(-9.4510770387233161e-05, 5.0598596682665122e-05, 8.2837938595504114e-05, -5.595546234320005e-05, -0.00011569369076887666), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(-7.4237827222199446e-05, -1.4622079564299774e-05, 7.1307644870114963e-05, -2.2783783853021305e-05, -6.8799714234541874e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(-0.0001604915696435579, 0.00011142678099771706, 1.7782290280398856e-05, -8.4530315921171654e-06, -9.2769106490147462e-05), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])
