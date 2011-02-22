#! /usr/bin/env python

from string import split, strip


# The file data.
file = open('testT1.txt')
lines = file.readlines()
file.close()

# The data - PDC T2, PDC T2 err, PDC scale factor, relax R2, relax R2 err (MC sim).
data = [
['Gln',  2, None, None, None,   2.19316607131,      0.0172386232908],
['Ile',  3, None, None, None,   2.33164219228,      0.0183443518519],
['Phe',  4, None, None, None,   2.34788508606,      0.0227955267542],
['Val',  5, None, None, None,   2.24886599821,      0.0180795406122],
['Lys',  6, None, None, None,    2.2789525024,      0.0177354763781],
['Thr',  7, None, None, None,   2.22003945867,      0.0163679694532],
['Leu',  8, None, None, None,   2.23951642467,      0.0254750354788],
['Thr',  9, None, None, None,   1.96777788367,      0.0352544464578],
['Gly', 10, None, None, None,    2.0875684322,      0.0153654041759],
['Lys', 11, None, None, None,   1.99730182405,       0.014531283342],
['Thr', 12, None, None, None,   2.16405472266,      0.0209402415213],
['Ile', 13, None, None, None,   2.27243094345,      0.0224280509971],
['Thr', 14, None, None, None,     2.198955365,      0.0150508562139],
['Leu', 15, None, None, None,   2.27948967552,       0.020430891379],
['Glu', 16, None, None, None,   2.08655000221,      0.0131497725671],
['Val', 17, None, None, None,   2.28438611675,      0.0171771915344],
['Glu', 18, None, None, None,    2.1078996481,       0.018674617039],
['Ser', 20, None, None, None,   2.24272715306,      0.0161431258325],
['Asp', 21, None, None, None,   2.34943133581,       0.013312575129],
['Thr', 22, None, None, None,   2.27465897388,      0.0207786570301],
['Ile', 23, None, None, None,   2.46663406087,       0.025490168883],
['Asn', 25, None, None, None,    2.3952903664,      0.0209840658917],
['Val', 26, None, None, None,   2.13289047641,      0.0134131139162],
['Lys', 27, None, None, None,   2.36225502002,      0.0235723466988],
['Ala', 28, None, None, None,   2.38482408468,      0.0193876962877],
['Lys', 29, None, None, None,   2.32669819269,      0.0211757913963],
['Thr', 30, None, None, None,   2.42006170148,      0.0183969142864],
['Gln', 31, None, None, None,   2.37188620597,      0.0171081419383],
['Asp', 32, None, None, None,    2.3427764194,      0.0166107892189],
['Lys', 33, None, None, None,   2.19297823605,      0.0147985959213],
['Glu', 34, None, None, None,   2.23811997028,      0.0161833329565],
['Gly', 35, None, None, None,   2.24602961229,      0.0132501633342],
['Ile', 36, None, None, None,   1.99065803361,      0.0119371117784],
['Asp', 39, None, None, None,   2.29367747495,      0.0146207658709],
['Gln', 40, None, None, None,   2.25468879195,      0.0175586127238],
['Gln', 41, None, None, None,    2.2243295406,      0.0213827058018],
['Arg', 42, None, None, None,    2.2796886728,      0.0246653917801],
['Leu', 43, None, None, None,    2.1724471962,      0.0277957833136],
['Ile', 44, None, None, None,   2.27921078025,      0.0238295262781],
['Phe', 45, None, None, None,   2.26626119216,      0.0258171858396],
['Ala', 46, None, None, None,   2.17184851821,      0.0564957968913],
['Gly', 47, None, None, None,   2.19128895435,      0.0171506431363],
['Lys', 48, None, None, None,   2.20111526618,      0.0170114668684],
['Gln', 49, None, None, None,   2.11389708191,      0.0156773151423],
['Leu', 50, None, None, None,   2.24429960044,      0.0231432887694],
['Glu', 51, None, None, None,   2.13354406803,      0.0215361108792],
['Asp', 52, None, None, None,   2.04571765737,      0.0160131880118],
['Arg', 54, None, None, None,    2.1917972293,      0.0202281839803],
['Thr', 55, None, None, None,   2.27484080671,      0.0252626224367],
['Leu', 56, None, None, None,   2.36904770093,      0.0201953638757],
['Ser', 57, None, None, None,   2.29802420383,      0.0149972198301],
['Asp', 58, None, None, None,   2.37716007771,      0.0188528192903],
['Tyr', 59, None, None, None,   2.22585681778,      0.0172777140575],
['Asn', 60, None, None, None,   2.28458371582,      0.0138771252559],
['Ile', 61, None, None, None,   2.34178470333,      0.0203630099596],
['Gln', 62, None, None, None,   1.97357442512,      0.0148163922994],
['Lys', 63, None, None, None,   2.16487344406,      0.0103478884037],
['Glu', 64, None, None, None,   2.31904426632,      0.0219686576237],
['Ser', 65, None, None, None,   2.18920681077,      0.0168659713768],
['Thr', 66, None, None, None,   2.18126161816,      0.0176501602926],
['Leu', 67, None, None, None,   2.26758959961,      0.0222025938212],
['His', 68, None, None, None,    2.2462367181,      0.0233778502267],
['Leu', 69, None, None, None,   2.24855138308,       0.017041910335],
['Val', 70, None, None, None,   2.31530066738,      0.0234394434209],
['Leu', 71, None, None, None,    2.1755953862,      0.0165496117566],
['Arg', 72, None, None, None,    2.1635257801,      0.0134432394378],
['Leu', 73, None, None, None,   1.85653927832,      0.0111980399019],
['Arg', 74, None, None, None,   1.61202380006,      0.0132121863859],
['Gly', 75, None, None, None,   1.16222624543,      0.0148261890535],
['Gly', 76, None, None, None,  0.763152015796,     0.00359679040075]]

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
