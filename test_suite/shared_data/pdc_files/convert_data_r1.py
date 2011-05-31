#! /usr/bin/env python

from string import split, strip


# The file data.
file = open('testT1.txt')
lines = file.readlines()
file.close()

# The data - PDC T2, PDC T2 err, PDC scale factor, relax R2, relax R2 err (MC sim).
data = [
['Gln',  2, None, None, None,    2.1931543671,      0.0150953094197],
['Ile',  3, None, None, None,   2.33146407173,      0.0160577446857],
['Phe',  4, None, None, None,    2.3482964848,       0.019713488727],
['Val',  5, None, None, None,    2.2490812645,      0.0164275028474],
['Lys',  6, None, None, None,   2.27941978889,       0.015118434456],
['Thr',  7, None, None, None,   2.21973220186,      0.0142724888389],
['Leu',  8, None, None, None,   2.24024670209,      0.0220723067644],
['Thr',  9, None, None, None,    1.9682398599,      0.0320202880659],
['Gly', 10, None, None, None,   2.08801972269,      0.0133512466715],
['Lys', 11, None, None, None,   1.99776427143,      0.0119683402446],
['Thr', 12, None, None, None,   2.16448623389,      0.0174891646325],
['Ile', 13, None, None, None,   2.27255388183,      0.0203045621019],
['Thr', 14, None, None, None,   2.19928611083,      0.0137179789481],
['Leu', 15, None, None, None,   2.27943290864,        0.01841703596],
['Glu', 16, None, None, None,   2.08711900135,      0.0110867843226],
['Val', 17, None, None, None,   2.28472626854,      0.0149813716965],
['Glu', 18, None, None, None,   2.10803348086,      0.0165871439247],
['Ser', 20, None, None, None,   2.24335721396,      0.0136423661701],
['Asp', 21, None, None, None,    2.3491468761,      0.0123466109271],
['Thr', 22, None, None, None,   2.27508355307,      0.0179254994426],
['Ile', 23, None, None, None,   2.46729511309,       0.022032166148],
['Asn', 25, None, None, None,   2.39562318634,      0.0182835550536],
['Val', 26, None, None, None,   2.13340147848,      0.0124491345714],
['Lys', 27, None, None, None,   2.36258684463,       0.021452496764],
['Ala', 28, None, None, None,   2.38480717279,      0.0167515948037],
['Lys', 29, None, None, None,   2.32696831127,      0.0186312168945],
['Thr', 30, None, None, None,   2.42063807895,       0.016486280768],
['Gln', 31, None, None, None,   2.37225963882,      0.0145645530678],
['Asp', 32, None, None, None,   2.34327154101,      0.0141218929004],
['Lys', 33, None, None, None,    2.1927627806,      0.0133120293255],
['Glu', 34, None, None, None,   2.23809535599,      0.0144347657445],
['Gly', 35, None, None, None,    2.2461346515,      0.0122274121117],
['Ile', 36, None, None, None,   1.99122925973,       0.010910732682],
['Asp', 39, None, None, None,   2.29368330103,      0.0126561091892],
['Gln', 40, None, None, None,   2.25464084772,      0.0146681195393],
['Gln', 41, None, None, None,   2.22441709558,      0.0180042863108],
['Arg', 42, None, None, None,   2.28040886598,      0.0226407473358],
['Leu', 43, None, None, None,   2.17231047053,      0.0237437949291],
['Ile', 44, None, None, None,   2.27954369008,      0.0201909508149],
['Phe', 45, None, None, None,   2.26618944243,      0.0208950941528],
['Ala', 46, None, None, None,   2.17293180472,      0.0496094013897],
['Gly', 47, None, None, None,   2.19171718851,      0.0143718164149],
['Lys', 48, None, None, None,   2.20180904452,      0.0159731114836],
['Gln', 49, None, None, None,   2.11417079383,      0.0137897460469],
['Leu', 50, None, None, None,   2.24457803209,      0.0193730177104],
['Glu', 51, None, None, None,   2.13348726698,      0.0178416908891],
['Asp', 52, None, None, None,    2.0460014256,      0.0130027410002],
['Arg', 54, None, None, None,   2.19214984513,      0.0173101801326],
['Thr', 55, None, None, None,   2.27509231624,      0.0229093320248],
['Leu', 56, None, None, None,   2.36912374644,      0.0178696073777],
['Ser', 57, None, None, None,   2.29814984784,      0.0129737044328],
['Asp', 58, None, None, None,   2.37723175535,      0.0159530364094],
['Tyr', 59, None, None, None,   2.22560065336,      0.0147756564606],
['Asn', 60, None, None, None,   2.28460144064,      0.0121672447449],
['Ile', 61, None, None, None,   2.34228508004,      0.0180155615894],
['Gln', 62, None, None, None,   1.97375590837,      0.0127517602123],
['Lys', 63, None, None, None,   2.16513054478,     0.00997271942879],
['Glu', 64, None, None, None,   2.31915705344,      0.0199426460098],
['Ser', 65, None, None, None,   2.18919504068,      0.0149076372426],
['Thr', 66, None, None, None,    2.1815681959,      0.0155283232121],
['Leu', 67, None, None, None,   2.26786646063,      0.0200115697764],
['His', 68, None, None, None,   2.24651038599,      0.0204872753534],
['Leu', 69, None, None, None,   2.24847954259,      0.0171435701978],
['Val', 70, None, None, None,   2.31549239579,      0.0204085987616],
['Leu', 71, None, None, None,   2.17566168322,      0.0141512899583],
['Arg', 72, None, None, None,    2.1637210197,      0.0124881076678],
['Leu', 73, None, None, None,   1.85663248042,     0.00972554000058],
['Arg', 74, None, None, None,   1.61255064461,      0.0109491376192],
['Gly', 75, None, None, None,   1.16260116356,      0.0127191083108],
['Gly', 76, None, None, None,  0.763062241201,     0.00312485609259]]

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
