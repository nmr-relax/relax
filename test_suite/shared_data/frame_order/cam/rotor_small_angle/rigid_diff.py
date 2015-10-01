from lib.io import extract_data


# Print formats.
format_pcs = "%10s%10s%10s%10s%10s%20.15f"
format_rdc = "%15s%15s%20.15f"

# Maximum differences.
max_pcs = 0.0
max_rdc = 0.0

# Loop over the tensors.
tensors = ['dy', 'tb', 'tm', 'er']
for tensor in tensors:
    # Print out.
    print("\n\nAlignment %s.\n" % tensor)

    # The PCS file name.
    file = "pcs_%s.txt" % tensor

    # Process the PCS.
    pcs_rigid = extract_data(file=file, dir='../rigid')
    pcs_moving = extract_data(file=file, dir='.')

    # Calculate the PCS differences.
    print("# %8s%10s%10s%10s%10s%20s" % (pcs_moving[0][1], pcs_moving[0][2], pcs_moving[0][3], pcs_moving[0][4], pcs_moving[0][5], "PCS difference"))
    for i in range(1, len(pcs_moving)):
        # The difference.
        diff = float(pcs_rigid[i+1][5]) - float(pcs_moving[i][5])

        # Printout.
        print(format_pcs % (pcs_moving[i][0], pcs_moving[i][1], pcs_moving[i][2], pcs_moving[i][3], pcs_moving[i][4], diff))

        # Store the maximum.
        if abs(diff) > max_pcs:
            max_pcs = abs(diff)

    # The RDC file name.
    file = "rdc_%s.txt" % tensor

    # Process the PCS.
    rdc_rigid = extract_data(file=file, dir='../rigid')
    rdc_moving = extract_data(file=file, dir='.')

    # Printout.
    print("# %13s%15s%20s" % (rdc_moving[0][1], rdc_moving[0][2], "RDC difference"))
    for i in range(1, len(rdc_moving)):
        # The difference.
        diff = float(rdc_rigid[i][2]) - float(rdc_moving[i][2])

        # Printout.
        print(format_rdc % (rdc_moving[i][0], rdc_moving[i][1], diff))

        # Store the maximum.
        if abs(diff) > max_rdc:
            max_rdc = abs(diff)

# Final printout.
print("\n\n")
print("Maximum PCS difference:  %.15f ppm." % max_pcs)
print("Maximum RDC difference:  %.15f Hz." % max_rdc)
