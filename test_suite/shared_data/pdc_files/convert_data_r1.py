#! /usr/bin/env python

from string import split, strip


# The file data.
file = open('testT1.txt')
lines = file.readlines()
file.close()

# The data - PDC T2, PDC T2 err, PDC scale factor, relax R2, relax R2 err (MC sim).
data = [
['Gln',  2, None, None, None, 2.19316068443,      0.0264822775112],
['Ile',  3, None, None, None, 2.33150942395,      0.0218282475286],
['Phe',  4, None, None, None, 2.34809773828,      0.0393993956573],
['Val',  5, None, None, None, 2.24905317514,      0.0190416227806],
['Lys',  6, None, None, None, 2.27991249993,      0.0073387122964],
['Thr',  7, None, None, None, 2.21988325334,      0.0289980021014],
['Leu',  8, None, None, None, 2.23992585719,      0.0394637142884],
['Thr',  9, None, None, None, 1.96827404586,      0.0285585555608],
['Gly', 10, None, None, None, 2.08825352037,     0.00856203608884],
['Lys', 11, None, None, None, 1.99766965295,      0.0154821098023],
['Thr', 12, None, None, None, 2.16418266589,      0.0589894950385],
['Ile', 13, None, None, None, 2.27249997894,      0.0323797055027],
['Thr', 14, None, None, None, 2.19913359459,      0.0261282530191],
['Leu', 15, None, None, None, 2.27947735732,      0.0804008170395],
['Glu', 16, None, None, None, 2.08663871613,      0.0742976416989],
['Val', 17, None, None, None, 2.28454679926,      0.0319478148557],
['Glu', 18, None, None, None, 2.10794161516,      0.0491390514111],
['Ser', 20, None, None, None, 2.2432376545,      0.0174075720472],
['Asp', 21, None, None, None, 2.34905882789,     0.00896916086091],
['Thr', 22, None, None, None, 2.27492782819,      0.0283784241729],
['Ile', 23, None, None, None, 2.46692508258,      0.0512139594604],
['Asn', 25, None, None, None, 2.39550908267,       0.028141856637],
['Val', 26, None, None, None, 2.13297271051,      0.0738836932379],
['Lys', 27, None, None, None, 2.36245343286,       0.034473000886],
['Ala', 28, None, None, None, 2.38481618154,      0.0369276054641],
['Lys', 29, None, None, None, 2.32688199592,      0.0267154381038],
['Thr', 30, None, None, None, 2.42020223098,      0.0641345037416],
['Gln', 31, None, None, None, 2.37198006924,      0.0607157552927],
['Asp', 32, None, None, None, 2.343030317,      0.0287089229986],
['Lys', 33, None, None, None, 2.19288519999,      0.0322404521468],
['Glu', 34, None, None, None, 2.23809730593,       0.016155226898],
['Gly', 35, None, None, None, 2.24610605696,      0.0166231784999],
['Ile', 36, None, None, None, 1.99097003714,       0.018556395961],
['Asp', 39, None, None, None, 2.29368308937,      0.0107946336402],
['Gln', 40, None, None, None, 2.25465715695,      0.0219579437623],
['Gln', 41, None, None, None, 2.22439489827,      0.0246838738103],
['Arg', 42, None, None, None, 2.27979894813,        0.14609662846],
['Leu', 43, None, None, None, 2.17239195077,      0.0562093749792],
['Ile', 44, None, None, None, 2.27944810393,      0.0274015962376],
['Phe', 45, None, None, None, 2.26621382042,      0.0325598012054],
['Ala', 46, None, None, None, 2.17327103743,      0.0366263114163],
['Gly', 47, None, None, None, 2.19159971705,      0.0200974396044],
['Lys', 48, None, None, None, 2.20125816954,      0.0769594227925],
['Gln', 49, None, None, None, 2.11409184343,      0.0211565921351],
['Leu', 50, None, None, None, 2.24441747047,      0.0466054926297],
['Glu', 51, None, None, None, 2.13351495913,      0.0369010861993],
['Asp', 52, None, None, None, 2.04583349976,      0.0309251585403],
['Arg', 54, None, None, None, 2.19228267695,      0.0125176652031],
['Thr', 55, None, None, None, 2.27502074947,      0.0319568936121],
['Leu', 56, None, None, None, 2.36913113746,      0.0158844775147],
['Ser', 57, None, None, None, 2.29814478201,      0.0142640516301],
['Asp', 58, None, None, None, 2.37720483191,      0.0272911357828],
['Tyr', 59, None, None, None, 2.22553611629,      0.0125933167265],
['Asn', 60, None, None, None, 2.28459962433,       0.013370924242],
['Ile', 61, None, None, None, 2.34213728573,      0.0264153868176],
['Gln', 62, None, None, None, 1.97367886288,      0.0217945020797],
['Lys', 63, None, None, None, 2.16500024708,      0.0195312534223],
['Glu', 64, None, None, None, 2.31913930394,      0.0223294049604],
['Ser', 65, None, None, None, 2.18918681844,     0.00908363177241],
['Thr', 66, None, None, None, 2.18167008464,      0.0112902195625],
['Leu', 67, None, None, None, 2.26772345178,      0.0444564014823],
['His', 68, None, None, None, 2.24680733455,     0.00926065649886],
['Leu', 69, None, None, None, 2.24851949133,      0.0379125750722],
['Val', 70, None, None, None, 2.31543911345,      0.0279226422469],
['Leu', 71, None, None, None, 2.1756894166,     0.00987045835498],
['Arg', 72, None, None, None, 2.16361975928,      0.0253849160526],
['Leu', 73, None, None, None, 1.85657597782,      0.0255460422485],
['Arg', 74, None, None, None, 1.6122677679,      0.0231001217925],
['Gly', 75, None, None, None, 1.16243924266,       0.023448186193],
['Gly', 76, None, None, None, 0.763064480891,      0.0030557315479]]

# Get the data.
in_data = False
index = 0
for line in lines:
    # Split the line.
    row = split(line, "\t")

    # Strip the rubbish.
    for j in range(len(row)):
        row[j] = strip(row[j])

    # Empty line.
    if len(row) == 0:
        continue

    # The section.
    if row[0] == 'SECTION:' and row[1] == 'results':
        in_data = True
        continue

    # Not in the data section.
    if not in_data:
        continue

    # The header line.
    if row[0] == 'Peak name':
        continue

    # The values.
    data[index][2] = float(row[3])
    data[index][3] = float(row[4])
    data[index][4] = float(row[5])

    # Increment the residue index.
    index += 1

r1 = []
r1_err = []
print("%-4s %-3s %-15s %-15s %-15s %-15s" % ('Name', 'Num', 'r1', 'err', 'r1_relax_ratio', 'err_relax_ratio'))
for i in range(len(data)):
    r1.append(1.0/data[i][2])
    r1_err.append((data[i][3] / data[i][4]) / data[i][2]**2)

    print("%-4s %-3s %15.10f %15.10f %15.10f %15.10f" % (data[i][0], data[i][1], r1[-1], r1_err[-1], r1[-1]/data[i][5], r1_err[-1]/data[i][6]))

print("\nr1 = %s" % r1)
print("\nr1_err = %s" % r1_err)
