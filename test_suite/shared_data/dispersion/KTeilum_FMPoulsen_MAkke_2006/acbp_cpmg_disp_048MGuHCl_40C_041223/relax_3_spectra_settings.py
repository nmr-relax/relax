# Loop over the spectra settings.
ncycfile=open('ncyc.txt', 'r')

# Make empty ncyclist
ncyclist = []

i = 0
for line in ncycfile:
    ncyc = line.split()[0]
    time_T2 = float(line.split()[1])
    vcpmg = line.split()[2]
    set_sfrq = float(line.split()[3])
    rmsd_err = float(line.split()[4])

    # Test if spectrum is a reference
    if float(vcpmg) == 0.0:
        vcpmg = None
    else:
        vcpmg = round(float(vcpmg), 3)

    # Add ncyc to list
    ncyclist.append(int(ncyc))

    # Set the current spectrum id
    current_id = "Z_A%s"%(i)

    # Set the current experiment type.
    relax_disp.exp_type(spectrum_id=current_id, exp_type='CPMG')

    # Set the peak intensity errors, as defined as the baseplane RMSD.
    spectrum.baseplane_rmsd(error=rmsd_err, spectrum_id=current_id)

    # Set the NMR field strength of the spectrum.
    spectrometer.frequency(id=current_id, frq=set_sfrq, units='MHz')

    # Relaxation dispersion CPMG constant time delay T (in s).
    relax_disp.relax_time(spectrum_id=current_id, time=time_T2)

    # Set the relaxation dispersion CPMG frequencies.
    relax_disp.cpmg_frq(spectrum_id=current_id, cpmg_frq=vcpmg)

    i += 1

# Specify the duplicated spectra.
#spectrum.replicated(spectrum_ids=['Z_A1', 'Z_A15'])

# Delete replicate spectrum
spectrum.delete('Z_A15')
