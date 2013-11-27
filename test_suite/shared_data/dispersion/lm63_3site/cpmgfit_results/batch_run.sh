#! /bin/sh

cpmgfit -grid -xmgr -f spin_1_N.in | tee spin_1_N.out
cpmgfit -grid -xmgr -f spin_2_N.in | tee spin_2_N.out
