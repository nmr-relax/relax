#!/usr/bin/perl -w


&open_files;
&constants;          # Define constants.
&dipolar;            # Calculate the dipolar constant.
&csa;                # Calculate the CSA constant.
&create_grid;        # Create grid.
print LOG "\n\n\n<<< Relaxation grid parameters >>>\n\n";
for ( $res = 0; $res <= $#grid; $res++ ) {
	print LOG "\nResidue $res:\n";

	# 600 MHz (a) data.
	$ja[0] = &spect_dens($frq_600[0], "a0");
	$ja[1] = &spect_dens($frq_600[1], "a1");
	$ja[2] = &spect_dens($frq_600[2], "a2");
	$ja[3] = &spect_dens($frq_600[3], "a3");
	$ja[4] = &spect_dens($frq_600[4], "a4");

	# 500 MHz (b) data.
	$jb[0] = &spect_dens($frq_500[0], "b0");
	$jb[1] = &spect_dens($frq_500[1], "b1");
	$jb[2] = &spect_dens($frq_500[2], "b2");
	$jb[3] = &spect_dens($frq_500[3], "b3");
	$jb[4] = &spect_dens($frq_500[4], "b4");

	# Calculate relaxation values.
	# 600 MHz R1.
	$grid[$res]{r1_600} = $dip * ( $ja[2] + 3*$ja[1] + 6*$ja[4] )  +  $csa_600 * $ja[1];
	$grid[$res]{r1_600_err} = $grid[$res]{r1_600} * 0.02;
	
	# 600 MHz R2.
	$r2_dip = ( $dip / 2 ) * ( 4*$ja[0] + $ja[2] + 3*$ja[1] + 6*$ja[3] + 6*$ja[4] );
	$r2_csa = ( $csa_600 / 6 ) * ( 4*$ja[0] + 3*$ja[1] );
	$grid[$res]{r2_600} = $r2_dip + $r2_csa + $grid[$res]{rex_600};
	$grid[$res]{r2_600_err} = $grid[$res]{r2_600} * 0.02;
	
	# 600 MHz NOE.
	$grid[$res]{noe_600} = 1 + ( $dip / $grid[$res]{r1_600} ) * ( $gh / $gn ) * (6*$ja[4] - $ja[2]);
	$grid[$res]{noe_600_err} = 0.04;
	
	# 500 MHz R1.
	$grid[$res]{r1_500} = $dip * ( $jb[2] + 3*$jb[1] + 6*$jb[4] )  +  $csa_500 * $jb[1];
	$grid[$res]{r1_500_err} = $grid[$res]{r1_500} * 0.02;
	
	# 500 MHz R2.
	$r2_dip = ( $dip / 2 ) * ( 4*$jb[0] + $jb[2] + 3*$jb[1] + 6*$jb[3] + 6*$jb[4] );
	$r2_csa = ( $csa_500 / 6 ) * ( 4*$jb[0] + 3*$jb[1] );
	$grid[$res]{r2_500} = $r2_dip + $r2_csa + $grid[$res]{rex_500};
	$grid[$res]{r2_500_err} = $grid[$res]{r2_500} * 0.02;
	
	# 500 MHz NOE.
	$grid[$res]{noe_500} = 1 + ( $dip / $grid[$res]{r1_500} ) * ( $gh / $gn ) * (6*$jb[4] - $jb[2]);
	$grid[$res]{noe_500_err} = 0.05;
}
&print_grid;         # Place all the grid parameters into a single file.
&create_grace;       # Create grace files.
&create_relax_files; # Create the NOE, R1, and R2 files for both a and b MHz.
&close_files;


sub open_files {
	open(LOG, ">log");
	open(GRID, ">grid.out");
	open(REXAGR, ">Rex_grids.agr");
	open(S2SAGR, ">S2s_grids.agr");
	open(NOE_600, ">noe.600.out");
	open(R1_600, ">r1.600.out");
	open(R2_600, ">r2.600.out");
	open(NOE_500, ">noe.500.out");
	open(R1_500, ">r1.500.out");
	open(R2_500, ">r2.500.out");
}

# Define constants.
sub constants {
	$tm = 11.091e-9;
	$gh = 26.7522e7;
	$gn = -2.7126e7;
	$pi = 3.141592654;
	$h = 6.6260755e-34;
	$h_bar = $h / (2*$pi);
	$rnh = 1.02e-10;
	$mu0 = 4*$pi * 1e-7;
	$csa = -170.0e-6;

	# 600 MHz data.
	$frq_600h = (599.741e6) * (2*$pi);
	$frq_600n = ( $gn / $gh ) * $frq_600h;

	$frq_600[0] = 0.0;
	$frq_600[1] = $frq_600n;
	$frq_600[2] = $frq_600h - $frq_600n;
	$frq_600[3] = $frq_600h;
	$frq_600[4] = $frq_600h + $frq_600n;

	print LOG "The 600 MHz frequencies are:\n";
	$temp = $frq_600[0] / (2*$pi*1e6);
	print LOG "\tFreq (0)    : $temp\n";
	$temp = $frq_600[1] / (2*$pi*1e6);
	print LOG "\tFreq (wn)   : $temp\n";
	$temp = $frq_600[2] / (2*$pi*1e6);
	print LOG "\tFreq (wh-wn): $temp\n";
	$temp = $frq_600[3] / (2*$pi*1e6);
	print LOG "\tFreq (wh)   : $temp\n";
	$temp = $frq_600[4] / (2*$pi*1e6);
	print LOG "\tFreq (wh+wn): $temp\n";

	# 500 MHz data.
	$frq_500h = (500.241e6) * (2*$pi);
	$frq_500n = ( $gn / $gh ) * $frq_500h;

	$frq_500[0] = 0.0;
	$frq_500[1] = $frq_500n;
	$frq_500[2] = $frq_500h - $frq_500n;
	$frq_500[3] = $frq_500h;
	$frq_500[4] = $frq_500h + $frq_500n;

	print LOG "The 500 MHz frequencies are:\n";
	$temp = $frq_500[0] / (2*$pi*1e6);
	print LOG "\tFreq (0)    : $temp\n";
	$temp = $frq_500[1] / (2*$pi*1e6);
	print LOG "\tFreq (wn)   : $temp\n";
	$temp = $frq_500[2] / (2*$pi*1e6);
	print LOG "\tFreq (wh-wn): $temp\n";
	$temp = $frq_500[3] / (2*$pi*1e6);
	print LOG "\tFreq (wh)   : $temp\n";
	$temp = $frq_500[4] / (2*$pi*1e6);
	print LOG "\tFreq (wh+wn): $temp\n";

	@s2f = (0.901);
	@tf = (0.0);
	for ($i = 0; $i <= $#tf; $i++) {
		$tf[$i] = $tf[$i] * 1e-12;
	}
	@rex_600 = (0);
	for ($i = 0; $i <= $#rex_600; $i++) {
		$rex_500[$i] = $rex_600[$i] * ( ($frq_500h / $frq_600h)**2 );
	}
	@s2s = @s2f;
	@ts = @tf;
}
# Calculate the dipolar constant.
sub dipolar {
	$dip = ($mu0/(4*$pi)) * $h_bar * $gh * $gn * ($rnh**-3);
	$dip = ($dip**2) / 4;
	$dip_temp = $dip / ( 1e9 );
	printf LOG "%-50s%8.6f%-6s\n", "The dipolar constant is:", $dip_temp, " * 10^9";
}

# Calculate the CSA constant.
sub csa {
	# 600 MHz (a) CSA constant.
	$csa_600 = ( ($csa**2) * ($frq_600[1]**2) ) / 3;
	$csa_temp_600 = $csa_600 / ( 1e9 );
	printf LOG "%-50s%8.6f%-6s\n", "The CSA constant at a MHz is:", $csa_temp_600, " * 10^9";
	$cd_600 = $csa_600 / $dip;
	printf LOG "%-50s%8.6f\n", "The CSA/dipolar constant ratio at a MHz is:", $cd_600;

	# 500 MHz (b) CSA constant.
	$csa_500 = ( ($csa**2) * ($frq_500[1]**2) ) / 3;
	$csa_temp_500 = $csa_500 / ( 1e9 );
	printf LOG "%-50s%8.6f%-6s\n", "The CSA constant at b MHz is:", $csa_temp_500, " * 10^9";
	$cd_500 = $csa_500 / $dip;
	printf LOG "%-50s%8.6f\n", "The CSA/dipolar constant ratio at b MHz is:", $cd_500;
}

# Create grid.
sub create_grid {
	$grid = [[]];
	$count = 0;
	print LOG "\n\n\n<<< Modelfree grid parameters >>>\n\n";
	printf LOG "%-8s%-8s%-12s%-8s%-8s%-12s%-8s\n", "Res", "S2f", "tf", "Rex(600)", "Rex(500)", "S2s", "ts", "S2";
	for ( $rex_count = 0; $rex_count <= $#rex_600; $rex_count++ ) {
		for ( $tf_count = 0; $tf_count <= $#tf; $tf_count++ ) {
			for ( $s2f_count = 0; $s2f_count <= $#s2f; $s2f_count++ ) {
				$grid[$count]{s2f} = $s2f[$s2f_count];
				$grid[$count]{tf}  = $tf[$tf_count];
				$grid[$count]{rex_600} = $rex_600[$rex_count];
				$grid[$count]{rex_500} = $rex_500[$rex_count];
				$grid[$count]{s2s} = 1;
				$grid[$count]{ts}  = 0;
				$grid[$count]{s2}  = $s2f[$s2f_count]*1;
				$grid[$count]{tf_prime} = $grid[$count]{tf}*$tm / ( $grid[$count]{tf} + $tm );
				$grid[$count]{ts_prime} = $grid[$count]{ts}*$tm / ( $grid[$count]{ts} + $tm );
				printf LOG "%-8s%-8.3f%-12s", $count, $grid[$count]{s2f}, $grid[$count]{tf};
				printf LOG "%-8.3f%-8.3f%-8.3f", $grid[$count]{rex_600}, $grid[$count]{rex_500}, $grid[$count]{s2s};
				printf LOG "%-12s%-8.3f%-22s", $grid[$count]{ts}, $grid[$count]{s2}, $grid[$count]{tf_prime};
				printf LOG "%-22s\n", $grid[$count]{ts_prime};
				$count++;
			}
		}
	}
	for ( $s2s_count = 0; $s2s_count <= $#s2s; $s2s_count++ ) {
		for ( $ts_count = 0; $ts_count <= $#ts; $ts_count++ ) {
			for ( $s2f_count = 0; $s2f_count <= $#s2f; $s2f_count++ ) {
				$grid[$count]{s2f} = $s2f[$s2f_count];
				$grid[$count]{tf}  = 0;
				$grid[$count]{rex_600} = 0;
				$grid[$count]{rex_500} = 0;
				$grid[$count]{s2s} = $s2s[$s2s_count];
				$grid[$count]{ts}  = $ts[$ts_count];
				$grid[$count]{s2}  = $s2f[$s2f_count]*$s2s[$s2s_count];
				$grid[$count]{tf_prime} = $grid[$count]{tf}*$tm / ( $grid[$count]{tf} + $tm );
				$grid[$count]{ts_prime} = $grid[$count]{ts}*$tm / ( $grid[$count]{ts} + $tm );
				printf LOG "%-8s%-8.3f%-12s", $count, $grid[$count]{s2f}, $grid[$count]{tf};
				printf LOG "%-8.3f%-8.3f%-8.3f", $grid[$count]{rex_600}, $grid[$count]{rex_500}, $grid[$count]{s2s};
				printf LOG "%-12s%-8.3f%-22s", $grid[$count]{ts}, $grid[$count]{s2}, $grid[$count]{tf_prime};
				printf LOG "%-22s\n", $grid[$count]{ts_prime};
				$count++;
			}
		}
	}
}

# Create grace files.
sub create_grace {
	# S2f.
	$count = 0;
	print REXAGR "\@target G2.S0\n\@type xy\n";
	print S2SAGR "\@target G2.S0\n\@type xy\n";
	for ( $rex_count = 0; $rex_count <= $#rex_600; $rex_count++ ) {
		for ( $tf_count = 0; $tf_count <= $#tf; $tf_count++ ) {
			for ( $s2f_count = 0; $s2f_count <= $#s2f; $s2f_count++ ) {
				print REXAGR "$count\t$s2f[$s2f_count]\n";
				$count++;
			}
		}
	}
	for ( $s2s_count = 0; $s2s_count <= $#s2s; $s2s_count++ ) {
		for ( $tf_count = 0; $tf_count <= $#tf; $tf_count++ ) {
			for ( $s2f_count = 0; $s2f_count <= $#s2f; $s2f_count++ ) {
				print S2SAGR "$count\t$s2f[$s2f_count]\n";
				$count++;
			}
		}
	}
	print REXAGR "&\n";
	print S2SAGR "&\n";

	# tf.
	$count = 0;
	print REXAGR "\@target G1.S0\n\@type xy\n";
	print S2SAGR "\@target G1.S0\n\@type xy\n";
	for ( $rex_count = 0; $rex_count <= $#rex_600; $rex_count++ ) {
		for ( $tf_count = 0; $tf_count <= $#tf; $tf_count++ ) {
			for ( $s2f_count = 0; $s2f_count <= $#s2f; $s2f_count++ ) {
				print REXAGR "$count\t$tf[$tf_count]\n";
				$count++;
			}
		}
	}
	for ( $s2s_count = 0; $s2s_count <= $#s2s; $s2s_count++ ) {
		for ( $tf_count = 0; $tf_count <= $#tf; $tf_count++ ) {
			for ( $s2f_count = 0; $s2f_count <= $#s2f; $s2f_count++ ) {
				print S2SAGR "$count\t$ts[$tf_count]\n";
				$count++;
			}
		}
	}
	print REXAGR "&\n";
	print S2SAGR "&\n";

	# Rex and S2s.
	$count = 0;
	print REXAGR "\@target G0.S0\n\@type xy\n";
	print S2SAGR "\@target G0.S0\n\@type xy\n";
	for ( $rex_count = 0; $rex_count <= $#rex_600; $rex_count++ ) {
		for ( $tf_count = 0; $tf_count <= $#tf; $tf_count++ ) {
			for ( $s2f_count = 0; $s2f_count <= $#s2f; $s2f_count++ ) {
				print REXAGR "$count\t$rex_600[$rex_count]\n";
				$count++;
			}
		}
	}
	for ( $s2s_count = 0; $s2s_count <= $#s2s; $s2s_count++ ) {
		for ( $tf_count = 0; $tf_count <= $#tf; $tf_count++ ) {
			for ( $s2f_count = 0; $s2f_count <= $#s2f; $s2f_count++ ) {
				print S2SAGR "$count\t$s2s[$s2s_count]\n";
				$count++;
			}
		}
	}
	print REXAGR "&\n";
	print S2SAGR "&\n";
}

# Calculate the spectral density.
sub spect_dens {
	printf LOG "%-7s%2s%-12.1f%-6s", "$_[1]", "J(", $_[0], " rad/s) = ";
	# Loren 1:
	$top = $grid[$res]{s2}*$tm;
	$bottom = 1 + ($_[0]*$tm)**2;
	$Loren1 = $top / $bottom;

	# Loren 2:
	$top = ( 1 - $grid[$res]{s2f} )*$grid[$res]{tf_prime};
	$bottom = 1 + ( $_[0]*$grid[$res]{tf_prime} )**2;
	$Loren2 = $top / $bottom;

	# Loren 3:
	$top = ( $grid[$res]{s2f} - $grid[$res]{s2} )*$grid[$res]{ts_prime};
	$bottom = 1 + ( $_[0]*$grid[$res]{ts_prime} )**2;
	$Loren3 = $top / $bottom;

	# Spectral density value.
	$j = 2/5 * ( $Loren1 + $Loren2 + $Loren3 );
	printf LOG "%-30s\n", $j;
	return $j;
}

# Place all the grid parameters into a single file.
sub print_grid {
	printf GRID "%-8s%-3s", "Res", " | ";
	printf GRID "%-10s%-10s%-10s%-10s%-10s%-10s", "NOE(600)", "NOE(500)", "R1(600)", "R1(500)", "R2(600)", "R2(500)";
	printf GRID "%-3s", " | ";
	printf GRID "%-8s%-12s%-8s%-8s%-8s%-12s%-8s%-22s%-22s\n", "S2f", "tf", "Rex(600)", "Rex(500)", "S2s", "ts", "S2", "tf prime", "ts prime";
	for ( $res = 0; $res <= $#grid; $res++ ) {
		printf GRID "%-8s%-3s", $res, " | ";
		printf GRID "%-10.5f%-10.5f%-10.5f", $grid[$res]{noe_600}, $grid[$res]{noe_500}, $grid[$res]{r1_600};
		printf GRID "%-10.5f%-10.5f%-10.5f", $grid[$res]{r1_500}, $grid[$res]{r2_600}, $grid[$res]{r2_500};
		printf GRID "%-3s", " | ";
		printf GRID "%-8.5f%-12s%-8.5f%-8.5f", $grid[$res]{s2f}, $grid[$res]{tf}, $grid[$res]{rex_600}, $grid[$res]{rex_500};
		printf GRID "%-8.5f%-12s%-8.5f", $grid[$res]{s2s}, $grid[$res]{ts}, $grid[$res]{s2};
		printf GRID "%-22s%-22s\n", $grid[$res]{tf_prime}, $grid[$res]{ts_prime};
	}
}

# Create the NOE, R1, and R2 files for both a and b MHz.
sub create_relax_files {
	printf NOE_600 "%-8s%-8s%-15s%-15s\n", "No", "Name", "NOE", "SD";
	printf R1_600 "%-8s%-8s%-15s%-15s\n", "No", "Name", "Rate", "SD";
	printf R2_600 "%-8s%-8s%-15s%-15s\n", "No", "Name", "Rate", "SD";
	printf NOE_500 "%-8s%-8s%-15s%-15s\n", "No", "Name", "NOE", "SD";
	printf R1_500 "%-8s%-8s%-15s%-15s\n", "No", "Name", "Rate", "SD";
	printf R2_500 "%-8s%-8s%-15s%-15s\n", "No", "Name", "Rate", "SD";
	for ( $res = 0; $res <= $#grid; $res++ ) {
		printf NOE_600 "%-8s%-8s%-10.5f%-10.5f\n", $res, "XXX", $grid[$res]{noe_600}, $grid[$res]{noe_600_err};
		printf R1_600 "%-8s%-8s%-10.5f%-10.5f\n", $res, "XXX", $grid[$res]{r1_600}, $grid[$res]{r1_600_err};
		printf R2_600 "%-8s%-8s%-10.5f%-10.5f\n", $res, "XXX", $grid[$res]{r2_600}, $grid[$res]{r2_600_err};
		printf NOE_500 "%-8s%-8s%-10.5f%-10.5f\n", $res, "XXX", $grid[$res]{noe_500}, $grid[$res]{noe_500_err};
		printf R1_500 "%-8s%-8s%-10.5f%-10.5f\n", $res, "XXX", $grid[$res]{r1_500}, $grid[$res]{r1_500_err};
		printf R2_500 "%-8s%-8s%-10.5f%-10.5f\n", $res, "XXX", $grid[$res]{r2_500}, $grid[$res]{r2_500_err};
	}
}

sub close_files {
	close(LOG);
	close(GRID);
	close(REXAGR);
	close(S2SAGR);
	close(NOE_600);
	close(R1_600);
	close(R2_600);
	close(NOE_500);
	close(R1_500);
	close(R2_500);
}
