#! /usr/bin/perl -w

# modelfree.pl   v1.1            31 August 2001        Edward d'Auvergne
#
# Script to process all modelfree input and output.  The file parameters.pm is required in
# the current working directory to specify the parameters to be used for the specific
# calculation.
#
#
# Input data is specified in the file "input". An example of the format of the file is:
#
#	$ cat ./input
#	NMR_frq_label 600
#	NMR_frq       599.741
#	R1            R1.600.out
#	R2            R2.600.out
#	NOE           noe.600.out
#	
#	NMR_frq_label 500
#	NMR_frq       500.241
#	R1            R1.500.out
#	R2            R2.500.out
#	NOE           noe.500.out
#
#
# The script is divided into the three stages of model selection:
#
#	Stage 1:   Initial run of all models 1 to 5 and f-tests between them.
#		The initial modelfree input files for each run is created and put into the
#		directories "m1", "m2", "m3", "m4", "m5", "f-m1m2", "f-m1m3", etc.
#	Stage 2:   Model selection and creation of the final optimization run.
#		The modelfree input files for optimization are placed into the directory
#		"optimize".
#	           Optional use of hand selected models. The file "hand.selection" will be read,
#		and the residue number and model number will be extracted from the first and second
#		columns. The final optimization run will be created.
#	Stage 3:   Extraction of optimized data.
#
#
# Load parameters:

use parameters;


# Start of script.
##################

&ask_stage;                                         # Ask for stage 1, 2, or 3.
&open_universal_files;                              # Open the log and raw data files.
$num_frq = 0;                                       # The number of spectrometer frequencies.
$n = 0;                                             # The number of raw data sets.
while ( <INPUT> ) {
	&input_data;                                # Open the "input" file.
	++$num_frq;
}
&num_data_sets;                                     # Count the number of data sets.
print "\n[ Raw Data Extraction ]\n";
foreach $n ( 0 .. $#input ) {
	($NMR_frq_label, $data_type) = split(' ',$input[$n]);
	&raw_data;                                  # Extract the raw data.
}
@models = ("m1", "m2", "m3", "m4", "m5", "f-m1m2", "f-m1m3");
if ( $num_data_sets > 3 ) {                         # ie degrees of freedom > 0 in all models.
	push (@models, "f-m2m4", "f-m2m5", "f-m3m4");
	#push (@models, "f-m1m4", "f-m1m5", "f-m2m4", "f-m2m5", "f-m3m4");
}
if ( $stage == 1 ) {
	print "\n[ File Creation ]\n";
	for $model ( @models ) {
		if ( $model =~ /^m/ ) {             # Models 1 to 5.
			print "Creating input files for model $model\n";
		} else {
			print "Creating input files for F-test $model\n";
		}
		print $log_fh "\n<<< Model $model >>>\n";
		&mkdir($model);                     # Make the directory for the models.
		&open_mfiles($model);               # Open the model specific files.
		&model_flags($model);               # Update the model flags for the current model.
		&log_param;                         # Put the parameter data structures into the log file.
		for $res ( 0 .. $total_res ) {      # Loop for all residues.
			&mfdata;                    # Create the Modelfree input file mfdata.
			&mfpar;                     # Create the Modelfree input file mfpar.
			if ( $model =~ /^m/ ) {     # Models 1 to 5.
				&mod1;              # Create the md1 section of mfmodel.
			} else {                    # F-test runs.
				&mod1;              # Create the md1 section of mfmodel.
				&mod2;              # Create the md2 section of mfmodel.
			}
		}
		&mfin;                              # Create the mfin file.
		&run($model);                       # Create the run file.
		&close_mfiles;                      # Close the model specific files.
	}
	print "\n[ End of Stage 1 ]\n\n";
}
if ( $stage == 2 ) {
	&open_stage2_files;                 # Open the files used in stage 2.
	print "\n[ Modelfree Data Extraction ]\n";
	for $model ( @models ) {
		@row = ();                          # Empty the @row array.
		# &model_flags($model);               # Update the model flags for the current model.
		if ( -e "$model/mfout" ) {
			open(MFOUT, "$model/mfout");
		} else {
			die "The file \"$model/mfout\" does not exist, quitting script.\n\n";
		}
		if ( $model =~ /^m/ ) {
			print "Extracting modelfree data from $model/mfout.";
			local $^W = 0;              # Turn off the warning for undef in the if loop.
			foreach $n ( 0 .. $#input ) {
				($NMR_frq_label, $data_type) = split(' ',$input[$n]);
				&orig_data;         # Extract the original data.
			}
			&s2;                        # Extract the S2 data.
			&s2f;                       # Extract the S2f data.
			&s2s;                       # Extract the S2s data.
			&te;                        # Extract the te data.
			&rex;                       # Extract the Rex data.
			&sse;                       # Extract the SSE data.
			print "      [ OK ]\n";
		}
		if ( $model =~ /^f/ ) {
			print "Extracting f-test data from $model/mfout.";
			local $^W = 0;              # Turn off the warning for undef in the if loop.
			&ftest;                     # Extract the ftest data.
			print "     [ OK ]\n";
		}
		close(MFOUT);
	}
	print "\n[ Model Selection ]\n";
	if ( $selection =~ "Palmer" ) {
		print "Model selection set to \"Palmer\"\n";
		if ( $num_data_sets > 3 ) {         # ie degrees of freedom > 0 in all models.
			print DLOG "Full model selection.\n\n";
			print "The number of data sets is greater than 3, \n";
			print "\tie the degrees of freedom is greater than 0 in the most complicated models\n";
			print "\tDoing \"full model selection\" with f-tests between all models.\n";
			&full_model_select;         # Do the model selection and create a 2D data structure.
		} else {
			print DLOG "Reduced model selection.\n\n";
			print "The number of data sets is equal to 3.\n";
			print "\tie the degrees of freedom is equal to 0 in the most complicated models\n";
			print "\tDoing the reduced model selection of Palmer.\n";
			&reduced_model_select;      # Do the model selection and create a 2D data structure.
		}
	} elsif ( $selection =~ "F-test" ) {
		print DLOG "F-test based model selection.\n\n";
		print "Model selection set to \"F-test\"\n";
		&ftest_model_select;        # Do the F-test based model selection.
	} elsif ( $selection =~ "AIC" ) {
		print DLOG "AIC model selection.\n\n";
		print "Model selection set to \"AIC\"\n";
		&aic_model_select;        # Do AIC model selection.
	} elsif ( $selection =~ "BIC" ) {
		print DLOG "BIC model selection.\n\n";
		print "Model selection set to \"BIC\"\n";
		&bic_model_select;        # Do BIC model selection.
	} elsif ( $selection =~ "Hand" ) {
		print DLOG "Hand model selection.\n\n";
		print "\n[ Extraction of Models from \"hand.selection\" ]\n";
		print "Model selection done by hand.\n";
		&extract_handsel;                   # Extract the model for each residue.
	} else {
		die "No model selection specified.  Killing script!\n\n";
	}
	&results;                                   # Create the output file ./results.stage2.
	print "\n[ Grace File Creation ]\n";
	&grace;                                     # Create grace files for the results.
	print "\n[ Placing Data Structures into \"data.str.stage$stage\" ]\n";
	&print_data;                                # Place the whole 3D %data data structure into the file "data.str.stage$stage".
	print "\n[ Final Optimization Input Files ]\n";
	# Final optimization.
	&open_mfiles("optimize");                   # Open the model specific files.
	&mfin;                                      # Create the mfin file.
	for $res ( 0 .. $total_res ) {
		if ( $results[$res]{model} eq "0" ) {
			$opt_model = "none";
		} elsif ( $results[$res]{model} =~ /2+3/ || $results[$res]{model} =~ /4+5/ ) {
			$opt_model = "none";
		} elsif ( $results[$res]{model} =~ /1./ ) {
			$opt_model = "m1";
		} else {
			$opt_model = "m" . $results[$res]{model};
		}
		&model_flags($opt_model);           # Update the model flags for the current model.
		&mfdata;                            # Create the mfdata file.
		&mfpar;                             # Create the mfpar file.
		&mod1;                              # Create the mfmodel file.
	}
	&run("optimize");                           # Create the run file.
	print "Finished\n\n";
	&close_mfiles;                              # Close the model specific files.
	&close_stage_files;                         # Close the files used in stage 2 and 3.
	print "\n[ End of Stage 2 ]\n\n";
}
if ( $stage == 3 ) {
	&open_stage3_files;                         # Open the files used in stage 3.
	print "\n[ Extraction of Models from \"results.stage2\" ]\n";
	&extract_models;                            # Extract the model for each residue from the stage 2 result file.
	print "\n[ Extraction of Optimized Modelfree Data ]\n";
	$model = "opt";
	local $^W = 0;                              # Turn off the warning for undef in the if loop.
	foreach $n ( 0 .. $#input ) {
		($NMR_frq_label, $data_type) = split(' ',$input[$n]);
		&orig_data;                         # Extract the original data.
	}
	&s2;                                        # Extract the S2 data.
	&s2f;                                       # Extract the S2f data.
	&s2s;                                       # Extract the S2s data.
	&te;                                        # Extract the te data.
	&rex;                                       # Extract the Rex data.
	&sse;                                       # Extract the SSE data.
	&final_results;                             # Create the final result data structure.
	&results;                                   # Create the output file ./results.final.
	print "\n[ Grace File Creation ]\n";
	&grace;                                     # Create grace files for the results.
	&close_stage_files;                         # Close the files used in stage 2 and 3.
	print "\n[ End of Stage 3 ]\n\n";
}
&close_universal_files;

################
# End of script.


# Ask for stage 1, 2, or 3.
sub ask_stage {
	print "\n[ Select the stage for Modelfree analysis ]\n\n";
	print "The stages are:\n";
	print "\tStage 1:   Initial run of all models 1 to 5 and f-tests between them.\n";
	print "\tStage 2:   Model selection and creation of the final optimization run.\n";
	print "\tStage 3:   Extraction of optimized data.\n\n";
	$stage = 0;
	until ( $stage == 1 || $stage == 2 || $stage == 3 ) {
		local $^W = 0;           # Turn off the warning for undef in the if loop.
		print "Chose the stage by inputting the number 1, 2, or 3.\n";
		print "=>   ";
		chop($stage = <STDIN>);
		print "Stage chosen is $stage.\n";
		if ( $stage != 1 && $stage != 2 && $stage != 3 ) {
			print "\nIncorrect choise, try again!\n\n";
			$stage = 0;
		}
	}
}

# Open the log and raw data files.
sub open_universal_files {
	$log_fh = "LOG" . $stage;
	$log_file = "log.stage" . $stage;
	open($log_fh, ">$log_file");
	print $log_fh "<<< Stage $stage of Modelfree analysis >>>\n\n\n";
	print $log_fh "The log filehandle is \"$log_fh\".\n";
	print $log_fh "The log file name is \"$log_file\".\n";
	open(INPUT, "input") || die "Input file \"input\" does not exist, quitting script!\n";
}

# Open the log and raw data files.
sub open_mfiles {
	open(MODEL, ">$_[0]/mfmodel");
	open(PAR, ">$_[0]/mfpar");
	open(DATA, ">$_[0]/mfdata");
	open(RUN, ">$_[0]/run");
	open(MFIN, ">$_[0]/mfin");
}

# Open the files used in stage 2.
sub open_stage2_files {
	if ( -e "optimize" ) {
		die "Directory ./optimize already exists, quitting script.\n";
	} else {
		system("mkdir optimize");
	}
	if ( -e "grace" ) {
		print "Directory ./grace already exists.\n";
		print $log_fh "Directory ./grace already exists.\n";
	} else {
		system("mkdir grace");
	}
	open(DLOG, ">data.str.stage2");
	open(RESULTS, ">results.stage2");
	open(S2AGR, ">grace/S2.stage2.agr");
	open(S2FAGR, ">grace/S2f.stage2.agr");
	open(S2SAGR, ">grace/S2s.stage2.agr");
	open(TEAGR, ">grace/te.stage2.agr");
	open(REXAGR, ">grace/Rex.stage2.agr");
	open(SSEAGR, ">grace/SSE.stage2.agr");
	if ( $selection =~ "Hand" ) {
		open(HAND, "hand.selection") || die "File \"hand.selection\" does not exist, quitting script!\n\n";
	}
}

# Open the files used in stage 3.
sub open_stage3_files {
	if ( -e "optimize/mfout" ) {
		open(MFOUT, "optimize/mfout");
	} else {
		die "The file \"optimize/mfout\" does not exist, quitting script.\n\n";
	}
	open(STAGE2_RESULTS, "results.stage2");
	open(RESULTS, ">results.final");
	open(S2AGR, ">grace/S2.final.agr");
	open(S2FAGR, ">grace/S2f.final.agr");
	open(S2SAGR, ">grace/S2s.final.agr");
	open(TEAGR, ">grace/te.final.agr");
	open(REXAGR, ">grace/Rex.final.agr");
	open(SSEAGR, ">grace/SSE.final.agr");
}

# Open the "input" file.
sub input_data {
	@row = split(' ',$_);
	until ( $row[0] eq "NMR_frq_label" ) {
		@row = split(' ',<INPUT>);
	}
	@row = split(' ',<INPUT>);             # Get the next line.
	$frq[$num_frq]{NMR_frq} = $row[0];     # Get the spectometer frequency.
	$frq[$num_frq]{NMR_frq_label} = $row[1];
	print $log_fh "NMR frequency => $frq[$num_frq]{NMR_frq}.\n";
	print "NMR frq $frq[$num_frq]{NMR_frq_label} MHz.\n";
	print $log_fh "NMR frequency label => $frq[$num_frq]{NMR_frq_label}.\n";
	print "\nNMR frq label $frq[$num_frq]{NMR_frq_label}.\n";
	while ( <INPUT> ) {
		local $^W = 0;                 # Turn off the warning for undef in the if loop.
		@row = split(' ',$_);
		if ( $row[0] eq "" ) {
			last;                  # Stop at the new line.
		}
		$input[$n] = $frq[$num_frq]{NMR_frq_label} . " " . $row[0];
		$data_fh = $row[0] . "_" . $frq[$num_frq]{NMR_frq_label};
		$data_file = $row[1];
		print $log_fh "\tData type \"$row[0]\", ";
		print $log_fh "filehandle is \"$data_fh\", ";
		print $log_fh "and file is \"$data_file\".\n";
		print "\t$row[0] => $data_file\n";
		open($data_fh, "$data_file") || die "Cannot open \"$data_file\".\n";
		++$n;
	}
}

# Create the data info.
sub create_data_info {
	$data_lowercase = $_[0];
	$data_lowercase =~ tr/A-Z/a-z/;
	$data_fh = $_[0] . "_" . $_[1];
	$data_label = $data_lowercase . "_" . $_[1];
	$data_err_label = $data_lowercase . "_err_" . $_[1]; 
	$data_fit_label = $data_lowercase . "_fit_" . $_[1];
	$data_SSE_label = $data_lowercase . "_SSE_" . $_[1];
}

# Count the number of data sets.
sub num_data_sets {
	$num_data_sets = 0;
	foreach $n ( 0 .. $#input ) {
		++$num_data_sets;
	}	
	print "\nThe number of data sets is $num_data_sets.\n\n";
	print $log_fh "The number of data sets is $num_data_sets.\n\n";
	if ( $num_data_sets < 3 ) {
		die "The number of data sets needs to be equal to, or greater than 3.\n\n";
	}
}

# Extract the raw data.
sub raw_data {
	print "Extracting the $NMR_frq_label MHz $data_type data\n";
	print $log_fh "\n\n<<< Extracting the $NMR_frq_label MHz $data_type data >>>\n";
	&create_data_info($data_type,$NMR_frq_label);     # Create the data info.
	$res = 0;
	while ( <$data_fh> ) {
		@row = split(' ',$_);
		if ( $row[0] eq "No" ) {    # Skip the title line.
			@row = split(' ',<$data_fh>);
		}
		if ( $n == 0 ) {
			$raw_data[$res]{resNo}   = $row[0];
			$raw_data[$res]{resName} = $row[1];
		}
		if ( $n >= 1 ) {
			&rawdata_lineup;         # Make sure all lines are from the same residue.
		}
		$raw_data[$res]{$data_label}     = $row[2];
		$raw_data[$res]{$data_err_label} = $row[3];
		print $log_fh "Residue $res, Seq no $row[0], Name $row[1].\n";
		++$res;
	}
	$total_res = $res - 1;   # Save the number of residues into $total_res.
}

# Make sure all lines are from the same residue.
sub rawdata_lineup {
	if ( $row[0] != $raw_data[$res]{resNo} ) {
		print "Bad lineup. $NMR_frq_label MHz $data_type data.\n\tres $row[0] != $raw_data[$res]{resNo}\n";
		print "Check that all data sets have the same residues.\n";
		print "Quitting script!\n";
		die "\n";
	}
} 

# Make the directory for the model.
sub mkdir {
	print $log_fh "Making dir $_[0]\n";
	mkdir("$_[0]",0777) || die "Directory ./$_[0] already exists, quitting script.\n";
}

# Update the model flags for the current model.
sub model_flags {
	# Reset flags.
	$md1{tloc}{flag} = 0;
	$md1{theta}{flag} = 0;
	$md1{sf2}{flag} = 0;
	$md1{ss2}{flag} = 0;
	$md1{te}{flag}  = 0;
	$md1{rex}{flag}  = 0;
	foreach $param ( keys %md1 ) {     # Give %md2 all the values of %md1.
		for $val ( keys %{ $md1{$param} } ) {
			$md2{$param}{$val} = $md1{$param}{$val};
		}
	}
	if ( $_[0] =~ /^m1/ ) {
		$md1{ss2}{flag} = 1;
	}
	if ( $_[0] =~ /^m2/ ) {
		$md1{ss2}{flag} = 1;
		$md1{te}{flag}  = 1;
	}
	if ( $_[0] =~ /^m3/ ) {
		$md1{ss2}{flag} = 1;
		$md1{rex}{flag} = 1;
	}
	if ( $_[0] =~ /^m4/ ) {
		$md1{ss2}{flag} = 1;
		$md1{te}{flag}  = 1;
		$md1{rex}{flag} = 1;
	}
	if ( $_[0] =~ /^m5/ ) {
		$md1{sf2}{flag} = 1;
		$md1{ss2}{flag} = 1;
		$md1{te}{flag}  = 1;
	}
	if ( $_[0] =~ /^f-m1m2/ ) {
		$md1{ss2}{flag} = 1;
		$md2{ss2}{flag} = 1;
		$md2{te}{flag}  = 1;
	}
	if ( $_[0] =~ /^f-m1m3/ ) {
		$md1{ss2}{flag} = 1;
		$md2{ss2}{flag} = 1;
		$md2{rex}{flag} = 1;
	}
	if ( $_[0] =~ /^f-m1m4/ ) {
		$md1{ss2}{flag} = 1;
		$md2{ss2}{flag} = 1;
		$md2{te}{flag}  = 1;
		$md2{rex}{flag} = 1;
	}
	if ( $_[0] =~ /^f-m1m5/ ) {
		$md1{ss2}{flag} = 1;
		$md2{ss2}{flag} = 1;
		$md2{sf2}{flag} = 1;
		$md2{te}{flag}  = 1;
	}
	if ( $_[0] =~ /^f-m2m4/ ) {
		$md1{ss2}{flag} = 1;
		$md1{te}{flag}  = 1;
		$md2{ss2}{flag} = 1;
		$md2{te}{flag}  = 1;
		$md2{rex}{flag} = 1;
	}
	if ( $_[0] =~ /^f-m3m4/ ) {
		$md1{ss2}{flag} = 1;
		$md1{rex}{flag} = 1;
		$md2{ss2}{flag} = 1;
		$md2{te}{flag}  = 1;
		$md2{rex}{flag} = 1;
	}
	if ( $_[0] =~ /^f-m2m5/ ) {
		$md1{ss2}{flag} = 1;
		$md1{te}{flag}  = 1;
		$md2{ss2}{flag} = 1;
		$md2{sf2}{flag} = 1;
		$md2{te}{flag}  = 1;
	}
}

# Put the parameter data structures into the log file.
sub log_param {
	print $log_fh "# md1 data structure\n";
	foreach $param ( sort keys %md1 ) {
		printf $log_fh "%-10s", "$param:";
		for $val ( sort keys %{ $md1{$param} } ) {
			print $log_fh "$val => $md1{$param}{$val}   ";
		}
		print $log_fh "\n";
	}
	print $log_fh "# md2 data structure\n";
	foreach $param ( sort keys %md2 ) {
		printf $log_fh "%-10s", "$param:";
		for $val ( sort keys %{ $md2{$param} } ) {
			printf $log_fh "$val => $md2{$param}{$val}   ";
		}
		print $log_fh "\n";
	}
}

# Create the Modelfree input file mfdata.
sub mfdata {
	print DATA "\nspin     $raw_data[$res]{resName}_$raw_data[$res]{resNo}\n";
	if ( $stage == 2 ) {
		if ( $opt_model =~ /none/ ) {
			$flag = 0;
		} else {
			$flag = 1;
		}
	} else {
		$flag = 1;
	}
	foreach $n ( 0 .. $#input ) {
		($NMR_frq_label, $data_type) = split(' ',$input[$n]);
		&create_data_info($data_type,$NMR_frq_label);     # Create the data info.
		printf DATA "%-7s%-10s%25s", $data_type, $NMR_frq_label, $raw_data[$res]{$data_label};
		printf DATA "%25s %-3s\n", $raw_data[$res]{$data_err_label}, $flag;
	}
}

# Create the Modelfree input file mfpar.
sub mfpar {
	print PAR "\nspin     $raw_data[$res]{resName}_$raw_data[$res]{resNo}\n";
	# Constants.
	printf PAR "%-14s%-6s%-7s", "constants", $raw_data[$res]{resNo}, $const{nucleus};
	printf PAR "%-8s%-8s%-8s\n", $const{gamma}, $const{rxh}, $const{csa};
	# Vector.
	printf PAR "%-10s%-4s%-4s\n", "vector", $vector{atom1}, $vector{atom2};
}

# Create the md1 section of mfmodel.
sub mod1 {
	print MODEL "\nspin     $raw_data[$res]{resName}_$raw_data[$res]{resNo}\n";
	# tloc.
	printf MODEL "%-3s%-6s%-6s", M1, "tloc", $md1{tloc}{start};
	printf MODEL "%-4s%-2s%11s", $md1{tloc}{flag}, $md1{tloc}{bound}, $md1{tloc}{lower};
	printf MODEL "%12s %-4s\n", $md1{tloc}{upper}, $md1{tloc}{steps};
	# Theta.
	printf MODEL "%-3s%-6s%-6s", M1, "Theta", $md1{theta}{start};
	printf MODEL "%-4s%-2s%11s", $md1{theta}{flag}, $md1{theta}{bound}, $md1{theta}{lower};
	printf MODEL "%12s %-4s\n", $md1{theta}{upper}, $md1{theta}{steps};
	# Sf2.
	printf MODEL "%-3s%-6s%-6s", M1, "Sf2", $md1{sf2}{start};
	printf MODEL "%-4s%-2s%11s", $md1{sf2}{flag}, $md1{sf2}{bound}, $md1{sf2}{lower};
	printf MODEL "%12s %-4s\n", $md1{sf2}{upper}, $md1{sf2}{steps};
	# Ss2.
	printf MODEL "%-3s%-6s%-6s", M1, "Ss2", $md1{ss2}{start};
	printf MODEL "%-4s%-2s%11s", $md1{ss2}{flag}, $md1{ss2}{bound}, $md1{ss2}{lower};
	printf MODEL "%12s %-4s\n", $md1{ss2}{upper}, $md1{ss2}{steps};
	# te.
	printf MODEL "%-3s%-6s%-6s", M1, "te", $md1{te}{start};
	printf MODEL "%-4s%-2s%11s", $md1{te}{flag}, $md1{te}{bound}, $md1{te}{lower};
	printf MODEL "%12s %-4s\n", $md1{te}{upper}, $md1{te}{steps};
	# Rex.
	printf MODEL "%-3s%-6s%-6s", M1, "Rex", $md1{rex}{start};
	printf MODEL "%-4s%-2s%11s", $md1{rex}{flag}, $md1{rex}{bound}, $md1{rex}{lower};
	printf MODEL "%12s %-4s\n", $md1{rex}{upper}, $md1{rex}{steps};
}

# Create the md2 section of mfmodel.
sub mod2 {
	# tloc.
	printf MODEL "\n%-3s%-6s%-6s", M2, "tloc", $md2{tloc}{start};
	printf MODEL "%-4s%-2s%11s", $md2{tloc}{flag}, $md2{tloc}{bound}, $md2{tloc}{lower};
	printf MODEL "%12s %-4s\n", $md2{tloc}{upper}, $md2{tloc}{steps};
	# Theta.
	printf MODEL "%-3s%-6s%-6s", M2, "Theta", $md2{theta}{start};
	printf MODEL "%-4s%-2s%11s", $md2{theta}{flag}, $md2{theta}{bound}, $md2{theta}{lower};
	printf MODEL "%12s %-4s\n", $md2{theta}{upper}, $md2{theta}{steps};
	# Sf2.
	printf MODEL "%-3s%-6s%-6s", M2, "Sf2", $md2{sf2}{start};
	printf MODEL "%-4s%-2s%11s", $md2{sf2}{flag}, $md2{sf2}{bound}, $md2{sf2}{lower};
	printf MODEL "%12s %-4s\n", $md2{sf2}{upper}, $md2{sf2}{steps};
	# Ss2.
	printf MODEL "%-3s%-6s%-6s", M2, "Ss2", $md2{ss2}{start};
	printf MODEL "%-4s%-2s%11s", $md2{ss2}{flag}, $md2{ss2}{bound}, $md2{ss2}{lower};
	printf MODEL "%12s %-4s\n", $md2{ss2}{upper}, $md2{ss2}{steps};
	# te.
	printf MODEL "%-3s%-6s%-6s", M2, "te", $md2{te}{start};
	printf MODEL "%-4s%-2s%11s", $md2{te}{flag}, $md2{te}{bound}, $md2{te}{lower};
	printf MODEL "%12s %-4s\n", $md2{te}{upper}, $md2{te}{steps};
	# Rex.
	printf MODEL "%-3s%-6s%-6s", M2, "Rex", $md2{rex}{start};
	printf MODEL "%-4s%-2s%11s", $md2{rex}{flag}, $md2{rex}{bound}, $md2{rex}{lower};
	printf MODEL "%12s %-4s\n", $md2{rex}{upper}, $md2{rex}{steps};
}

# Create the mfin file.
sub mfin {
	$sel = "none";
	if ( $stage == 1 ) {
		$algorithm = "fix";
		$diffusion_search = "none";
		if ( $model =~ /^f/ ) {
			$sel = "ftest";
		}
	} elsif ( $stage == 2 ) {
		if ( $diff eq "isotropic" ) {
			$algorithm = "brent";
			$diffusion_search = "grid";
		} elsif ( $diff eq "axial" ) {
			$algorithm = "powell";
			$diffusion_search = "none";
		}
	}
	print MFIN "optimization    tval\n\n";
	print MFIN "seed            0\n\n";
	print MFIN "search          grid\n\n";
	print MFIN "diffusion       $diff $diffusion_search\n\n";
	print MFIN "algorithm       $algorithm\n\n";
	if ( $stage == 1 ) {
		#print MFIN "simulations     expr    $no_sim      $trim\n\n";
		print MFIN "simulations     pred    $no_sim      $trim\n\n";
	} elsif ( $stage == 2 ) {
		print MFIN "simulations     none\n\n";
	}
	print MFIN "selection       $sel\n\n";
	print MFIN "sim_algorithm   $algorithm\n\n";
	print MFIN "fields          $num_frq     ";
	foreach $n ( 0 .. $#frq ) {
		print MFIN "  $frq[$n]{NMR_frq_label}";
	}
	print MFIN "\n";
	printf MFIN "%-7s%14s%2s%3s", "tm", $tm{val}, $tm{flag}, $tm{bound};
	printf MFIN "%5s%6s%4s\n", $tm{lower}, $tm{upper}, $tm{steps};
	printf MFIN "%-7s%14s%2s%3s", "Dratio", $dratio{val}, $dratio{flag}, $dratio{bound};
	printf MFIN "%5s%6s%4s\n", $dratio{lower}, $dratio{upper}, $dratio{steps};
	printf MFIN "%-7s%14s%2s%3s", "Theta", $theta{val}, $theta{flag}, $theta{bound};
	printf MFIN "%5s%6s%4s\n", $theta{lower}, $theta{upper}, $theta{steps};
	printf MFIN "%-7s%14s%2s%3s", "Phi", $phi{val}, $phi{flag}, $phi{bound};
	printf MFIN "%5s%6s%4s\n", $phi{lower}, $phi{upper}, $phi{steps};
}

# Create the run file.
sub run {
	print RUN "# /bin/sh\n";
	print RUN "modelfree4 -i mfin -d mfdata -p mfpar ";
	if ( $diff eq "isotropic" ) {
		print RUN "-m mfmodel -o mfout -e out\n";
	} elsif ( $diff eq "axial" ) {
		# Copy the pdb file to the model directory so there are no problems with the *.rotate file already existing.
		system("cp $pdb_full $_[0]/.");
		print RUN "-m mfmodel -s $pdb_file -o mfout -e out\n";
	}
	chmod(0777,"$_[0]/run") || die "Can't chmod $_[0]/run\n";
}

# Extract the original data.
sub orig_data {
	if ( $data_type eq "NOE" ) {
		$units = "()";
	} else {
		$units = "(1/s)";
	}
	until ( $row[0] eq $data_type && $row[1] eq $units ) {     # Skip all lines until the data is reached.
		@row = split(' ',<MFOUT>);
	}
	$res = 0;                # Init residue count.
	print $log_fh "\n\n<<< Extracting $NMR_frq_label MHz $data_type values from $model/mfout >>>\n";
	while ( <MFOUT> ) {      # Loop until the end of the data.
		@row = split(' ',$_);
		&end;            # Check for the end of the data and terminate the loop.
		&create_data_info($data_type,$NMR_frq_label);    # Create the variables for the original data.
		$data{$model}[$res]{$data_label} = $row[1];
		if ( $row[2] == 0 ) {
			$row[2] = 0.0005;
		}
		$data{$model}[$res]{$data_err_label} = $row[2];
		$data{$model}[$res]{$data_fit_label} = $row[4];
		$data{$model}[$res]{$data_SSE_label} = ($row[4] - $row[1])**2 / $row[2]**2;
		print $log_fh "$model    Res $row[0], $data{$model}[$res]{$data_label}±";
		print $log_fh "$data{$model}[$res]{$data_err_label}, Fit $data{$model}[$res]{$data_fit_label}, ";
		print $log_fh "SSE $data{$model}[$res]{$data_SSE_label}.\n";
		++$res;
	}
}

# Extract the S2 data.
sub s2 {
	until ( $row[0] eq "S2" && $row[1] eq "()" ) {     # Skip all lines until the S2 data is reached.
		@row = split(' ',<MFOUT>);
	}
	$res = 0;                # Init residue count.
	print $log_fh "\n$model Extracting S2 values.\n";
	while ( <MFOUT> ) {      # Loop until the end of the S2 data.
		@row = split(' ',$_);
		&end;            # Check for the end of the data and terminate the loop.
		print $log_fh "$model    Res $row[0], $row[1]±$row[5].\n";
		$data{$model}[$res]{resNo} = $row[0];
		$data{$model}[$res]{S2} = $row[1];
		$data{$model}[$res]{S2_err} = $row[5];
		++$res;
	}
	$total_res = $res - 1;   # Save the number of residues - 1 into $total_res.
	print $log_fh "The total number of residues is $total_res + 1\n";
}

# Extract the S2f data.
sub s2f {
	until ( $row[0] eq "S2f" && $row[1] eq "()" ) {     # Goto the S2f data.
		@row = split(' ',<MFOUT>);
	}
	$res = 0;                # Init residue count.
	print $log_fh "\n$model Extracting S2f values.\n";
	while ( <MFOUT> ) {      # Loop until the end of the S2f data.
		@row = split(' ',$_);
		&end;            # Check for the end of the data and terminate the loop.
		&data_lineup;    # Check residue line up.
		print $log_fh "    Res $row[0], $row[1]±$row[5].\n";
		$data{$model}[$res]{S2f} = $row[1];
		$data{$model}[$res]{S2f_err} = $row[5];
		++$res;
	}
}

# Extract the S2s data.
sub s2s {
	until ( $row[0] eq "S2s" && $row[1] eq "()" ) {     # Goto the S2s data.
		@row = split(' ',<MFOUT>);
	}
	$res = 0;                # Init residue count.
	print $log_fh "\n$model Extracting S2s values.\n";
	while ( <MFOUT> ) {      # Loop until the end of the S2s data.
		@row = split(' ',$_);
		&end;            # Check for the end of the data and terminate the loop.
		&data_lineup;    # Check residue line up.
		print $log_fh "    Res $row[0], $row[1]±$row[5].\n";
		$data{$model}[$res]{S2s} = $row[1];
		$data{$model}[$res]{S2s_err} = $row[5];
		++$res;
	}
}

# Extract the te data.
sub te {
	until ( $row[0] eq "te" && $row[1] eq "(ps)" ) {    # Goto the te data.
		@row = split(' ',<MFOUT>);
	}
	$res = 0;                # Init residue count.
	print $log_fh "\n$model Extracting te values.\n";
	while ( <MFOUT> ) {      # Loop until the end of the te data.
		@row = split(' ',$_);
		&end;            # Check for the end of the data and terminate the loop.
		&data_lineup;    # Check residue line up.
		print $log_fh "    Res $row[0], $row[1]±$row[5].\n";
		$data{$model}[$res]{te} = $row[1];
		$data{$model}[$res]{te_err} = $row[5];
		++$res;
	}
}

# Extract the Rex data.
sub rex {
	until ( $row[0] eq "Rex" && $row[1] eq "(1/s)" ) {  # Goto the Rex data.
		@row = split(' ',<MFOUT>);
	}
	$res = 0;                # Init residue count.
	print $log_fh "\n$model Extracting Rex values.\n";
	while ( <MFOUT> ) {      # Loop until the end of the Rex data.
		@row = split(' ',$_);
		&end;            # Check for the end of the data and terminate the loop.
		&data_lineup;    # Check residue line up.
		print $log_fh "    Res $row[0], $row[1]±$row[5].\n";
		$data{$model}[$res]{Rex} = $row[1];
		$data{$model}[$res]{Rex_err} = $row[5];
		++$res;
	}
}

# Check residue line up.
sub data_lineup {
        if ( $row[0] != $data{$model}[$res]{resNo} ) {
                printf $log_fh "%-31s", "$model    Line up $row[0] != $data{$model}[$res]{resNo}  [failed],";
                die "Residues don't match!\n";     # Kill the script.
        } else {
                printf $log_fh "%-31s", "$model    Line up $row[0] = $data{$model}[$res]{resNo}  [OK],";
        }
}

# Extract the SSE data.
sub sse {
	until ( $row[0] eq "data_sse" ) {     # Goto the SSE data.
		@row = split(' ',<MFOUT>);
	}
	$res = 0;                             # Init residue count.
	print $log_fh "\n$model Extracting SSE values.\n";
	while ( <MFOUT> ) {                   # Loop until the end of the SSE data.
		@row = split(' ',$_);
		if ( $row[0] eq "" ) {
			next;                 # Skip blank lines.
		}
		if ( $row[0] eq "data_correlation_matrix" ) {
			last;                 # Check for the end of data_sse section and terminate the loop.
		}
		until ( $row[0] =~ $data{$model}[$res]{resNo} ) {     # Goto the residue data.
			@row = split(' ',<MFOUT>);
		}
		$data{$model}[$res]{SSE} = $row[1];            # Save the actual SSE value for the residue.
		printf $log_fh "%-28s", "$model Res $data{$model}[$res]{resNo}, SSE $data{$model}[$res]{SSE},";
		while ( <MFOUT> ) {           # Loop until the end of the simulated SSE values for the residue.
			@row = split(' ',$_);
			&end;                 # Check for the end of the data and terminate the loop.
			if ( $row[0] == $SSEtile ) {           # Find the SSE limit.
				$data{$model}[$res]{SSElim} = $row[1];
				printf $log_fh "%-31s", "\%ile $row[0], SSElim $data{$model}[$res]{SSElim}";
			}
		}
		if ( $data{$model}[$res]{SSE} <= $data{$model}[$res]{SSElim} ) {
			printf $log_fh "%-20s", "SSE chk [OK],";
			$data{$model}[$res]{SSElim_f} = 1;     # Under critical value.
		} else {
			printf $log_fh "%-20s", "SSE chk [failed],";
			$data{$model}[$res]{SSElim_f} = 0;     # Not under critical value.
		}
		if ( $data{$model}[$res]{SSE} >= $largeSSE ) {
			printf $log_fh "%-12s", "SSE > $largeSSE";
			$data{$model}[$res]{largeSSE} = 1;     # Large SSE.
		} else {
			printf $log_fh "%-12s", "SSE < $largeSSE";
			$data{$model}[$res]{largeSSE} = 0;     # Small SSE.
		}
		if ( $data{$model}[$res]{SSE} == 0 ) {
			printf $log_fh "%-12s", "SSE = 0";
			$data{$model}[$res]{zeroSSE} = 0;      # Zero SSE.
		} else {
			printf $log_fh "%-12s", "SSE ne 0";
			$data{$model}[$res]{zeroSSE} = 1;      # Non-zero SSE.
		}
		print $log_fh "\n";
		++$res;
	}
}

# Extract the ftest data.
sub ftest {
	$row[0] = "empty";
	until ( $row[0] eq "data_F_dist" ) {   # Goto the SSE data.
		@row = split(' ',<MFOUT>);
	}
	$res = 0;                              # Init residue count.
	print $log_fh "\n$model Extracting F-test values.\n";
	while ( <MFOUT> ) {                    # Loop until the end of the SSE data.
		@row = split(' ',$_);
		if ( $row[0] eq "" ) {
			next;                  # Skip blank lines.
		}
		until ( $row[0] =~ $data{m1}[$res]{resNo} ) {  # Goto the residue data.
			@row = split(' ',<MFOUT>);
		}
		$ftest{$model}[$res]{resNo} = $data{$model}[$res]{resNo};
		$ftest{$model}[$res]{fstat} = $row[1];         # Save the actual F-stat value for the residue.
		printf $log_fh "%-35s", "$model Res $ftest{$model}[$res]{resNo}, F-stat $ftest{$model}[$res]{fstat},";
		while ( <MFOUT> ) {            # Loop until the end of the simulated F-stat values for the residue.
			@row = split(' ',$_);
			&end;                  # Check for the end of the data and terminate the loop.
			if ( $row[0] == $Ftest_lim ) {         # Find the F-test limit.
				$ftest{$model}[$res]{fstatlim} = $row[1];
				printf $log_fh "%-38s", "\%ile $row[0], fstatlim $ftest{$model}[$res]{fstatlim}";
			}
		}
		if ( $ftest{$model}[$res]{fstatlim} > 1.5 && $ftest{$model}[$res]{fstat} > $ftest{$model}[$res]{fstatlim} ) {
			printf $log_fh "%-20s", "F-test [OK]";
			$ftest{$model}[$res]{ftest_f} = 1;     # Above critical value.
		} elsif ( $ftest{$model}[$res]{fstatlim} < 1.5 && $ftest{$model}[$res]{fstat} > 1.5 ) {
			printf $log_fh "%-20s", "F-test [OK]";
			$ftest{$model}[$res]{ftest_f} = 1;     # Above critical value.
		} elsif ( $ftest{$model}[$res]{fstatlim} > 5 && $ftest{$model}[$res]{fstat} > 1.5 ) {
			printf $log_fh "%-20s", "F-test [OK]";
			$ftest{$model}[$res]{ftest_f} = 1;     # Above critical value.
		} else {
			printf $log_fh "%-20s", "F-test [failed]";
			$ftest{$model}[$res]{ftest_f} = 0;     # Not above critical value.
		}
		print $log_fh "F-stat calculations\n";
		if ( $model =~ "f-m1m2" ) {
			$p1 = 5;
			$p2 = 4;
			$SSE1 = $data{"m1"}[$res]{SSE};
			$SSE2 = $data{"m2"}[$res]{SSE};
		} elsif ( $model =~ "f-m1m3" ) {
			$p1 = 5;
			$p2 = 4;
			$SSE1 = $data{"m1"}[$res]{SSE};
			$SSE2 = $data{"m3"}[$res]{SSE};
		} elsif ( $model =~ "f-m1m4" ) {
			$p1 = 5;
			$p2 = 3;
			$SSE1 = $data{"m1"}[$res]{SSE};
			$SSE2 = $data{"m4"}[$res]{SSE};
		} elsif ( $model =~ "f-m1m5" ) {
			$p1 = 5;
			$p2 = 3;
			$SSE1 = $data{"m1"}[$res]{SSE};
			$SSE2 = $data{"m5"}[$res]{SSE};
		} elsif ( $model =~ "f-m2m4" ) {
			$p1 = 4;
			$p2 = 3;
			$SSE1 = $data{"m2"}[$res]{SSE};
			$SSE2 = $data{"m4"}[$res]{SSE};
		} elsif ( $model =~ "f-m2m5" ) {
			$p1 = 4;
			$p2 = 3;
			$SSE1 = $data{"m2"}[$res]{SSE};
			$SSE2 = $data{"m5"}[$res]{SSE};
		} elsif ( $model =~ "f-m3m4" ) {
			$p1 = 4;
			$p2 = 3;
			$SSE1 = $data{"m3"}[$res]{SSE};
			$SSE2 = $data{"m4"}[$res]{SSE};
		}
		print $log_fh "\n";
		++$res;
	}
}

# Check for the end of the data and terminate the loop.
sub end {
	if ( $row[0] eq "stop_" ) {
		last;     # Stop the loop.
	}
}

# Do the model selection and create a 2D data structure.
sub full_model_select {
	print $log_fh "\n\n<<<Full Model Selection>>>";
	for $res ( 0 .. $total_res ) {                 # Loop from first to last residue.
		printf $log_fh "\n%-22s", "   Checking res $data{m1}[$res]{resNo}";
		$results[$res] = {
			resNo   => $data{m1}[$res]{resNo},
			model   => "",
			S2      => "",
			S2_err  => "",
			S2f     => "",
			S2f_err => "",
			S2s     => "",
			S2s_err => "",
			te      => "",
			te_err  => "",
			Rex     => "",
			Rex_err => "",
			SSE     => "",
		};
		# Model 1 test.
		if ( $data{m1}[$res]{SSElim_f} == 1 ) {
			printf $log_fh "%-12s", "[Model 1]";
			$results[$res]{model} = 1;
			$results[$res]{S2}      = $data{m1}[$res]{S2};
			$results[$res]{S2_err}  = $data{m1}[$res]{S2_err};
			$results[$res]{SSE}     = $data{m1}[$res]{SSE};
		}
		# Test if both model 2 and 3 fit!!! (Should not occur)
		elsif ( $data{m2}[$res]{SSElim_f} == 1 && $ftest{"f-m1m2"}[$res]{ftest_f} == 1
			&& $data{m3}[$res]{SSElim_f} ==  1 && $ftest{"f-m1m3"}[$res]{ftest_f} == 1 ) {
			printf $log_fh "%-12s", "[Model 2 and 3]";
			$results[$res]{model}   = "2+3";
		}
		# Model 2 test.
		elsif ( $data{m2}[$res]{SSElim_f} == 1 && $ftest{"f-m1m2"}[$res]{ftest_f} == 1 ) {
			printf $log_fh "%-12s", "[Model 2]";
			$results[$res]{model}   = 2;
			$results[$res]{S2}      = $data{m2}[$res]{S2};
			$results[$res]{S2_err}  = $data{m2}[$res]{S2_err};
			$results[$res]{te}      = $data{m2}[$res]{te};
			$results[$res]{te_err}  = $data{m2}[$res]{te_err};
			$results[$res]{SSE}     = $data{m2}[$res]{SSE};
		}
		# Model 3 test.
		elsif ( $data{m3}[$res]{SSElim_f} == 1  && $ftest{"f-m1m3"}[$res]{ftest_f} == 1 ) {
			printf $log_fh "%-12s", "[Model 3]";
			$results[$res]{model}   = 3;
			$results[$res]{S2}      = $data{m3}[$res]{S2};
			$results[$res]{S2_err}  = $data{m3}[$res]{S2_err};
			$results[$res]{Rex}     = $data{m3}[$res]{Rex};
			$results[$res]{Rex_err} = $data{m3}[$res]{Rex_err};
			$results[$res]{SSE}     = $data{m3}[$res]{SSE};
		}
		# Large SSE test for model 1.
		elsif ( $data{m1}[$res]{largeSSE} == 0 ) {
			printf $log_fh "%-12s", "[SSE < $largeSSE]";
			$results[$res]{model}   = "1*";
			$results[$res]{S2}      = $data{m1}[$res]{S2};
			$results[$res]{S2_err}  = $data{m1}[$res]{S2_err};
			$results[$res]{SSE}     = $data{m1}[$res]{SSE};
		}
		# Test if both model 4 and 5 fit!!! (Should not occur)
		elsif ( $data{m4}[$res]{SSElim_f} == 1 && $ftest{"f-m2m4"}[$res]{ftest_f} == 1
			&& $ftest{"f-m3m4"}[$res]{ftest_f} == 1
			&& $data{m5}[$res]{SSElim_f} == 1 && $ftest{"f-m2m5"}[$res]{ftest_f} == 1 ) {
			printf $log_fh "%-12s", "[Model 4 and 5]";
			$results[$res]{model}   = "4+5";
		}
		# Model 4 test.
		elsif ( $data{m4}[$res]{SSElim_f} == 1 && $ftest{"f-m2m4"}[$res]{ftest_f} == 1
			&& $ftest{"f-m3m4"}[$res]{ftest_f} == 1 ) {
			printf $log_fh "%-12s", "[Model 4]";
			$results[$res]{model}   = 4;
			$results[$res]{S2}      = $data{m4}[$res]{S2};
			$results[$res]{S2_err}  = $data{m4}[$res]{S2_err};
			$results[$res]{te}      = $data{m4}[$res]{te};
			$results[$res]{te_err}  = $data{m4}[$res]{te_err};
			$results[$res]{Rex}     = $data{m4}[$res]{Rex};
			$results[$res]{Rex_err} = $data{m4}[$res]{Rex_err};
			$results[$res]{SSE}     = $data{m4}[$res]{SSE};
		}
		# Model 5 test.
		elsif ( $data{m5}[$res]{SSElim_f} == 1 && $ftest{"f-m2m5"}[$res]{ftest_f} == 1 ) {
			printf $log_fh "%-12s", "[Model 5]";
			$results[$res]{model}   = 5;
			$results[$res]{S2}      = $data{m5}[$res]{S2};
			$results[$res]{S2_err}  = $data{m5}[$res]{S2_err};
			$results[$res]{S2f}     = $data{m5}[$res]{S2f};
			$results[$res]{S2f_err} = $data{m5}[$res]{S2f_err};
			$results[$res]{S2s}     = $data{m5}[$res]{S2s};
			$results[$res]{S2s_err} = $data{m5}[$res]{S2s_err};
			$results[$res]{te}      = $data{m5}[$res]{te};
			$results[$res]{te_err}  = $data{m5}[$res]{te_err};
			$results[$res]{SSE}     = $data{m5}[$res]{SSE};
		}
		# No model fits!
		else {
			printf $log_fh "%-12s", "[No Model]";
			$results[$res]{model}   = 0;
			$results[$res]{SSE}     = $data{m1}[$res]{SSE};
		}
	}
}

# Do the model selection and create a 2D data structure.
sub reduced_model_select {
	print $log_fh "\n\n<<<Reduced Model Selection>>>";
	for $res ( 0 .. $total_res ) {                 # Loop from first to last residue.
		printf $log_fh "\n%-22s", "   Checking res $data{m1}[$res]{resNo}";
		$results[$res] = {
			resNo   => $data{m1}[$res]{resNo},
			model   => "",
			S2      => "",
			S2_err  => "",
			S2f     => "",
			S2f_err => "",
			S2s     => "",
			S2s_err => "",
			te      => "",
			te_err  => "",
			Rex     => "",
			Rex_err => "",
			SSE     => "",
		};
		# Model 1 test.
		if ( $data{m1}[$res]{SSElim_f} == 1 ) {
			printf $log_fh "%-12s", "[Model 1]";
			$results[$res]{model}   = 1;
			$results[$res]{S2}      = $data{m1}[$res]{S2};
			$results[$res]{S2_err}  = $data{m1}[$res]{S2_err};
			$results[$res]{SSE}     = $data{m1}[$res]{SSE};
		}
		# Test if both model 2 and 3 fit!!! (Should not occur)
		elsif ( $data{m2}[$res]{SSElim_f}    == 1 && $ftest{"f-m1m2"}[$res]{ftest_f} == 1
			&& $data{m3}[$res]{SSElim_f} == 1 && $ftest{"f-m1m3"}[$res]{ftest_f} == 1 ) {
			printf $log_fh "%-12s", "[Model 2 and 3]";
			$results[$res]{model}   = "2+3";
		}
		# Model 2 test.
		elsif ( $data{m2}[$res]{SSElim_f} == 1 && $ftest{"f-m1m2"}[$res]{ftest_f} == 1 ) {
			printf $log_fh "%-12s", "[Model 2]";
			$results[$res]{model}   = 2;
			$results[$res]{S2}      = $data{m2}[$res]{S2};
			$results[$res]{S2_err}  = $data{m2}[$res]{S2_err};
			$results[$res]{te}      = $data{m2}[$res]{te};
			$results[$res]{te_err}  = $data{m2}[$res]{te_err};
			$results[$res]{SSE}     = $data{m2}[$res]{SSE};
		}
		# Model 3 test.
		elsif ( $data{m3}[$res]{SSElim_f} == 1 && $ftest{"f-m1m3"}[$res]{ftest_f} == 1 ) {
			printf $log_fh "%-12s", "[Model 3]";
			$results[$res]{model}   = 3;
			$results[$res]{S2}      = $data{m3}[$res]{S2};
			$results[$res]{S2_err}  = $data{m3}[$res]{S2_err};
			$results[$res]{Rex}     = $data{m3}[$res]{Rex};
			$results[$res]{Rex_err} = $data{m3}[$res]{Rex_err};
			$results[$res]{SSE}     = $data{m3}[$res]{SSE};
		}
		# Large SSE test for model 1.
		elsif ( $data{m1}[$res]{largeSSE} == 0 ) {
			printf $log_fh "%-12s", "[SSE < $largeSSE]";
			$results[$res]{model}   = "1*";
			$results[$res]{S2}      = $data{m1}[$res]{S2};
			$results[$res]{S2_err}  = $data{m1}[$res]{S2_err};
			$results[$res]{SSE}     = $data{m1}[$res]{SSE};
		}
		# Test if both model 4 and 5 fit!!! (Should not occur)
		elsif ( $data{m4}[$res]{zeroSSE} == 0 && $data{m5}[$res]{zeroSSE} == 0 ) {
			printf $log_fh "%-12s", "[Model 4 and 5]";
			$results[$res]{model}   = "4+5";
		}
		# Model 4 test.
		elsif ( $data{m4}[$res]{zeroSSE} == 0 ) {
			printf $log_fh "%-12s", "[Model 4]";
			$results[$res]{model}   = 4;
			$results[$res]{S2}      = $data{m4}[$res]{S2};
			$results[$res]{S2_err}  = $data{m4}[$res]{S2_err};
			$results[$res]{te}      = $data{m4}[$res]{te};
			$results[$res]{te_err}  = $data{m4}[$res]{te_err};
			$results[$res]{Rex}     = $data{m4}[$res]{Rex};
			$results[$res]{Rex_err} = $data{m4}[$res]{Rex_err};
			$results[$res]{SSE}     = $data{m4}[$res]{SSE};
		}
		# Model 5 test.
		elsif ( $data{m5}[$res]{zeroSSE} == 0 ) {
			printf $log_fh "%-12s", "[Model 5]";
			$results[$res]{model}   = 5;
			$results[$res]{S2}      = $data{m5}[$res]{S2};
			$results[$res]{S2_err}  = $data{m5}[$res]{S2_err};
			$results[$res]{S2f}     = $data{m5}[$res]{S2f};
			$results[$res]{S2f_err} = $data{m5}[$res]{S2f_err};
			$results[$res]{S2s}     = $data{m5}[$res]{S2s};
			$results[$res]{S2s_err} = $data{m5}[$res]{S2s_err};
			$results[$res]{te}      = $data{m5}[$res]{te};
			$results[$res]{te_err}  = $data{m5}[$res]{te_err};
			$results[$res]{SSE}     = $data{m5}[$res]{SSE};
		}
		# No model fits!
		else {
			printf $log_fh "%-12s", "[No Model]";
			$results[$res]{model}   = 0;
			$results[$res]{SSE}     = $data{m1}[$res]{SSE};
		}
	}
}

# Do the F-test based model selection.
sub ftest_model_select {
	print $log_fh "\n\n<<<F-test based Model Selection>>>";
	for $res ( 0 .. $total_res ) {                 # Loop from first to last residue.
		printf $log_fh "\n%-22s", "   Checking res $data{m1}[$res]{resNo}";

		### Set up.
		$results[$res] = {
			resNo   => $data{m1}[$res]{resNo},
			model   => "",
			S2      => "",
			S2_err  => "",
			S2f     => "",
			S2f_err => "",
			S2s     => "",
			S2s_err => "",
			te      => "",
			te_err  => "",
			Rex     => "",
			Rex_err => "",
			SSE     => "",
		};
		$select_model = 0;
		# F-stat.
		$fs_m1m2 = $ftest{"f-m1m2"}[$res]{fstat};
		$fs_m1m3 = $ftest{"f-m1m3"}[$res]{fstat};
		$fs_m1m4 = $ftest{"f-m1m4"}[$res]{fstat};
		$fs_m1m5 = $ftest{"f-m1m5"}[$res]{fstat};
		$fs_m2m3 = $ftest{"f-m2m3"}[$res]{fstat};
		$fs_m2m4 = $ftest{"f-m2m4"}[$res]{fstat};
		$fs_m3m4 = $ftest{"f-m3m4"}[$res]{fstat};
		# F-test results.
		$ft_m1m2 = $ftest{"f-m1m2"}[$res]{ftest_f};
		$ft_m1m3 = $ftest{"f-m1m3"}[$res]{ftest_f};
		$ft_m1m4 = $ftest{"f-m1m4"}[$res]{ftest_f};
		$ft_m1m5 = $ftest{"f-m1m5"}[$res]{ftest_f};
		$ft_m2m3 = $ftest{"f-m2m3"}[$res]{ftest_f};
		$ft_m2m4 = $ftest{"f-m2m4"}[$res]{ftest_f};
		$ft_m3m4 = $ftest{"f-m3m4"}[$res]{ftest_f};

		### Model selection.
		# Test if both f-m1m4 and f-m1m5 are accepted, and select the model using the highest F-stat.
		if ( $ft_m1m4 == 1 && $ft_m1m5 == 1 ) {
			if ( $fs_m1m4 > $fs_m1m5 ) {
				$select_model = 4;
			} elsif ( $fs_m1m4 < $fs_m1m5 ) {
				$select_model = 5;
			} else {
				$select_model = "4+5";
			}
		}
		# Test if model 4 is a significant improvement on model 1.
		elsif ( $ft_m1m4 == 1 ) {
			$select_model = 4;
		}
		# Test if model 5 is a significant improvement on model 1.
		elsif ( $ft_m1m5 == 1 ) {
			$select_model = 5;
		}
		# Test if both f-m1m2 and f-m1m3 are accepted, and find the highest F-stat.
		elsif ( $ft_m1m2 == 1 && $ft_m1m3 == 1 ) {
			# Model 2.
			if ( $fs_m1m2 > $fs_m1m3 ) {
				# Test if both f-m2m4 and f-m2m5 accepted.
				if ( $ft_m2m4 == 1 && $ft_m2m5 == 1 ) {
					if ( $fs_m2m4 > $fs_m2m5 ) {
						$select_model = 4;
					} elsif ( $fs_m2m4 < $fs_m2m5 ) {
						$select_model = 5;
					} else {
						$select_model = "4+5";
					}
				}
				# Test if model 4 is a significant improvement on model 2.
				elsif ( $ft_m2m4 == 1 ) {
					$select_model = 4;
				}
				# Test if model 5 is a significant improvement on model 2.
				elsif ( $ft_m2m5 == 1 ) {
					$select_model = 5;
				}
				# Model 2.
				else {
					$select_model = 2;
				}
			}
			# Model 3.
			elsif ( $fs_m1m2 < $fs_m1m3 ) {
				# Test if model 4 is a significant improvement on model 3.
				if ( $ft_m3m4 == 1 ) {
					$select_model = 4;
				}
				# Model 3.
				else {
					$select_model = 3;
				}
			} else {
				$select_model = "2+3";
			}
		}
		# Test if model 2 is a significant improvement on model 1.
		elsif ( $ft_m1m2 == 1 ) {
			# Test if both f-m2m4 and f-m2m5 accepted.
			if ( $ft_m2m4 == 1 && $ft_m2m5 == 1 ) {
				if ( $fs_m2m4 > $fs_m2m5 ) {
					$select_model = 4;
				} elsif ( $fs_m2m4 < $fs_m2m5 ) {
					$select_model = 5;
				} else {
					$select_model = "4+5";
				}
			}
			# Test if model 4 is a significant improvement on model 2.
			elsif ( $ft_m2m4 == 1 ) {
				$select_model = 4;
			}
			# Test if model 5 is a significant improvement on model 2.
			elsif ( $ft_m2m5 == 1 ) {
				$select_model = 5;
			}
			# Model 2.
			else {
				$select_model = 2;
			}
		}
		# Test if model 3 is a significant improvement on model 1.
		elsif ( $ft_m1m3 == 1 ) {
			# Test if model 4 is a significant improvement on model 3.
			if ( $ft_m3m4 == 1 ) {
				$select_model = 4;
			}
			# Model 3.
			else {
				$select_model = 3;
			}
		}
		# Fall back to model 1 if all F-test fail.
		else {
			$select_model = 1;
		}

		### Setting variables.
		if ( $select_model == 1 ) {
			printf $log_fh "%-12s", "[Model 1]";
			$results[$res]{model}   = 1;
			$results[$res]{S2}      = $data{m1}[$res]{S2};
			$results[$res]{S2_err}  = $data{m1}[$res]{S2_err};
			$results[$res]{SSE}     = $data{m1}[$res]{SSE};
		} elsif ( $select_model == 2 ) {
			printf $log_fh "%-12s", "[Model 2]";
			$results[$res]{model}   = 2;
			$results[$res]{S2}      = $data{m2}[$res]{S2};
			$results[$res]{S2_err}  = $data{m2}[$res]{S2_err};
			$results[$res]{te}      = $data{m2}[$res]{te};
			$results[$res]{te_err}  = $data{m2}[$res]{te_err};
			$results[$res]{SSE}     = $data{m2}[$res]{SSE};
		} elsif ( $select_model == 3 ) {
			printf $log_fh "%-12s", "[Model 3]";
			$results[$res]{model}   = 3;
			$results[$res]{S2}      = $data{m3}[$res]{S2};
			$results[$res]{S2_err}  = $data{m3}[$res]{S2_err};
			$results[$res]{Rex}     = $data{m3}[$res]{Rex};
			$results[$res]{Rex_err} = $data{m3}[$res]{Rex_err};
			$results[$res]{SSE}     = $data{m3}[$res]{SSE};
		} elsif ( $select_model == 4 ) {
			printf $log_fh "%-12s", "[Model 4]";
			$results[$res]{model}   = 4;
			$results[$res]{S2}      = $data{m4}[$res]{S2};
			$results[$res]{S2_err}  = $data{m4}[$res]{S2_err};
			$results[$res]{te}      = $data{m4}[$res]{te};
			$results[$res]{te_err}  = $data{m4}[$res]{te_err};
			$results[$res]{Rex}     = $data{m4}[$res]{Rex};
			$results[$res]{Rex_err} = $data{m4}[$res]{Rex_err};
			$results[$res]{SSE}     = $data{m4}[$res]{SSE};
		} elsif ( $select_model == 5 ) {
			printf $log_fh "%-12s", "[Model 5]";
			$results[$res]{model}   = 5;
			$results[$res]{S2}      = $data{m5}[$res]{S2};
			$results[$res]{S2_err}  = $data{m5}[$res]{S2_err};
			$results[$res]{S2f}     = $data{m5}[$res]{S2f};
			$results[$res]{S2f_err} = $data{m5}[$res]{S2f_err};
			$results[$res]{S2s}     = $data{m5}[$res]{S2s};
			$results[$res]{S2s_err} = $data{m5}[$res]{S2s_err};
			$results[$res]{te}      = $data{m5}[$res]{te};
			$results[$res]{te_err}  = $data{m5}[$res]{te_err};
			$results[$res]{SSE}     = $data{m5}[$res]{SSE};
		} elsif ( $select_model == "2+3" ) {
			printf $log_fh "%-12s", "[Model 2 and 3]";
			$results[$res]{model}   = "2+3";
		} elsif ( $select_model == "4+5" ) {
			printf $log_fh "%-12s", "[Model 4 and 5]";
			$results[$res]{model}   = "4+5";
		} else {
			printf $log_fh "%-12s", "[[[Model 0]]]";
			$results[$res]{model}   = 0;
		}
	}
}

# Do AIC model selection.
sub aic_model_select {
	print $log_fh "\n\n<<<AIC Model Selection>>>";
	for $res ( 0 .. $total_res ) {                 # Loop from first to last residue.
		printf $log_fh "\n\n%-22s\n", "   Checking res $data{m1}[$res]{resNo}";

		### Set up.
		$results[$res] = {
			resNo   => $data{m1}[$res]{resNo},
			model   => "",
			S2      => "",
			S2_err  => "",
			S2f     => "",
			S2f_err => "",
			S2s     => "",
			S2s_err => "",
			te      => "",
			te_err  => "",
			Rex     => "",
			Rex_err => "",
			SSE     => "",
		};
		$pi = 3.1415926535897932384626433832795028841971693993751058209749445923078164062862;
		$n = $num_data_sets;
		$AIC = [];
		$select_model = 0;

		### AIC Model selection.

		# Calculate AIC factors.
		# m1.
		$AIC[0] = $n*log(2*$pi) + $data{m1}[$res]{SSE} + 2*1;
		$AIC[0] = $AIC[0] / ( 2 * $n );
		$data{m1}[$res]{AIC} = $AIC[0];

		# m2.
		$AIC[1] = $n*log(2*$pi) + $data{m2}[$res]{SSE} + 2*2;
		$AIC[1] = $AIC[1] / ( 2 * $n );
		$data{m2}[$res]{AIC} = $AIC[1];

		# m3.
		$AIC[2] = $n*log(2*$pi) + $data{m3}[$res]{SSE} + 2*2;
		$AIC[2] = $AIC[2] / ( 2 * $n );
		$data{m3}[$res]{AIC} = $AIC[2];

		# m4.
		$AIC[3] = $n*log(2*$pi) + $data{m4}[$res]{SSE} + 2*3;
		$AIC[3] = $AIC[3] / ( 2 * $n );
		$data{m4}[$res]{AIC} = $AIC[3];

		# m5.
		$AIC[4] = $n*log(2*$pi) + $data{m5}[$res]{SSE} + 2*3;
		$AIC[4] = $AIC[4] / ( 2 * $n );
		$data{m5}[$res]{AIC} = $AIC[4];


		# Select model.
		$index = 0;
		for ( $i = 0; $i <= $#AIC; $i++ ) {
			if ( $AIC[$i] < $AIC[$index] ) {
				$index = $i;
			}
		}
		$select_model = $index + 1;
		print $log_fh "\tAIC (m1) $AIC[0]\n";
		print $log_fh "\tAIC (m2) $AIC[1]\n";
		print $log_fh "\tAIC (m3) $AIC[2]\n";
		print $log_fh "\tAIC (m4) $AIC[3]\n";
		print $log_fh "\tAIC (m5) $AIC[4]\n";
		print $log_fh "\tThe index is $index\n";
		print $log_fh "\tTherefore the selected model is $select_model\n";

		### Setting variables.
		if ( $select_model == 1 ) {
			printf $log_fh "%-12s", "[Model 1]";
			$results[$res]{model}   = 1;
			$results[$res]{S2}      = $data{m1}[$res]{S2};
			$results[$res]{S2_err}  = $data{m1}[$res]{S2_err};
			$results[$res]{SSE}     = $data{m1}[$res]{SSE};
		} elsif ( $select_model == 2 ) {
			printf $log_fh "%-12s", "[Model 2]";
			$results[$res]{model}   = 2;
			$results[$res]{S2}      = $data{m2}[$res]{S2};
			$results[$res]{S2_err}  = $data{m2}[$res]{S2_err};
			$results[$res]{te}      = $data{m2}[$res]{te};
			$results[$res]{te_err}  = $data{m2}[$res]{te_err};
			$results[$res]{SSE}     = $data{m2}[$res]{SSE};
		} elsif ( $select_model == 3 ) {
			printf $log_fh "%-12s", "[Model 3]";
			$results[$res]{model}   = 3;
			$results[$res]{S2}      = $data{m3}[$res]{S2};
			$results[$res]{S2_err}  = $data{m3}[$res]{S2_err};
			$results[$res]{Rex}     = $data{m3}[$res]{Rex};
			$results[$res]{Rex_err} = $data{m3}[$res]{Rex_err};
			$results[$res]{SSE}     = $data{m3}[$res]{SSE};
		} elsif ( $select_model == 4 ) {
			printf $log_fh "%-12s", "[Model 4]";
			$results[$res]{model}   = 4;
			$results[$res]{S2}      = $data{m4}[$res]{S2};
			$results[$res]{S2_err}  = $data{m4}[$res]{S2_err};
			$results[$res]{te}      = $data{m4}[$res]{te};
			$results[$res]{te_err}  = $data{m4}[$res]{te_err};
			$results[$res]{Rex}     = $data{m4}[$res]{Rex};
			$results[$res]{Rex_err} = $data{m4}[$res]{Rex_err};
			$results[$res]{SSE}     = $data{m4}[$res]{SSE};
		} elsif ( $select_model == 5 ) {
			printf $log_fh "%-12s", "[Model 5]";
			$results[$res]{model}   = 5;
			$results[$res]{S2}      = $data{m5}[$res]{S2};
			$results[$res]{S2_err}  = $data{m5}[$res]{S2_err};
			$results[$res]{S2f}     = $data{m5}[$res]{S2f};
			$results[$res]{S2f_err} = $data{m5}[$res]{S2f_err};
			$results[$res]{S2s}     = $data{m5}[$res]{S2s};
			$results[$res]{S2s_err} = $data{m5}[$res]{S2s_err};
			$results[$res]{te}      = $data{m5}[$res]{te};
			$results[$res]{te_err}  = $data{m5}[$res]{te_err};
			$results[$res]{SSE}     = $data{m5}[$res]{SSE};
		}
	}
}

# Do BIC model selection.
sub bic_model_select {
	print $log_fh "\n\n<<<BIC Model Selection>>>";
	for $res ( 0 .. $total_res ) {                 # Loop from first to last residue.
		printf $log_fh "\n\n%-22s\n", "   Checking res $data{m1}[$res]{resNo}";

		### Set up.
		$results[$res] = {
			resNo   => $data{m1}[$res]{resNo},
			model   => "",
			S2      => "",
			S2_err  => "",
			S2f     => "",
			S2f_err => "",
			S2s     => "",
			S2s_err => "",
			te      => "",
			te_err  => "",
			Rex     => "",
			Rex_err => "",
			SSE     => "",
		};
		$pi = 3.1415926535897932384626433832795028841971693993751058209749445923078164062862;
		$n = $num_data_sets;
		$BIC = [];
		$select_model = 0;

		### BIC Model selection.

		# Calculate BIC factors.
		# m1.
		$BIC[0] = $n*log(2*$pi) + $data{m1}[$res]{SSE} + 1*log($n);
		$BIC[0] = $BIC[0] / ( 2 * $n );
		$data{m1}[$res]{BIC} = $BIC[0];

		# m2.
		$BIC[1] = $n*log(2*$pi) + $data{m2}[$res]{SSE} + 2*log($n);
		$BIC[1] = $BIC[1] / ( 2 * $n );
		$data{m2}[$res]{BIC} = $BIC[1];

		# m3.
		$BIC[2] = $n*log(2*$pi) + $data{m3}[$res]{SSE} + 2*log($n);
		$BIC[2] = $BIC[2] / ( 2 * $n );
		$data{m3}[$res]{BIC} = $BIC[2];

		# m4.
		$BIC[3] = $n*log(2*$pi) + $data{m4}[$res]{SSE} + 3*log($n);
		$BIC[3] = $BIC[3] / ( 2 * $n );
		$data{m4}[$res]{BIC} = $BIC[3];

		# m5.
		$BIC[4] = $n*log(2*$pi) + $data{m5}[$res]{SSE} + 3*log($n);
		$BIC[4] = $BIC[4] / ( 2 * $n );
		$data{m5}[$res]{BIC} = $BIC[4];


		# Select model.
		$index = 0;
		for ( $i = 0; $i <= $#BIC; $i++ ) {
			if ( $BIC[$i] < $BIC[$index] ) {
				$index = $i;
			}
		}
		$select_model = $index + 1;
		print $log_fh "\tBIC (m1) $BIC[0]\n";
		print $log_fh "\tBIC (m2) $BIC[1]\n";
		print $log_fh "\tBIC (m3) $BIC[2]\n";
		print $log_fh "\tBIC (m4) $BIC[3]\n";
		print $log_fh "\tBIC (m5) $BIC[4]\n";
		print $log_fh "\tThe index is $index\n";
		print $log_fh "\tTherefore the selected model is $select_model\n";

		### Setting variables.
		if ( $select_model == 1 ) {
			printf $log_fh "%-12s", "[Model 1]";
			$results[$res]{model}   = 1;
			$results[$res]{S2}      = $data{m1}[$res]{S2};
			$results[$res]{S2_err}  = $data{m1}[$res]{S2_err};
			$results[$res]{SSE}     = $data{m1}[$res]{SSE};
		} elsif ( $select_model == 2 ) {
			printf $log_fh "%-12s", "[Model 2]";
			$results[$res]{model}   = 2;
			$results[$res]{S2}      = $data{m2}[$res]{S2};
			$results[$res]{S2_err}  = $data{m2}[$res]{S2_err};
			$results[$res]{te}      = $data{m2}[$res]{te};
			$results[$res]{te_err}  = $data{m2}[$res]{te_err};
			$results[$res]{SSE}     = $data{m2}[$res]{SSE};
		} elsif ( $select_model == 3 ) {
			printf $log_fh "%-12s", "[Model 3]";
			$results[$res]{model}   = 3;
			$results[$res]{S2}      = $data{m3}[$res]{S2};
			$results[$res]{S2_err}  = $data{m3}[$res]{S2_err};
			$results[$res]{Rex}     = $data{m3}[$res]{Rex};
			$results[$res]{Rex_err} = $data{m3}[$res]{Rex_err};
			$results[$res]{SSE}     = $data{m3}[$res]{SSE};
		} elsif ( $select_model == 4 ) {
			printf $log_fh "%-12s", "[Model 4]";
			$results[$res]{model}   = 4;
			$results[$res]{S2}      = $data{m4}[$res]{S2};
			$results[$res]{S2_err}  = $data{m4}[$res]{S2_err};
			$results[$res]{te}      = $data{m4}[$res]{te};
			$results[$res]{te_err}  = $data{m4}[$res]{te_err};
			$results[$res]{Rex}     = $data{m4}[$res]{Rex};
			$results[$res]{Rex_err} = $data{m4}[$res]{Rex_err};
			$results[$res]{SSE}     = $data{m4}[$res]{SSE};
		} elsif ( $select_model == 5 ) {
			printf $log_fh "%-12s", "[Model 5]";
			$results[$res]{model}   = 5;
			$results[$res]{S2}      = $data{m5}[$res]{S2};
			$results[$res]{S2_err}  = $data{m5}[$res]{S2_err};
			$results[$res]{S2f}     = $data{m5}[$res]{S2f};
			$results[$res]{S2f_err} = $data{m5}[$res]{S2f_err};
			$results[$res]{S2s}     = $data{m5}[$res]{S2s};
			$results[$res]{S2s_err} = $data{m5}[$res]{S2s_err};
			$results[$res]{te}      = $data{m5}[$res]{te};
			$results[$res]{te_err}  = $data{m5}[$res]{te_err};
			$results[$res]{SSE}     = $data{m5}[$res]{SSE};
		}
	}
}

# Extract the model for each residue form the "hand.selection" file.
sub extract_handsel {
	$res = 0;
	while ( @row = split(' ',<HAND>) ) {
		if ( $row[0] =~ /^R/ || $row[0] =~ /^r/ ) {
			next;
		}
		if ( $row[0] != $data{m1}[$res]{resNo} ) {
			die "Residue $row[0] in \"hand.selection\" does not match residue $data{m1}[$res]{resNo}, quitting!\n\n";
		}
		$results[$res] = {
			resNo   => $row[0],
			model   => $row[1],
			S2      => "",
			S2_err  => "",
			S2f     => "",
			S2f_err => "",
			S2s     => "",
			S2s_err => "",
			te      => "",
			te_err  => "",
			Rex     => "",
			Rex_err => "",
			SSE     => $data{m1}[$res]{SSE},
		};
		$model = "m" . $results[$res]{model};
		if ( $model eq "m1" ) {
			$results[$res]{S2}      = $data{$model}[$res]{S2};
			$results[$res]{S2_err}  = $data{$model}[$res]{S2_err};
			$results[$res]{SSE}     = $data{$model}[$res]{SSE};
		} elsif ( $model eq "m2" ) {
			$results[$res]{S2}      = $data{$model}[$res]{S2};
			$results[$res]{S2_err}  = $data{$model}[$res]{S2_err};
			$results[$res]{te}      = $data{$model}[$res]{te};
			$results[$res]{te_err}  = $data{$model}[$res]{te_err};
			$results[$res]{SSE}     = $data{$model}[$res]{SSE};
		} elsif ( $model eq "m3" ) {
			$results[$res]{S2}      = $data{$model}[$res]{S2};
			$results[$res]{S2_err}  = $data{$model}[$res]{S2_err};
			$results[$res]{Rex}     = $data{$model}[$res]{Rex};
			$results[$res]{Rex_err} = $data{$model}[$res]{Rex_err};
			$results[$res]{SSE}     = $data{$model}[$res]{SSE};
		} elsif ( $model eq "m4" ) {
			$results[$res]{S2}      = $data{$model}[$res]{S2};
			$results[$res]{S2_err}  = $data{$model}[$res]{S2_err};
			$results[$res]{te}      = $data{$model}[$res]{te};
			$results[$res]{te_err}  = $data{$model}[$res]{te_err};
			$results[$res]{Rex}     = $data{$model}[$res]{Rex};
			$results[$res]{Rex_err} = $data{$model}[$res]{Rex_err};
			$results[$res]{SSE}     = $data{$model}[$res]{SSE};
		} elsif ( $model eq "m5" ) {
			$results[$res]{S2}      = $data{$model}[$res]{S2};
			$results[$res]{S2_err}  = $data{$model}[$res]{S2_err};
			$results[$res]{S2f}     = $data{$model}[$res]{S2f};
			$results[$res]{S2f_err} = $data{$model}[$res]{S2f_err};
			$results[$res]{S2s}     = $data{$model}[$res]{S2s};
			$results[$res]{S2s_err} = $data{$model}[$res]{S2s_err};
			$results[$res]{te}      = $data{$model}[$res]{te};
			$results[$res]{te_err}  = $data{$model}[$res]{te_err};
			$results[$res]{SSE}     = $data{$model}[$res]{SSE};
		}
		++$res;
	}
}

# Create the output files ./results.*.
sub results {
	printf RESULTS "%-6s%-6s%-13s", "ResNo", "Model", "    S2";
	printf RESULTS "%-13s%-13s%-19s%-13s", "    S2f", "    S2s", "       te", "    Rex";
	printf RESULTS "%-10s\n", "    SSE";
	for $res ( 0 .. $total_res ) {           # Loop from first to last residue.
		printf RESULTS "%-6s%-6s", $results[$res]{resNo}, $results[$res]{model};
		if ( $results[$res]{S2} ) {      # All residues with an S2 value.
			printf RESULTS "%5s%1s%-5s  ", $results[$res]{S2}, "±", $results[$res]{S2_err};
		} else {
			printf RESULTS "%13s", "";
		}
		if ( $results[$res]{S2f} ) {     # All residues with an S2f value.
			printf RESULTS "%5s%1s%-5s  ", $results[$res]{S2f}, "±", $results[$res]{S2f_err};
		} else {
			printf RESULTS "%13s", "";
		}
		if ( $results[$res]{S2s} ) {     # All residues with an S2s value.
			printf RESULTS "%5s%1s%-5s  ", $results[$res]{S2s}, "±", $results[$res]{S2s_err};
		} else {
			printf RESULTS "%13s", "";
		}
		if ( $results[$res]{te} ) {      # All residues with an te value.
			printf RESULTS "%8s%1s%-8s  ", $results[$res]{te}, "±", $results[$res]{te_err};
		} else {
			printf RESULTS "%19s", "";
		}
		if ( $results[$res]{Rex} ) {     # All residues with an Rex value.
			printf RESULTS "%5s%1s%-5s  ", $results[$res]{Rex}, "±", $results[$res]{Rex_err};
		} else {
			printf RESULTS "%13s", "";
		}
		printf RESULTS "%10s\n", $results[$res]{SSE};
	}
}

# Create grace files for the results.
sub grace {
	print $log_fh "\n\n";
	if ( $stage == 2 ) {
		$sub_title = "After model selection, unoptimized";
	} elsif ( $stage == 3 ) {
		$sub_title = "Fully optimized";
	}
	&grace_header("S2AGR","S2 values",$sub_title,"Residue Number","S2","xydy");           # Create a grace header.
	&grace_header("S2FAGR","S2f values",$sub_title,"Residue Number","S2f","xydy");        # Create a grace header.
	&grace_header("S2SAGR","S2s values",$sub_title,"Residue Number","S2s","xydy");        # Create a grace header.
	&grace_header("TEAGR","te values",$sub_title,"Residue Number","te (ps)","xydy");      # Create a grace header.
	&grace_header("REXAGR","Rex values",$sub_title,"Residue Number","Rex (1/s)","xydy");  # Create a grace header.
	&grace_header("SSEAGR","SSE values",$sub_title,"Residue Number","SSE","xy");          # Create a grace header.
	for $res ( 0 .. $total_res ) {           # Loop from first to last residue.
		if ( $results[$res]{S2} ) {      # All residues with an S2 value.
			print S2AGR "$results[$res]{resNo} $results[$res]{S2} $results[$res]{S2_err}\n";
		}
		if ( $results[$res]{S2f} ) {     # All residues with an S2f value.
			print S2FAGR "$results[$res]{resNo} $results[$res]{S2f} $results[$res]{S2f_err}\n";
		}
		if ( $results[$res]{S2s} ) {     # All residues with an S2s value.
			print S2SAGR "$results[$res]{resNo} $results[$res]{S2s} $results[$res]{S2s_err}\n";
		}
		if ( $results[$res]{te} ) {      # All residues with an te value.
			print TEAGR "$results[$res]{resNo} $results[$res]{te} $results[$res]{te_err}\n";
		}
		if ( $results[$res]{Rex} ) {     # All residues with an Rex value.
			print REXAGR "$results[$res]{resNo} $results[$res]{Rex} $results[$res]{Rex_err}\n";
		}
		if ( $results[$res]{SSE} ) {     # All residues with an SSE value.
			print SSEAGR "$results[$res]{resNo} $results[$res]{SSE}\n";
		}
	}
	print S2AGR "&\n";
	print S2FAGR "&\n";
	print S2SAGR "&\n";
	print TEAGR "&\n";
	print REXAGR "&\n";
	print SSEAGR "&\n";
	if ( -e "header" ) {
		print "Found the grace header \"./header\", appending to \"./grace/sse_*.agr\" files.\n";
	} else {
		print "Grace header file \"./header\" missing, grace files will be unformatted.\n";
	}
	if ( $stage == 2 ) {
		print "Creating a grace file for each residue, with SSE values for each relaxation value for each model.\n";
		for $res ( 0 .. $total_res ) {               # Loop from first to last residue.
			$sse_file = "sse_" . $data{m1}[$res]{resNo} . ".agr";
			open(RES_SSE_AGR, ">grace/$sse_file");
			print RES_SSE_AGR "\@    title \"Residue $data{m1}[$res]{resNo}\"\n";
			foreach $n ( 0 .. $#input ) {
				($NMR_frq_label, $data_type) = split(' ',$input[$n]);
				&create_data_info($data_type,$NMR_frq_label);     # Create the data info.
				print RES_SSE_AGR "\@target G0.S$n\n\@type xy\n";
				for $model ( @models ) {     # Loop for the 5 mfout files.
					if ( $model =~ /^m/ ) {
						@model_num = split('m',$model);
						&create_data_info($data_type,$NMR_frq_label);    # Create the variables for the original data.
						print RES_SSE_AGR "$model_num[1] $data{$model}[$res]{$data_SSE_label}\n";
					}
				}
				print RES_SSE_AGR "&\n";
			}
			close(RES_SSE_AGR);
			if ( -e "header" ) {
				system("cat header grace/$sse_file > grace/temp.agr");
				system("mv grace/temp.agr grace/$sse_file");
			}
		}
		print "Creating grace files for comparing SSE to relaxation values.\n";
		foreach $n ( 0 .. $#input ) {
			($NMR_frq_label, $data_type) = split(' ',$input[$n]);
			$sse_fh = "SSE_VS_" . $data_type . "_" . $NMR_frq_label;
			$sse_file = "SSEvs" . $data_type . "_" . $NMR_frq_label . ".agr";
			$title = $data_type . " SSE  vs  " . $NMR_frq_label . "MHz " . $data_type . " Values";
			open($sse_fh, ">grace/$sse_file");
			if ( $data_type eq "NOE" ) {
				$xaxis = $data_type;
			} else {
				$xaxis = $data_type . " (1/s)";
			}
			&grace_header($sse_fh,$title,"SSE of selected models",$xaxis,"SSE","xy");     # Create a grace header.
			&create_data_info($data_type,$NMR_frq_label);    # Create the variables for the original data.
			for $res ( 0 .. $total_res ) {                   # Loop from first to last residue.
				if ( $data{$results[$res]{model}}[$res]{$data_SSE_label} ) {
					print $sse_fh "$data{m1}[$res]{$data_label} $data{$results[$res]{model}}[$res]{$data_SSE_label}\n";
				} else {
					print $sse_fh "$data{m1}[$res]{$data_label} $data{m1}[$res]{$data_SSE_label}\n";
				}
			}
			print $sse_fh "&\n";
			close($sse_fh);
		}
	}
}

# Create a grace header.
# Input data should be in the following format:
#    0 => Filehandle
#    1 => Title
#    2 => Subtitle
#    3 => X axis lable
#    4 => Y axis lable
#    5 => Graph type
#
sub grace_header {
	local($fh);
	$fh = $_[0];
	print $fh "\@version 50100\n";
	print $fh "\@with g0\n";
	if ( $_[3] eq "Residue Number" ) {
		print $fh "\@    world xmax 165\n";
	} elsif ( $_[3] eq "R1 (1/s)" && $_[4] eq "SSE" ) {
		print $fh "\@    world xmin 0.8\n";
		print $fh "\@    world xmax 2\n";
		print $fh "\@    world ymin 0\n";
		print $fh "\@    world ymax 2000\n";
	} elsif ( $_[3] eq "R2 (1/s)" && $_[4] eq "SSE" ) {
		print $fh "\@    world xmin 5\n";
		print $fh "\@    world xmax 45\n";
		print $fh "\@    world ymin 0\n";
		print $fh "\@    world ymax 2000\n";
	} elsif ( $_[3] eq "NOE" && $_[4] eq "SSE" ) {
		print $fh "\@    world xmin 0\n";
		print $fh "\@    world xmax 1\n";
		print $fh "\@    world ymin 0\n";
		print $fh "\@    world ymax 2000\n";
	}
	print $fh "\@    view xmax 1.22\n";
	print $fh "\@    title \"$_[1]\"\n";
	print $fh "\@    subtitle \"$_[2]\"\n";
	print $fh "\@    xaxis  label \"$_[3]\"\n";
	if ( $_[3] eq "Residue Number" ) {
		print $fh "\@    xaxis  tick major 10\n";
	} elsif ( $_[3] eq "R1 (1/s)" && $_[4] eq "SSE" ) {
		print $fh "\@    xaxis  tick major 0.2\n";
	} elsif ( $_[3] eq "R2 (1/s)" && $_[4] eq "SSE" ) {
		print $fh "\@    xaxis  tick major 5\n";
	} elsif ( $_[3] eq "NOE" && $_[4] eq "SSE" ) {
		print $fh "\@    xaxis  tick major 0.1\n";
	}
	print $fh "\@    xaxis  tick major size 0.480000\n";
	print $fh "\@    xaxis  tick major linewidth 0.5\n";
	print $fh "\@    xaxis  tick minor linewidth 0.5\n";
	print $fh "\@    xaxis  tick minor size 0.240000\n";
	print $fh "\@    xaxis  ticklabel char size 0.790000\n";
	print $fh "\@    yaxis  label \"$_[4]\"\n";
	if ( $_[3] eq "R1 (1/s)" && $_[4] eq "SSE" ) {
		print $fh "\@    yaxis  tick major 200\n";
	} elsif ( $_[3] eq "R2 (1/s)" && $_[4] eq "SSE" ) {
		print $fh "\@    yaxis  tick major 200\n";
	} elsif ( $_[3] eq "NOE" && $_[4] eq "SSE" ) {
		print $fh "\@    yaxis  tick major 200\n";
	}
	print $fh "\@    yaxis  tick major size 0.480000\n";
	print $fh "\@    yaxis  tick major linewidth 0.5\n";
	print $fh "\@    yaxis  tick minor linewidth 0.5\n";
	print $fh "\@    yaxis  tick minor size 0.240000\n";
	print $fh "\@    yaxis  ticklabel char size 0.790000\n";
	print $fh "\@    frame linewidth 0.5\n";
	print $fh "\@    s0 symbol 1\n";
	print $fh "\@    s0 symbol size 0.49\n";
	print $fh "\@    s0 symbol fill pattern 1\n";
	print $fh "\@    s0 symbol linewidth 0.5\n";
	print $fh "\@    s0 line linestyle 0\n";
	print $fh "\@target G0.S0\n\@type $_[5]\n";
}

# Place the whole 3D %data data structure into the file data.str.stage2.
sub print_data {
	for $res ( 0 .. $total_res ) {              # Loop for all residues.
		print DLOG "<<< Residue $data{m1}[$res]{resNo}, Model $results[$res]{model} >>>\n";
		printf DLOG "%-10s", "";
		printf DLOG "%-8s%-8s%-8s%-8s", "S2", "S2_err", "S2f", "S2f_err";
		printf DLOG "%-8s%-8s", "S2s", "S2s_err";
		printf DLOG "%-10s%-10s%-8s%-8s", "te", "te_err", "Rex", "Rex_err";
		printf DLOG "%-10s%-10s%-10s", "SSE", "SSElim", "SSE<$SSEtile";
		printf DLOG "%-10s%-10s\n", "LargeSSE", "ZeroSSE";
		for $model ( @models ) {            # Loop for the 5 mfout files.
			if ( $model =~ /^m/ ) {     # Models 1 to 5.
				printf DLOG "%-10s", "$model";
				printf DLOG "%-8s", $data{$model}[$res]{S2};
				printf DLOG "%-8s", $data{$model}[$res]{S2_err};
				printf DLOG "%-8s", $data{$model}[$res]{S2f};
				printf DLOG "%-8s", $data{$model}[$res]{S2f_err};
				printf DLOG "%-8s", $data{$model}[$res]{S2s};
				printf DLOG "%-8s", $data{$model}[$res]{S2s_err};
				printf DLOG "%-10s", $data{$model}[$res]{te};
				printf DLOG "%-10s", $data{$model}[$res]{te_err};
				printf DLOG "%-8s", $data{$model}[$res]{Rex};
				printf DLOG "%-8s", $data{$model}[$res]{Rex_err};
				printf DLOG "%-10s", $data{$model}[$res]{SSE};
				printf DLOG "%-10s", $data{$model}[$res]{SSElim};
				printf DLOG "%-10s", $data{$model}[$res]{SSElim_f};
				printf DLOG "%-10s", $data{$model}[$res]{largeSSE};
				printf DLOG "%-10s", $data{$model}[$res]{zeroSSE};
				print DLOG "\n";
			}
		}
		printf DLOG "%-3s", "";
		foreach $n ( 0 .. $#input ) {
			($NMR_frq_label, $data_type) = split(' ',$input[$n]);
			printf DLOG "%13s%7s%10s", "$NMR_frq_label $data_type", $data_type . "fit", $data_type . "sse";
		}
		printf DLOG "\n";
		for $model ( @models ) {            # Loop for the 5 mfout files.
			if ( $model !~ /^m/ ) {     # Not models 1 to 5.
				next;
			}
			printf DLOG "%-3s", "$model";
			foreach $n ( 0 .. $#input ) {
				($NMR_frq_label, $data_type) = split(' ',$input[$n]);
				&create_data_info($data_type,$NMR_frq_label);     # Create the data info.
				printf DLOG "%13s", "$data{$model}[$res]{$data_label}±$data{$model}[$res]{$data_err_label}";
				printf DLOG "%7.3f", $data{$model}[$res]{$data_fit_label};
				printf DLOG "%10.3f", $data{$model}[$res]{$data_SSE_label};
			}
			printf DLOG "\n";
		}
		if ( $selection =~ "AIC" ) {
			printf DLOG "%-3s%13s\n", "", "AIC/2n";
			for $model ( @models ) {            # Loop for the 5 mfout files.
				if ( $model =~ /^m/ ) {     # Models 1 to 5.
					printf DLOG "%-3s%13.8f\n", $model, $data{$model}[$res]{AIC};
				}
			}
		}
		if ( $selection =~ "BIC" ) {
			printf DLOG "%-3s%13s\n", "", "BIC/2n";
			for $model ( @models ) {            # Loop for the 5 mfout files.
				if ( $model =~ /^m/ ) {     # Models 1 to 5.
					printf DLOG "%-3s%13.8f\n", $model, $data{$model}[$res]{BIC};
				}
			}
		}
		printf DLOG "%-10s%-18s%-18s%-18s\n", "", "F-stat", "F-stat_lim", "F-test_f";
		for $model ( @models ) {            # Loop for the 5 mfout files.
			if ( $model =~ /^f/ ) {
				printf DLOG "%-10s", "$model";
				printf DLOG "%-18s", $ftest{$model}[$res]{fstat};
				printf DLOG "%-18s", $ftest{$model}[$res]{fstatlim};
				printf DLOG "%-18s", $ftest{$model}[$res]{ftest_f};
				print DLOG "\n";
			}
		}
		print DLOG "\n";
	}
}

# Extract the model for each residue from the stage 2 result file.
sub extract_models {
	$res = 0;
	while ( @row = split(' ',<STAGE2_RESULTS>) ) {
		if ( $row[0] =~ /ResNo/ ) {
			next;
		}
		$data{opt}[$res]{resNo} = $row[0];
		$data{opt}[$res]{model} = $row[1];
		++$res;
	}
}

# Create the final result data structure.
sub final_results {
	for $res ( 0 .. $total_res ) {              # Loop from first to last residue.
		$results[$res] = {
			resNo   => $data{opt}[$res]{resNo},
			model   => $data{opt}[$res]{model},
			S2      => "",
			S2_err  => "",
			S2f     => "",
			S2f_err => "",
			S2s     => "",
			S2s_err => "",
			te      => "",
			te_err  => "",
			Rex     => "",
			Rex_err => "",
			SSE     => "",
		};
		if ( $results[$res]{model} eq "0" ) {
			$results[$res]{SSE}     = $data{opt}[$res]{SSE};
		} elsif ( $results[$res]{model} =~ /2\+3/ || $results[$res]{model} =~ /4\+5/ ) {
			$results[$res]{SSE}     = $data{opt}[$res]{SSE};
		} elsif ( $results[$res]{model} =~ /1./ ) {
			$results[$res]{S2}      = $data{opt}[$res]{S2};
			$results[$res]{S2_err}  = $data{opt}[$res]{S2_err};
			$results[$res]{SSE}     = $data{opt}[$res]{SSE};
		} elsif ( $results[$res]{model} == 1 ) {
			$results[$res]{S2}      = $data{opt}[$res]{S2};
			$results[$res]{S2_err}  = $data{opt}[$res]{S2_err};
			$results[$res]{SSE}     = $data{opt}[$res]{SSE};
		} elsif ( $results[$res]{model} == 2 ) {
			$results[$res]{S2}      = $data{opt}[$res]{S2};
			$results[$res]{S2_err}  = $data{opt}[$res]{S2_err};
			$results[$res]{te}      = $data{opt}[$res]{te};
			$results[$res]{te_err}  = $data{opt}[$res]{te_err};
			$results[$res]{SSE}     = $data{opt}[$res]{SSE};
		} elsif ( $results[$res]{model} == 3 ) {
			$results[$res]{S2}      = $data{opt}[$res]{S2};
			$results[$res]{S2_err}  = $data{opt}[$res]{S2_err};
			$results[$res]{Rex}     = $data{opt}[$res]{Rex};
			$results[$res]{Rex_err} = $data{opt}[$res]{Rex_err};
			$results[$res]{SSE}     = $data{opt}[$res]{SSE};
		} elsif ( $results[$res]{model} == 4 ) {
			$results[$res]{S2}      = $data{opt}[$res]{S2};
			$results[$res]{S2_err}  = $data{opt}[$res]{S2_err};
			$results[$res]{te}      = $data{opt}[$res]{te};
			$results[$res]{te_err}  = $data{opt}[$res]{te_err};
			$results[$res]{Rex}     = $data{opt}[$res]{Rex};
			$results[$res]{Rex_err} = $data{opt}[$res]{Rex_err};
			$results[$res]{SSE}     = $data{opt}[$res]{SSE};
		} elsif ( $results[$res]{model} == 5 ) {
			$results[$res]{S2}      = $data{opt}[$res]{S2};
			$results[$res]{S2_err}  = $data{opt}[$res]{S2_err};
			$results[$res]{S2f}     = $data{opt}[$res]{S2f};
			$results[$res]{S2f_err} = $data{opt}[$res]{S2f_err};
			$results[$res]{S2s}     = $data{opt}[$res]{S2s};
			$results[$res]{S2s_err} = $data{opt}[$res]{S2s_err};
			$results[$res]{te}      = $data{opt}[$res]{te};
			$results[$res]{te_err}  = $data{opt}[$res]{te_err};
			$results[$res]{SSE}     = $data{opt}[$res]{SSE};
		}
	}
}

# Close the log and raw data files.
sub close_universal_files {
	foreach $n ( 0 .. $#input ) {
		($NMR_frq_label, $data_type) = split(' ',$input[$n]);
		&create_data_info($data_type,$NMR_frq_label);     # Create the data info.
		close($data_fh);
	}
	close($log_fh);
}

# Close the model specific files.
sub close_mfiles {
	close(MODEL);
	close(PAR);
	close(DATA);
	close(RUN);
	close(MFIN);
}

# Close the files used in stage 2 and 3.
sub close_stage_files {
	close(DLOG);
	close(RESULTS);
	close(S2AGR);
	close(S2FAGR);
	close(S2SAGR);
	close(TEAGR);
	close(REXAGR);
	close(SSEAGR);
	if ( $selection =~ "Hand" ) {
		close(HAND);
	}
}
