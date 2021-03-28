#!/bin/bash
#
#   Created March 24, 2021
#   amf
#
#   Script for looping through images for visual inspection of segmentation results
#   Will open one file at a time and wait for user to make a keypress in the terminal command line
#       before opening the next image file

cd data

for sub in */ ; do
    cd ${sub}
    for ses in */ ; do
        cd ${ses}

        if [[ -f segmentation_results.png ]]; then
            open segmentation_results.png
            echo "Showing ${sub} - Press any key to continue"
            read -s -n 1
        fi

        cd ..
    done
    cd ..
done

cd ..
