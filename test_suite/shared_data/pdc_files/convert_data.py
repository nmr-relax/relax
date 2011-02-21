#! /usr/bin/env python

# The data - PDC T2, PDC T2 err, PDC scale factor, relax R2, relax R2 err (MC sim).
data = [
['Gln',  2,  0.4560, 0.012326 ,   2.22814 ,       2.19316068443,      0.0264822775112],
['Ile',  3,  0.4289, 0.0089800 ,   2.22814 ,       2.33150942395,      0.0218282475286],
['Phe',  4,  0.4259, 0.015866 ,   2.22814 ,       2.34809773828,      0.0393993956573],
['Val',  5,  0.4446, 0.0084807 ,   2.22814 ,       2.24905317514,      0.0190416227806],
['Lys',  6,  0.4386, 0.0032737 ,   2.22814 ,       2.27991249993,      0.0073387122964],
['Thr',  7,  0.4505, 0.012887 ,   2.22814 ,       2.21988325334,      0.0289980021014],
['Leu',  8,  0.4464, 0.017357 ,    2.22814,       2.23992585719,      0.0394637142884],
['Thr',  9,  0.5081, 0.016893 ,    2.22814,       1.96827404586,      0.0285585555608],
['Gly', 10,  0.4789, 0.0045383 ,    2.22814,       2.08825352037,     0.00856203608884],
['Lys', 11,  0.5006, 0.0087386 ,    2.22814,       1.99766965295,      0.0154821098023],
['Thr', 12,  0.4621, 0.028354 ,    2.22814,       2.16418266589,      0.0589894950385],
['Ile', 13,  0.4400, 0.014724 ,   2.22814 ,       2.27249997894,      0.0323797055027],
['Thr', 14,  0.4547, 0.011743 ,   2.22814 ,       2.19913359459,      0.0261282530191],
['Leu', 15,  0.4387, 0.033559 ,   2.22814 ,       2.27947735732,      0.0804008170395],
['Glu', 16,  0.4792, 0.038163 ,    2.22814,       2.08663871613,      0.0742976416989],
['Val', 17,  0.4377, 0.013371 ,   2.22814 ,       2.28454679926,      0.0319478148557],
['Glu', 18,  0.4744, 0.025534 ,   2.22814 ,       2.10794161516,      0.0491390514111],
['Ser', 20,  0.4458, 0.0075985 ,   2.22814 ,        2.2432376545,      0.0174075720472],
['Asp', 21,  0.4257, 0.0036873 ,   2.22814 ,       2.34905882789,     0.00896916086091],
['Thr', 22,  0.4396, 0.012438 ,   2.22814 ,       2.27492782819,      0.0283784241729],
['Ile', 23,  0.4054, 0.018904 ,    2.22814,       2.46692508258,      0.0512139594604],
['Asn', 25,  0.4174, 0.010689 ,   2.22814 ,       2.39550908267,       0.028141856637],
['Val', 26,  0.4688, 0.035345 ,    2.22814,       2.13297271051,      0.0738836932379],
['Lys', 27,  0.4233, 0.013666 ,   2.22814 ,       2.36245343286,       0.034473000886],
['Ala', 28,  0.4193, 0.014360 ,   2.22814 ,       2.38481618154,      0.0369276054641],
['Lys', 29,  0.4298, 0.011476 ,   2.22814 ,       2.32688199592,      0.0267154381038],
['Thr', 30,  0.4132, 0.026029 ,    2.22814,       2.42020223098,      0.0641345037416],
['Gln', 31,  0.4216, 0.023199 ,   2.22814 ,       2.37198006924,      0.0607157552927],
['Asp', 32,  0.4268, 0.011464 ,   2.22814 ,         2.343030317,      0.0287089229986],
['Lys', 33,  0.4560, 0.014005 ,   2.22814 ,       2.19288519999,      0.0322404521468],
['Glu', 34,  0.4468, 0.0067758 ,   2.22814 ,       2.23809730593,       0.016155226898],
['Gly', 35,  0.4452, 0.0072146 ,   2.22814 ,       2.24610605696,      0.0166231784999],
['Ile', 36,  0.5023, 0.011122 ,   2.22814 ,       1.99097003714,       0.018556395961],
['Asp', 39,  0.4360, 0.0041799 ,   2.22814 ,       2.29368308937,      0.0107946336402],
['Gln', 40,  0.4435, 0.0097303 ,   2.22814 ,       2.25465715695,      0.0219579437623],
['Gln', 41,  0.4496, 0.010974 ,   2.22814 ,       2.22439489827,      0.0246838738103],
['Arg', 42,  0.4386, 0.060259 ,    2.22814,       2.27979894813,        0.14609662846],
['Leu', 43,  0.4603, 0.027054 ,   2.22814 ,       2.17239195077,      0.0562093749792],
['Ile', 44,  0.4387, 0.012389 ,   2.22814 ,       2.27944810393,      0.0274015962376],
['Phe', 45,  0.4413, 0.014084 ,   2.22814 ,       2.26621382042,      0.0325598012054],
['Ala', 46,  0.4601, 0.017401 ,    2.22814,       2.17327103743,      0.0366263114163],
['Gly', 47,  0.4563, 0.0095167 ,    2.22814,       2.19159971705,      0.0200974396044],
['Lys', 48,  0.4543, 0.034380 ,    2.22814,       2.20125816954,      0.0769594227925],
['Gln', 49,  0.4730, 0.0099851 ,   2.22814 ,       2.11409184343,      0.0211565921351],
['Leu', 50,  0.4455, 0.020395 ,   2.22814 ,       2.24441747047,      0.0466054926297],
['Glu', 51,  0.4687, 0.018214 ,   2.22814 ,       2.13351495913,      0.0369010861993],
['Asp', 52,  0.4888, 0.017327 ,   2.22814 ,       2.04583349976,      0.0309251585403],
['Arg', 54,  0.4561, 0.0059463 ,   2.22814 ,       2.19228267695,      0.0125176652031],
['Thr', 55,  0.4396, 0.013766 ,   2.22814 ,       2.27502074947,      0.0319568936121],
['Leu', 56,  0.4221, 0.0064286 ,   2.22814 ,       2.36913113746,      0.0158844775147],
['Ser', 57,  0.4351, 0.0057569 ,   2.22814 ,       2.29814478201,      0.0142640516301],
['Asp', 58,  0.4207, 0.010105 ,   2.22814 ,       2.37720483191,      0.0272911357828],
['Tyr', 59,  0.4493, 0.0055646 ,   2.22814 ,       2.22553611629,      0.0125933167265],
['Asn', 60,  0.4377, 0.0058785 ,   2.22814 ,       2.28459962433,       0.013370924242],
['Ile', 61,  0.4270, 0.010546 ,   2.22814 ,       2.34213728573,      0.0264153868176],
['Gln', 62,  0.5067, 0.012662 ,   2.22814 ,       1.97367886288,      0.0217945020797],
['Lys', 63,  0.4619, 0.0094808 ,   2.22814 ,       2.16500024708,      0.0195312534223],
['Glu', 64,  0.4312, 0.0095453 ,   2.22814 ,       2.31913930394,      0.0223294049604],
['Ser', 65,  0.4568, 0.0043694 ,   2.22814 ,       2.18918681844,     0.00908363177241],
['Thr', 66,  0.4584, 0.0054046 ,   2.22814 ,       2.18167008464,      0.0112902195625],
['Leu', 67,  0.4410, 0.018436 ,    2.22814,       2.26772345178,      0.0444564014823],
['His', 68,  0.4451, 0.0043067 ,   2.22814 ,       2.24680733455,     0.00926065649886],
['Leu', 69,  0.4447, 0.015813 ,   2.22814 ,       2.24851949133,      0.0379125750722],
['Val', 70,  0.4319, 0.011793 ,   2.22814 ,       2.31543911345,      0.0279226422469],
['Leu', 71,  0.4596, 0.0046414 ,   2.22814 ,        2.1756894166,     0.00987045835498],
['Arg', 72,  0.4622, 0.012209 ,   2.22814 ,       2.16361975928,      0.0253849160526],
['Leu', 73,  0.5386, 0.016241 ,    2.22814,       1.85657597782,      0.0255460422485],
['Arg', 74,  0.6202, 0.020482 ,    2.22814,        1.6122677679,      0.0231001217925],
['Gly', 75,  0.8603, 0.038094 ,    2.22814,       1.16243924266,       0.023448186193],
['Gly', 76,   1.311, 0.011609 ,    2.22814,      0.763064480891,      0.0030557315479]]

r1 = []
r1_err = []
print("%-4s %-3s %-15s %-15s %-15s %-15s" % ('Name', 'Num', 'r1', 'err', 'r1_relax_ratio', 'err_relax_ratio'))
for i in range(len(data)):
    r1.append(1.0/data[i][2])
    r1_err.append((data[i][3] / data[i][4]) / data[i][2]**2)

    print("%-4s %-3s %15.10f %15.10f %15.10f %15.10f" % (data[i][0], data[i][1], r1[-1], r1_err[-1], r1[-1]/data[i][5], r1_err[-1]/data[i][6]))

print("\nr1 = %s" % r1)
print("\nr1_err = %s" % r1_err)
