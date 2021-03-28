#!/bin/bash
#
#   Created March 24, 2021
#   amf
#
#   Script for generating images of registration results using FSL's slicesdir command
#
#       REQUIRES FSL


cd data

for sub in */ ; do
    cd ${sub}
    for ses in */ ; do
        cd ${ses}

        rm -r reg_flair
        rm -r reg_t1_pre
        rm -r reg_t2

        # FLAIR
        slicesdir -p BRATS_output/FL_to_T1CE.nii.gz BRATS_output/T1CE_rai.nii.gz
        mv slicesdir reg_flair
        mv reg_flair/BRATS_output_T1CE_rai.png reg_flair/FL_to_T1CE_registration.png 

        # T1 (pre)
        slicesdir -p BRATS_output/T1_to_T1CE.nii.gz BRATS_output/T1CE_rai.nii.gz
        mv slicesdir reg_t1_pre
        mv reg_t1_pre/BRATS_output_T1CE_rai.png reg_t1_pre/T1_to_T1CE_registration.png 

        # T2
        slicesdir -p BRATS_output/T2_to_T1CE.nii.gz BRATS_output/T1CE_rai.nii.gz
        mv slicesdir reg_t2
        mv reg_t2/BRATS_output_T1CE_rai.png reg_t2/T2_to_T1CE_registration.png 

        cd ..
    done
    cd ..
done

cd ..


