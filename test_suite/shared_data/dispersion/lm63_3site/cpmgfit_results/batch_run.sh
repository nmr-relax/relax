#! /bin/sh

cpmgfit -grid -xmgr -f spin_:1@N.in | tee spin_:1@N.out
cpmgfit -grid -xmgr -f spin_:2@N.in | tee spin_:2@N.out
