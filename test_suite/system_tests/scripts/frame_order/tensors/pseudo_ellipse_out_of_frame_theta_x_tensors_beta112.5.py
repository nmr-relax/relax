# Rotation matrix:
# [[-0.38268343  0.          0.92387953]
#  [ 0.  1.  0.]
#  [-0.92387953  0.         -0.38268343]]
# Euler angles:
# alpha: 0.0
# beta: 1.96349540849
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
align_tensor.init(tensor='0 red', params=(0.00032378015382085305, -0.0001988510509685051, 0.00025368413735180214, 0.00019462915698808102, 0.00038568189498721061), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00011370113624184955, -0.00025517038659175696, 0.00026161269709063428, -0.00031440807955071737, 0.00020752952577002682), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00016953612731268407, -0.00018361443965793194, 0.00026315164579682171, -0.0002328525453540226, 0.00015747815181675991), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-0.00011807408721505822, -0.00024786409862135022, 0.00011360162570750541, -2.6745655044525731e-05, 0.0001254649304327669), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00033537288402475624, 0.00047627638587084334, 5.3059463662999997e-05, -2.045023298640155e-05, -0.00012746083704858984), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-0.00040229118789229118, -0.00023227854566694163, 0.00033645663013405768, -0.00014652943934320408, -0.00014992077074331848), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-3.5872885567571901e-05, -0.00018342690565096182, -6.256637046941175e-05, 1.6658933925794842e-05, 0.00015629996129966779), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00015756612814750559, -0.00050473491160410661, 0.00022472185332247596, -0.0003496124242013609, 0.00045453778090032544), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00036220288371511882, -0.00050723221329195304, 7.633608643595126e-05, -0.0002940790018902476, -0.00022460998974126824), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.00010991191183905154, -0.00014282930339123452, 4.9851302801596738e-05, 0.00031048139110351284, 2.4081444280668802e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.00032214828844223935, -0.00019762774509063629, 0.00025476467555692582, 0.00019316600588452509, 0.00037904465531583858), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00011541797376486746, -0.00024583821876872613, 0.00025499081306269879, -0.00030092221155782385, 0.00019655239531933674), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.0001694193409562974, -0.00017768169576042687, 0.00025960840494449752, -0.00022369290895339581, 0.00015039338238823286), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-0.00011111703908033753, -0.00023770788344938131, 0.00010436139138749546, -2.219981490996001e-05, 0.00012003016861920862), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00033268358879985253, 0.00046824729232025348, 5.573084434556691e-05, -2.4412974404479151e-05, -0.0001230165533381664), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-0.00038705627920708545, -0.00021527305342722058, 0.00031881680799704609, -0.00014331535347698578, -0.00014707454470854061), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-3.3293051717072757e-05, -0.00017818269435415131, -6.6792448257816642e-05, 2.07507540846431e-05, 0.00014954057396052449), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.0001608159648562894, -0.00048908841720762624, 0.00021375622961567958, -0.00032878760808233501, 0.00043305503711088387), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00035896075949002791, -0.00049556766907111441, 7.1255968301180199e-05, -0.000286654008536201, -0.00022091113771524021), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.000110983987540632, -0.00014171004326359426, 4.9679823878454435e-05, 0.00030086913579225553, 2.9587981644294463e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.00031806177232594643, -0.00019581195714872399, 0.00025619808803104991, 0.00019086018750264755, 0.0003680833171762635), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00011833926609007447, -0.00023096736331559966, 0.00024473410899226457, -0.00027905529671864787, 0.00017893661344508806), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00016913759370741909, -0.000168175603802772, 0.00025416624482720149, -0.00020844983402223792, 0.00013909864361834267), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-0.00010007037431610973, -0.0002214531107288126, 8.981008225046071e-05, -1.5717302128049154e-05, 0.00011096100584628037), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00032812152483543755, 0.00045543002125417013, 5.9414770885313196e-05, -3.0647985480940728e-05, -0.00011526990604088178), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-0.00036256232699098033, -0.00018755021715332302, 0.00029113281144237558, -0.00013869205822956325, -0.00014262548682287036), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-2.9086221520534205e-05, -0.00016998932318295341, -7.344551774916857e-05, 2.64446071049753e-05, 0.00013832546021389704), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.0001662641248460113, -0.00046440237972380095, 0.00019669472084317524, -0.00029598852540372992, 0.00039817196507796574), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00035420532973185436, -0.00047644162823079917, 6.4345231407871226e-05, -0.00027350812797766828, -0.00021517764914378564), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.00011162938852520979, -0.00013974462612980463, 4.9367489087363264e-05, 0.00028528354653775304, 3.8048273425696485e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.00031359190244043542, -0.00019263010268077586, 0.00025857139986555292, 0.0001871672750531779, 0.00035336583498065386), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00012161218879079787, -0.00021174443603644722, 0.00023111200727432904, -0.00025115182280422777, 0.00015644574219842372), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00016852705179427776, -0.00015584913261596552, 0.00024692887216004741, -0.00018925492943761211, 0.0001245024272518266), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-8.6007624450153199e-05, -0.00020044465784599901, 7.0845570587885171e-05, -7.0510207295648042e-06, 9.9669055250700944e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00032188600232526678, 0.00043830507959265804, 6.4480769091933456e-05, -3.8523577462932598e-05, -0.00010595971745395385), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-0.00033139459622048362, -0.00015258214819221171, 0.00025495470857297796, -0.00013215516988101676, -0.00013644115019735922), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-2.3832317428826478e-05, -0.00015914911441902653, -8.2149375533973834e-05, 3.4082810320151463e-05, 0.00012430144217409964), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00017254963469125279, -0.00043209809676042298, 0.00017412587486325049, -0.00025381488171896514, 0.00035389721878854142), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00034699716331135585, -0.00045194959407585415, 5.4532292411874471e-05, -0.0002568981099353336, -0.00020688835430356163), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.00011306360166241559, -0.00013684886233688803, 4.9315611907714817e-05, 0.00026504993883431205, 4.876524571714643e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.00030868365647694613, -0.00018896082980309216, 0.0002617536043570543, 0.00018259122598629211, 0.00033552392614682493), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00012453821353899323, -0.00018932773234163841, 0.00021536612353809044, -0.00021865427917621999, 0.00013057132498494022), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00016725144734136002, -0.00014135412803425659, 0.00023856066374613438, -0.00016684711475129608, 0.00010767776868373844), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-7.0133791537443555e-05, -0.00017638072380172978, 4.9042555286707589e-05, 3.1403480394818784e-06, 8.6407867340885028e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00031382330716922329, 0.00041783889564003091, 7.0327443443740623e-05, -4.7498983947515436e-05, -9.4836620978402351e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-0.00029576581020301365, -0.00011257993985408393, 0.00021300919483677357, -0.00012361294291153617, -0.00012921402002720955), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-1.8094917821763259e-05, -0.00014672537159054496, -9.2071892293143717e-05, 4.2735931972912082e-05, 0.00010790861232042487), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.000178422272868394, -0.00039457468656828494, 0.00014821370536033439, -0.00020507055304871464, 0.00030263718345670813), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.0003372185899981446, -0.00042239234399045922, 4.2682624298569013e-05, -0.00023707487999289571, -0.00019700898921178197), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.0001151356954442106, -0.00013349751765075833, 4.9434766379213428e-05, 0.00024161735618008322, 6.0505071836965742e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.00030317044629372589, -0.00018454686169833368, 0.00026449569816795, 0.00017663101987072465, 0.00031545101091405808), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00012730770090053591, -0.00016500506518462096, 0.00019839531184347777, -0.00018367457095506609, 0.00010350928971582066), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00016552088040727391, -0.00012543855771937504, 0.00022944511380805933, -0.00014256145192936663, 9.0173516566350437e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-5.3206702360881733e-05, -0.00015071610985757417, 2.5721108815552692e-05, 1.3356871289687072e-05, 7.2069089449892755e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00030385840658825374, 0.00039480378383555169, 7.6544767146703927e-05, -5.6705556123211833e-05, -8.3116623670145714e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-0.00025746607622695929, -7.0231781701889659e-05, 0.00016852127780862851, -0.0001145473745614375, -0.00012104279380697699), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-1.206552520868489e-05, -0.00013342893759618651, -0.00010273044591599688, 5.1273770840535027e-05, 9.0106332019172783e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.0001840903956699057, -0.00035392485360043115, 0.00012023398950197494, -0.00015347097815010676, 0.00024820636603460232), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00032483725331559096, -0.00038919878394785563, 3.055928540338541e-05, -0.0002145728901866225, -0.00018472995423011898), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.0001170226329002472, -0.00012958011807846065, 4.9433448867551194e-05, 0.00021576603533472676, 7.2305385729965797e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.0002974971385544383, -0.00017964386501445557, 0.00026711753391096241, 0.00016951948087651211, 0.00029398657251713211), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00012917520697022564, -0.00014026672463643381, 0.0001812073189308795, -0.00014842265497445076, 7.7174932085279975e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00016306696154801164, -0.00010903798156653756, 0.00022015477348362274, -0.00011793500434420207, 7.3216515407824626e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-3.663947297611012e-05, -0.00012520936355952839, 2.3443889893200232e-06, 2.3102696476632718e-05, 5.7530577299384674e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00029226551740342067, 0.00037024240656196206, 8.2702067555748222e-05, -6.5672345105473567e-05, -7.1511493712391404e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-0.00021942940797094299, -2.8612213573942155e-05, 0.00012400278387576905, -0.00010498073890367483, -0.00011232672272816632), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-6.3394292707534497e-06, -0.0001201037932036494, -0.00011341289729872182, 5.9136059470946543e-05, 7.199095131679794e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00018830700435091584, -0.00031261377583962485, 9.1961300704024705e-05, -0.00010235815984197552, 0.00019424321742684189), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00030998240035483754, -0.00035388951911241118, 1.8531893856786415e-05, -0.00019038757102525511, -0.00017044751101298584), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.0001188392471663608, -0.00012533046403055272, 4.9551266285767864e-05, 0.00018928063867175641, 8.3049469557086285e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.00029171657037673626, -0.00017410457736270215, 0.00026964719033438728, 0.00016119720937969543, 0.00027202917531674622), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00012962583454455886, -0.00011632378357001811, 0.00016493511810276856, -0.00011468683927420422, 5.3102639066078906e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00015959556033840592, -9.2762022348225149e-05, 0.00021133826953318997, -9.4129150375156845e-05, 5.7716273209275042e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-2.1309299321861278e-05, -0.00010156387282216852, -1.967423515971483e-05, 3.1645629934305605e-05, 4.3671350750713632e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00027908328976953271, 0.00034531460024183957, 8.8266416492508977e-05, -7.3558275321681268e-05, -6.0620918805698895e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-0.00018364773748100251, 9.4848026792385815e-06, 8.1945743131246943e-05, -9.5073862193986253e-05, -0.00010349875613062014), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(-1.1681747576383358e-06, -0.00010773827868628545, -0.00012341971586582755, 6.5526414591866882e-05, 5.4688112172221702e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00019037246288332413, -0.00027294115185014852, 6.530791972314369e-05, -5.481060956644719e-05, 0.00014395064106207981), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00029239186859788944, -0.00031796526742870941, 7.3801216193495744e-06, -0.00016536519573911816, -0.00015500925948454416), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.0001204284766685669, -0.00012088455972981663, 4.9801382036876424e-05, 0.00016331346350316602, 9.1884957734383855e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.00028599740565630436, -0.00016778227827160601, 0.00027192961101326561, 0.0001515692199749541, 0.00024999121060074986), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00012888061714062495, -9.4383493516198049e-05, 0.00014994566511809787, -8.4233657669837201e-05, 3.2805200164750777e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00015554711244557162, -7.7542102021082307e-05, 0.00020306521380645035, -7.2444471505334491e-05, 4.465265512199698e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(-8.1377282368331496e-06, -8.053843627334565e-05, -3.9212666980162727e-05, 3.8358751032030702e-05, 3.124998291147263e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00026479906153974381, 0.00032071244878387553, 9.306983668685634e-05, -8.0269201591397845e-05, -5.1421368846581825e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-0.00015184484493688773, 4.2214964478443589e-05, 4.4574472495617905e-05, -8.5710814625218049e-05, -9.4488005319834478e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(2.9548335885479527e-06, -9.6475318097920075e-05, -0.00013224473395409306, 7.0133726126548471e-05, 3.9027813135734931e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00019021489468982515, -0.00023636974458029022, 4.1045744279364998e-05, -1.3261224601162051e-05, 0.00010012414047929914), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00027327034034324463, -0.00028338247039646689, -2.6902084258818016e-06, -0.00014012372721144384, -0.00013776998429260973), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.00012146379134487713, -0.00011608600132445298, 5.0494499540008298e-05, 0.00013892121145288157, 9.809258504001762e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.00028051475387006386, -0.00016116550085826882, 0.00027369681779728137, 0.00014141074510628997, 0.00022902661407645398), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00012647569952557513, -7.4745350398934047e-05, 0.00013702763276374354, -5.7812124891031356e-05, 1.6951883347283403e-05), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00015064738493766248, -6.3417595834068709e-05, 0.00019585242666117123, -5.3228887481295084e-05, 3.4597499604204681e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(2.3452446975092598e-06, -6.3098818064441286e-05, -5.5682305251433105e-05, 4.3012256731173431e-05, 2.0498874293291565e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00024953849439004517, 0.00029725025849244434, 9.68103036826401e-05, -8.5357864547881381e-05, -4.3615238571140269e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-0.00012524905362645762, 6.8574207641830865e-05, 1.3114165575443157e-05, -7.6808117151597383e-05, -8.5631306173411935e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(5.8750589563358025e-06, -8.7063838214398542e-05, -0.00013965108478616059, 7.2515983030952137e-05, 2.5221147240441063e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00018722811475229317, -0.00020400894331191398, 2.0277970261160826e-05, 2.0884173958044481e-05, 6.3879004110093399e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00025246381902967007, -0.00025026538272527178, -1.0775890066579147e-05, -0.00011541979588657598, -0.0001199987724947874), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.00012208496322217035, -0.0001114635784698933, 5.1338956575901676e-05, 0.00011708556766557334, 0.00010153155788459598), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.00027523067920953216, -0.00015444325557153679, 0.00027512265341291756, 0.00013078141843302478, 0.00020935183664095696), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00012267711033526067, -5.8123395477421894e-05, 0.00012624050233470455, -3.607278176437693e-05, 5.72454664738275e-06), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00014510290063272959, -5.0993161092282598e-05, 0.00018967331700337766, -3.7018191254801042e-05, 2.7539625738347363e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(1.0058129761121086e-05, -4.9536423829655855e-05, -6.8725775716892918e-05, 4.548208153548987e-05, 1.1725496875272532e-05), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00023395210072008773, 0.0002756187988871977, 9.9479647350980452e-05, -8.8866854395277373e-05, -3.7638401634911562e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-0.00010434541004835304, 8.8038953109961112e-05, -1.1955384936556144e-05, -6.8799116071576873e-05, -7.7237857166633834e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(7.7024673936225524e-06, -7.9589356233731478e-05, -0.00014541077562352521, 7.273511905384293e-05, 1.3777305158706261e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00018192271670290975, -0.00017679644155949319, 3.2811166010669395e-06, 4.6937458101062267e-05, 3.6041693803739438e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00023085465570114855, -0.00021992043037635572, -1.7208765145736895e-05, -9.1737148294447583e-05, -0.00010197601265688219), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.0001221403724533316, -0.00010700874852518245, 5.2494976977424798e-05, 9.8201378436724168e-05, 0.00010213263966554925), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.00027102556820314322, -0.00014808371456347854, 0.00027594917111166764, 0.0001197561019213932, 0.00019138311348560724), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00011741316463700816, -4.464515410217929e-05, 0.00011794920010245235, -1.9426623146117396e-05, -7.9760721343693391e-07), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00013894026718093923, -4.0413640785821906e-05, 0.00018477623709220754, -2.4330196137008964e-05, 2.355054770060586e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(1.5114765468289094e-05, -4.0011619801108325e-05, -7.8218202703615017e-05, 4.6175290909440564e-05, 4.9882266248604762e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00021869617227716204, 0.0002562327086322847, 0.00010105525651213089, -9.0488818473227471e-05, -3.3643203314218464e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-8.9477441580585354e-05, 0.00010054820093416674, -3.0280619547022064e-05, -6.1391103989920511e-05, -6.9590810574418814e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(8.6043818082407084e-06, -7.415490419942243e-05, -0.00014949377107256794, 7.1213405478803214e-05, 4.8261545214507403e-06), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00017446257528163582, -0.00015501495753811239, -9.5042981152759454e-06, 6.4817640397515656e-05, 1.6894570594148981e-05), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00020857127090330766, -0.00019263305323944963, -2.1594795345919641e-05, -7.0446969723627281e-05, -8.3952665870368621e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.00012230314804809059, -0.00010305588794353453, 5.3651513810966313e-05, 8.2495985578902889e-05, 0.00010000909890376616), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.00026701519448047865, -0.00014185818702370647, 0.00027643834842212302, 0.00010922065053673281, 0.00017550254378858403), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00011158698259201433, -3.4439884477414263e-05, 0.00011186443059343161, -6.9877855632305061e-06, -3.5958508256812529e-06), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00013284261565180101, -3.1933439279410319e-05, 0.00018103929972247942, -1.4375112193045721e-05, 2.2005437390870352e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(1.7708318585619786e-05, -3.3832909189918248e-05, -8.4604452699270897e-05, 4.5251054794949236e-05, -6.9268047404024704e-08), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00020400906916740239, 0.00023933517071464394, 0.00010160871987666955, -9.0991870507907657e-05, -3.1266814467116649e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-7.9550184753445611e-05, 0.00010722378609966854, -4.2822190444864466e-05, -5.4991221639574962e-05, -6.3046914520315344e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(8.4467808798044932e-06, -7.0376019539144261e-05, -0.00015209138626577588, 6.8146262796679852e-05, -1.9588568658614856e-06), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00016568459196086884, -0.00013852085251734469, -1.853861211686386e-05, 7.5910813170454444e-05, 4.9091614954839422e-06), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00018742705750004926, -0.00016936843238856664, -2.4244115430792048e-05, -5.0853745877533696e-05, -6.6729838873951536e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.00012186219372435698, -9.9194783696146375e-05, 5.4881310560240961e-05, 6.9922191339700051e-05, 9.5954742377149402e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.00026397348028949164, -0.0001362774977552672, 0.00027664699979063171, 9.9318858453225863e-05, 0.00016175007112216892), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(0.00010541095842941474, -2.6732352100282626e-05, 0.00010751981113941242, 1.4696983209333112e-06, -3.4510873708155026e-06), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.0001269570658645206, -2.5064849244952481e-05, 0.00017817077212919433, -7.1874090409247522e-06, 2.2331771068464036e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(1.8389185210234701e-05, -3.0457388812656432e-05, -8.8351433983907643e-05, 4.310339275595906e-05, -3.5073620235184075e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00019037299602395381, 0.00022488958131377501, 0.00010141190588047446, -9.0443257711721634e-05, -3.0148810275693004e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-7.4041944695444245e-05, 0.00010940030298247928, -5.0449120888234032e-05, -4.9773204161322491e-05, -5.7319741934944713e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(7.5890659210990828e-06, -6.8087003417722865e-05, -0.00015342129818043146, 6.4101756123705289e-05, -6.7503422192038973e-06), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00015621667729743944, -0.00012632755907236688, -2.4547996347992135e-05, 8.1139443141743607e-05, -1.1032412453716182e-06), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00016735221411288731, -0.00014936305325109731, -2.5682714204062755e-05, -3.382755682673709e-05, -5.0915882736152102e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.00012137909620693066, -9.5900356249989754e-05, 5.6231552838883922e-05, 6.0214833960818056e-05, 9.0588511949775305e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.00026134149017508873, -0.00013154237942229925, 0.000276043081090388, 9.0656461098086885e-05, 0.00015038968372647004), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(9.9321327827670073e-05, -2.1266841524396834e-05, 0.00010463937855103676, 6.9337925213590444e-06, -1.3489429041836949e-06), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.0001213587615655994, -1.9772408702261338e-05, 0.00017605128973080403, -2.1765742796001932e-06, 2.3898098194579069e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(1.8013772620470198e-05, -2.9208680523996346e-05, -9.0303947657928549e-05, 4.0487819538695886e-05, -5.6187569947752672e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00017868075942559914, 0.00021334575558950837, 0.00010093065151520131, -8.9302484973552101e-05, -3.0130837664540655e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-7.1604220776760034e-05, 0.00010852143250680156, -5.4398288935252694e-05, -4.5474208599817926e-05, -5.2531738592842027e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(6.6558007898545894e-06, -6.7021481413732806e-05, -0.00015395303318457721, 5.981046384575957e-05, -9.8708594802924841e-06), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00014714093213037704, -0.00011799301261833148, -2.8277870398890607e-05, 8.2517334937683731e-05, -2.6958457453615398e-06), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00014956762151248384, -0.00013319983131131381, -2.5970813774275942e-05, -1.9694778873469367e-05, -3.6870662384548488e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.00012085245919978067, -9.3254566251418122e-05, 5.7124633307384552e-05, 5.304994279244247e-05, 8.4800267550795227e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.0002595264828796745, -0.00012794460662844109, 0.00027513404766802872, 8.3376917767243031e-05, 0.00014113979539327333), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(9.3894180609538195e-05, -1.7464003221946822e-05, 0.00010255177749083268, 1.026052513358459e-05, 1.6825160502135768e-06), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00011654446057230181, -1.5815737995462938e-05, 0.00017429178986138886, 1.2313355556559295e-06, 2.5996366702467504e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(1.7077652071599552e-05, -2.9239363823837576e-05, -9.1049321827101916e-05, 3.7671627512235952e-05, -6.7295564057698903e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00016900111809461195, 0.00020429060280911028, 0.0001002923839348373, -8.7909581943012728e-05, -3.060411771589179e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-7.1100555183743088e-05, 0.00010602805351144981, -5.603745857708549e-05, -4.2272364871276738e-05, -4.8404325378166548e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(5.6894910664510195e-06, -6.6673204621842098e-05, -0.00015390454047354147, 5.5635908073785334e-05, -1.1776939036246897e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00013910729247128454, -0.00011239953305806102, -3.0641835023350629e-05, 8.1527228752290853e-05, -1.6843161147361647e-06), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00013441494088951126, -0.00012028793880785923, -2.5884675974783295e-05, -8.2480241773141454e-06, -2.5048689441178553e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.0001204674872172311, -9.1351104611311841e-05, 5.7918141719656149e-05, 4.7835875918206482e-05, 7.9182472955307529e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.00025801244783887629, -0.00012506243450014946, 0.00027403245576919502, 7.7742607517419037e-05, 0.00013396574669483373), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(8.943363249501209e-05, -1.4902618840282076e-05, 0.0001010397743802103, 1.2545249907444147e-05, 4.4955839381157536e-06), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.00011262536827455877, -1.2947819756001188e-05, 0.00017281428464459178, 3.7236367743768373e-06, 2.7919868845302577e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(1.6100519465501323e-05, -2.9702359089695724e-05, -9.1160499200188159e-05, 3.535035232086399e-05, -7.4727726588401402e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00016157120504050975, 0.00019754707932952281, 9.9570556459430248e-05, -8.6898892777321059e-05, -3.1373945959761883e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-7.1252194795189041e-05, 0.00010341237411557025, -5.6636041336864139e-05, -3.9734620991016892e-05, -4.5437425890441375e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(4.884800217383487e-06, -6.6679630667055827e-05, -0.00015347760913028089, 5.2207975042112361e-05, -1.3014150127857711e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.00013256149887201423, -0.0001087739376429645, -3.1993958716041773e-05, 8.0182542834288396e-05, -3.3969704317514764e-08), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00012269356328219031, -0.00011065139580378663, -2.5670941890543177e-05, 9.2733214860738079e-07, -1.548238081077385e-05), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.00012016670243321237, -8.9794005516575194e-05, 5.844194740156454e-05, 4.4121470727493158e-05, 7.4493737900364164e-05), param_types=0)
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
align_tensor.init(tensor='0 red', params=(0.0002572771324431594, -0.00012369143176369518, 0.00027247072592266733, 7.3776110421433492e-05, 0.00012872167732380657), param_types=0)
align_tensor.init(tensor='0 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='0 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='0 full', domain='full')
align_tensor.set_domain(tensor='0 red', domain='red')

# Load tensor 1.
align_tensor.init(tensor='1 full', params=(-0.00014307694949297205, -0.00039671919293883539, -0.00024724524395487659, 0.00031948292975139144, 0.00018868359624777637), param_types=0)
align_tensor.init(tensor='1 red', params=(8.6137248992117715e-05, -1.3105850942916754e-05, 9.9651316303645899e-05, 1.4133379247596585e-05, 6.5431693015033398e-06), param_types=0)
align_tensor.init(tensor='1 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='1 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='1 full', domain='full')
align_tensor.set_domain(tensor='1 red', domain='red')

# Load tensor 2.
align_tensor.init(tensor='2 full', params=(-0.00022967898444150887, -0.00027171643813494106, -0.00021961563147411279, 0.00010337393266477703, 0.00029030226175831515), param_types=0)
align_tensor.init(tensor='2 red', params=(0.0001096872677822838, -1.0987218506126125e-05, 0.00017130504049044174, 5.4751878391841053e-06, 2.9262204293696149e-05), param_types=0)
align_tensor.init(tensor='2 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='2 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='2 full', domain='full')
align_tensor.set_domain(tensor='2 red', domain='red')

# Load tensor 3.
align_tensor.init(tensor='3 full', params=(0.00043690692358615301, -0.00034379559287467062, -0.00019359695171683388, 0.00030194133983804048, -6.314162250164486e-05), param_types=0)
align_tensor.init(tensor='3 red', params=(1.5566619607125847e-05, -3.0098964129661258e-05, -9.1107742926380009e-05, 3.3669276777112669e-05, -7.8580783417287527e-06), param_types=0)
align_tensor.init(tensor='3 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='3 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='3 full', domain='full')
align_tensor.set_domain(tensor='3 red', domain='red')

# Load tensor 4.
align_tensor.init(tensor='4 full', params=(-0.00026249527958822807, 0.00073561736796410628, 6.3975419225898133e-05, 6.2788017118057252e-05, 0.00020119758245770023), param_types=0)
align_tensor.init(tensor='4 red', params=(-0.00015670841486874586, 0.00019316150009254633, 9.9028837136750221e-05, -8.6263820771575051e-05, -3.2098436619622879e-05), param_types=0)
align_tensor.init(tensor='4 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='4 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='4 full', domain='full')
align_tensor.set_domain(tensor='4 red', domain='red')

# Load tensor 5.
align_tensor.init(tensor='5 full', params=(0.00048180707211229368, -0.00033930112217225942, 0.00011094068795736053, 0.00070350646902989675, 0.00037537667271407197), param_types=0)
align_tensor.init(tensor='5 red', params=(-7.1630497490284689e-05, 0.00010188933955548871, -5.6912469733070745e-05, -3.8039563410245703e-05, -4.3148119277724783e-05), param_types=0)
align_tensor.init(tensor='5 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='5 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='5 full', domain='full')
align_tensor.set_domain(tensor='5 red', domain='red')

# Load tensor 6.
align_tensor.init(tensor='6 full', params=(0.00035672066304092451, -0.00026838578790208884, -0.00016936140664230585, 0.00017187371551506447, -0.00030579015509609098), param_types=0)
align_tensor.init(tensor='6 red', params=(4.6052329255327578e-06, -6.6811717310683393e-05, -0.0001529057897819536, 4.9775722173475362e-05, -1.3757895473232604e-05), param_types=0)
align_tensor.init(tensor='6 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='6 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='6 full', domain='full')
align_tensor.set_domain(tensor='6 red', domain='red')

# Load tensor 7.
align_tensor.init(tensor='7 full', params=(0.00017061308478202151, -0.00076455273118810501, -0.00052048809712606505, 0.00049258369866413392, -0.00013905141064073534), param_types=0)
align_tensor.init(tensor='7 red', params=(0.0001281171076203785, -0.00010642497567064398, -3.3083647029955203e-05, 7.9201063564970564e-05, 1.3273905357079369e-06), param_types=0)
align_tensor.init(tensor='7 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='7 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='7 full', domain='full')
align_tensor.set_domain(tensor='7 red', domain='red')

# Load tensor 8.
align_tensor.init(tensor='8 full', params=(-0.00022193220790426714, -0.00090073235703922686, 0.00050867766236886724, 0.00028215012727179065, 0.0002562167583736733), param_types=0)
align_tensor.init(tensor='8 red', params=(0.00011420957433800564, -0.00010376834852329669, -2.5582704893371442e-05, 7.5089923732747366e-06, -8.4790575182231382e-06), param_types=0)
align_tensor.init(tensor='8 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='8 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='8 full', domain='full')
align_tensor.set_domain(tensor='8 red', domain='red')

# Load tensor 9.
align_tensor.init(tensor='9 full', params=(0.00037091020965736575, -0.00012230875848954012, -0.00016247713611487416, -0.00042725170061841107, 9.0103851318397519e-05), param_types=0)
align_tensor.init(tensor='9 red', params=(0.00012025344664230896, -8.9080788090048509e-05, 5.8603118718874339e-05, 4.1527707228167404e-05, 7.1139059507211873e-05), param_types=0)
align_tensor.init(tensor='9 full', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.init(tensor='9 red', params=(error, error, error, error, error), param_types=0, errors=True)
align_tensor.set_domain(tensor='9 full', domain='full')
align_tensor.set_domain(tensor='9 red', domain='red')

# Tensor reductions.
for i in range(len(full_list)):
    align_tensor.reduction(full_tensor=full_list[i], red_tensor=red_list[i])
