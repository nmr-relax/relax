#! /usr/bin/perl -w

# parameters.pm   v1.1                  31 August 2001        Edward d'Auvergne
#
# Module containing all the parameters used by the script modelfree.pl
# Make sure the version numbers between the two scripts are identical

package parameters;
require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(
	$SSEtile
	$Ftest_lim
	$largeSSE
	$pdb_file
	$pdb_path
	$pdb_full
	$diff
	$no_sim
	$trim
	%tm
	%dratio
	%theta
	%phi
	%const
	%vector
	%md1
);


$SSEtile = "0.90";       # Set the SSE limit (1 - alpha critical value).
$Ftest_lim = "0.80";     # Set the F-test limit (1 - alpha critical value).
$largeSSE = 20;          # Set the SSE limit for when much greater than the SSE limit.

# run file parameters:
$pdb_file = "Ap4Aase_new_3.pdb";
$pdb_path = "../../";
$pdb_full = $pdb_path . $pdb_file;

# mfin file parameters:
$diff = "isotropic";
$no_sim = "500";
$trim = 0;               # Trim unconverged simulations.
%tm = (
	val   => "11.09",
	flag  => 1,
	bound => 2,
	lower => "9.0",
	upper => "13.0",
	steps => 100,
);
%dratio = (
	val   => "1.123",
	flag  => 1,
	bound => 0,
	lower => 0.6,
	upper => 1.5,
	steps => 5,
);
%theta = (
	val   => "87.493",
	flag  => 1,
	bound => 0,
	lower => -90,
	upper => 90,
	steps => 10,
);
%phi = (
	val   => "-52.470",
	flag  => 1,
	bound => 0,
	lower => -90,
	upper => 90,
	steps => 10,
);
# mfpar file parameters:
%const = (
	nucleus => "N15",
	gamma   => "-2.710",
	rxh     => "1.020",
	csa     => "-170.00",
);
%vector = (
	atom1 => "N",
	atom2 => "H",
);

# mfmodel file parameters:
%md1 = (
	tloc => {
		start => "0.0",
		flag  => 0,
		bound => 2,
		lower => "0.000",
		upper => "20.000",
		steps => 20,
	},
	theta => {
		start => "0.0",
		flag  => 0,
		bound => 2,
		lower => "0.000",
		upper => "90.000",
		steps => 20,
	},
	sf2 => {
		start => "1.0",
		flag  => 0,
		bound => 2,
		lower => "0.000",
		upper => "1.000",
		steps => 20,
	},
	ss2 => {
		start => "1.0",
		flag  => 0,
		bound => 2,
		lower => "0.000",
		upper => "1.000",
		steps => 20,
	},
	te => {
		start => "0.0",
		flag  => 0,
		bound => 2,
		lower => "0.000",
		upper => "5000.000",
		steps => 25,
	},
	rex => {
		start => "0.0",
		flag  => 0,
		bound => -1,
		lower => "0.000",
		upper => "20.000",
		steps => 20,
	}
);

1;     # What the???  Perl module needs to return true!
