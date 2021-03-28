#!/bin/bash
#
#   Created March 24, 2021
#   amf
#
#   Script for looping through images for visual inspection of registration results
#   Will open one file at a time and wait for user to make a keypress in the terminal command line
#       before opening the next image file

cd data

for sub in */ ; do
    cd ${sub}
    for ses in */ ; do
        cd ${ses}

        open reg_flair/FL_to_T1CE_registration.png
        echo "Showing ${sub} FLAIR - Press any key to continue"
        read -s -n 1

        open reg_t1_pre/T1_to_T1CE_registration.png
        echo "Showing ${sub} T1-pre - Press any key to continue"
        read -s -n 1

        open reg_t2/T2_to_T1CE_registration.png
        echo "Showing ${sub} T2 - Press any key to continue"
        read -s -n 1

        cd ..
    done
    cd ..
done

cd ..
