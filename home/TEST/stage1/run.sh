#!/bin/sh

echo
echo "Queuing modelfree runs"

cd m1
echo
echo "Running model 1"
./run >> output

cd ../m2
echo
echo "Running model 2"
./run >> output

cd ../m3
echo
echo "Running model 3"
./run >> output

cd ../m4
echo
echo "Running model 4"
./run >> output

cd ../m5
echo
echo "Running model 5"
./run >> output

cd ../f-m1m2
echo
echo "Running the F-tests between models 1 and 2"
./run >> output

cd ../f-m1m3
echo
echo "Running the F-tests between models 1 and 3"
./run >> output

cd ../f-m2m4
echo
echo "Running the F-tests between models 2 and 4"
./run >> output

cd ../f-m2m5
echo
echo "Running the F-tests between models 2 and 5"
./run >> output

cd ../f-m3m4
echo
echo "Running the F-tests between models 3 and 4"
./run >> output

cd ..
ls m*/mfout f*/mfout

echo "Finished all runs!"
