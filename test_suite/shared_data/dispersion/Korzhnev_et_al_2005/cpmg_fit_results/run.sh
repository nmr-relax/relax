#! /bin/sh

rm -f backups/*
cpmg_fit < example_5.in | tee example_5.log
