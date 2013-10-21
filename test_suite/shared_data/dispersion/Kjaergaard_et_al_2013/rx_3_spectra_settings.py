# Set settings for experiment
import os

spin_locks = [0.0, 500.0, 1000.0, 2000.0, 5000.0, 10000.0]
lock_powers = [35.0, 39.0, 41.0, 43.0, 46.0, 48.0]
ncycs = [0, 4, 10, 14, 20, 40]

# Load the experiments settings file.
expfile = open('exp_parameters_sort.txt','r')
expfileslines = expfile.readlines()
fpipe = open('pipe_names_rx.txt','w')

for spin_lock in spin_locks:
    for lock_power in lock_powers:
        for i in range(len(expfileslines)):
            line=expfileslines[i]
            if line[0] == "#":
                continue
            else:
                # DIRN I deltadof2 dpwr2slock ncyc trim ss sfrq
                DIRN = line.split()[0]
                I = int(line.split()[1])
                deltadof2 = float(line.split()[2])
                dpwr2slock = float(line.split()[3])
                ncyc = int(line.split()[4])
                trim = float(line.split()[5])
                ss = int(line.split()[6])
                set_sfrq = float(line.split()[7])

                # Calculate spin_lock time
                time_sl = 2*ncyc*trim

                # Define file name for peak list.
                FNAME = "%s_%s_%s_%s_max_standard.ser"%(I, int(deltadof2), int(dpwr2slock), ncyc)
                sp_id = "%s_%s_%s_%s"%(I, int(deltadof2), int(dpwr2slock), ncyc)

                if deltadof2 == spin_lock and dpwr2slock == lock_power and ncyc == ncycs[0]:
                    pipename = "%s_%s"%(int(deltadof2), int(dpwr2slock))
                    pipebundle = 'relax_fit'
                    pipe.copy(pipe_from='base pipe', pipe_to=pipename, bundle_to=pipebundle)
                    pipe.switch(pipe_name=pipename)
                    fpipe.write("%s %s"%(pipename, pipebundle)+"\n")

                #print spin_lock, deltadof2, lock_power, dpwr2slock
                if deltadof2 == spin_lock and dpwr2slock == lock_power:
                    # Load the peak intensities (first the backbone NH, then the tryptophan indole NH).
                    spectrum.read_intensities(file=FNAME, dir=os.path.join(os.getcwd(),"peak_lists"), spectrum_id=sp_id, int_method='height')

                    # Set the relaxation times.
                    relax_fit.relax_time(time=time_sl, spectrum_id=sp_id)

                    # Set the peak intensity errors, as defined as the baseplane RMSD.
                    spectrum.baseplane_rmsd(error=1.33e+03, spectrum_id=sp_id)
                     

expfile.close()
fpipe.close()
    

