## Wrapper script for running the pipeline
#       March 2021
#       Ariana Familiar
#
#   To be run within the project directory.
#
#   EXAMPLE USAGE: ./run.sh
#
#   Alternatively could copy & paste each command into command line to run separately.

## Download data
python3 code/fw_download.py

## Delete unnecessary data
./code/delete.sh

## Rename main scans
python3 code/rename_scans.py

## Convert main scans (DICOM to Nifti/.nii.gz)
./code/convert_dicom2nifti.sh

## Run CaPTk BRATS preprocessing and auto-segmentation pipeline
./code/run_BRATS.sh

## Change segmentation values & register to T1 post-contrast
./code/change_and_reg_autoseg.sh

## Register images to T1 post-contrast
./code/reg_2_t1post.sh

## Visually inspect the registration and auto-segmentation results
##      (1) Generate images containing a series of slices of the T1 post-contrast
##      with an overlay of red edges for the given image
./code/check_reg.sh
./code/check_seg.sh

##      (2) Loop through each subject and open each image for visual inspection.
##      Opens one image and waits for user key-press in command line before opening next image.
./code/view_reg_check.sh
./code/view_seg_check.sh

## Upload results to Flywheel
python3 code/fw_upload.py

## Check Flywheel upload
python3 code/check_fw_upload.py
