#!/bin/bash
#   Converts DICOM files in specified directory to Nifti (.nii.gz)
#   
#   REQUIRES dcm2niix

cd data

for sub in */ ; do
    cd $sub
    for ses in */ ; do
        cd $ses

        dcm2niix -f T1_pre -z y -o . T1_pre/
        dcm2niix -f T1_post -z y -o . T1_post/
        dcm2niix -f T2 -z y -o . T2/
        dcm2niix -f T2_flair -z y -o . T2_flair/

        cd ..
    done
    cd ..
done

cd ..