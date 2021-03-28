# Pipeline for brain tumor MRI processing
## &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Ariana Familiar
## &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; March 2021

This processing pipeline contains code for executing existing pre-processing and auto-tumor segmentation of MR images using the built-in BRATS-preprocessing command in the open-source [CaPTk software](https://cbica.github.io/CaPTk/preprocessing_brats.html). Pre-processing involves orientation to RAI (Right-Anterior-Inferior) coordinates, co-registration, and skull stripping. Tumor segmentation is carried out by the DeepMedic auto-segmentation tool using the trained convolutional neural network model from the BRATS 2017 challenge.


Additionally, all final images are registered to the post-contrast T1 image using transformation matrices that are output by the BRATS-preprocessing command.


The functionality of each script is described in the following sections. Required software is listed below and within each script. Python code written for Python 3.



## <u> Download data from Flywheel </u>

Python script that downloads sessions or specific files from Flywheel. Requires a CSV input containing a list of the subjects and corresponding sessions to download (see subj_list.csv). Depending on the input "files" variable, either the entire session (if "files" is empty), or specified files are downloaded. Restructures downloaded data into the following directory structure:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; data/

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   ├ sub-01/

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   | └ session/

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   |   ├ acquisition-01

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   |   ├ acquisition-02

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   |   └ acquisition-N

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   ├ sub-02/

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;   └ sub-N/

Subsequent processes require the data to be structured in this manner.

Required package: flywheel-sdk



## <u> (optional) Delete unnecessary acquisitions </u>

Bash script that deletes unnecessary acquisition files (e.g., to clear local storage space and clean up session directories). The files-to-delete are defined within the script.



## <u> Rename main scans </u>

Python script to rename 4 main scans (t1, t1 post-contrast, t2, flair) based on expected file names, so that they match across subjects. Uses SeriesNumber DICOM tag to sort t1-mprage into pre/post contrast based on order of acquisitons. Subjects that do not match expected file names are hard-coded.

If modifying this for a new dataset, make sure to check hard-coded subjects and subjects with more than 1 t1-mprage file to make sure the correct acquisitions get renamed.

Required package: pydicom



## <u> Convert main scans (DICOM to nifti) </u>

Bash script that converts 4 main scans from DICOM to Nifti (.nii.gz) using Chris Rorden's [dcm2niix](https://github.com/rordenlab/dcm2niix) tool.



## <u> Run CaPTk pre-processing & auto-segmentation pipeline </u>

Bash script that inputs 4 main scans to the CaPTk command to run the built-in BRATS pipeline. Output is placed in directory "BRATS_output/" within each subject's session folder.

Command outputs each main scan, re-oriented to standard RAI coordinates and registered to the SRI atlas (FL_to_SRI.nii.gz, T1_to_SRI.nii.gz, T1CE_to_SRI.nii.gz, T2_to_SRI.nii.gz) as well as intermediate files (e.g., skull-stripped images). Additionally, transformation matrices for each registration step are output as .mat files.

The auto-segmentation results are in the output file brainTumorMask_SRI.nii.gz that has 4 possible labels (1 = necrotic core, 2 = edema, 3 = non-enhancing core, 4 = enhancing core). If the model did not find any regions for the given image this file will contain all zeros.

Required software: CaPTk (binaries)



## <u> Change auto-segmentation label values & register it to T1 post-contrast </u>

Bash script to change segmentation label values to new mapping & apply the registration to the segmentation results to T1 post-contrast (using the inverse of the transformation matrix T1CE_to_SRI.mat).

The original mask (brainTumorMask_SRI.nii.gz) is split into 4 separate files, one per label (1-4), and changed to the new target label value (specific to D3b research projects). Each file is then registered to the T1 post-contrast image. Because the interpolation results in non-integer values (at edges of the segmented region) the registered mask images are then thresholded to exclude any values above or below the new target labels. The resulting files are then combined back into a single mask image (brainTumorMask_to_T1CE.nii.gz).

Required software: FSL, greedy (part of CaPTk install)



## <u> Register scans to T1 post-contrast </u>

Bash script to register the 3 main images (T1 pre-contrast, T2, flair) to T1 post-contrast using the existing (affine) transformation matrices from the BRATS pipeline. Inputs are the re-oriented (RAI) images in the BRATS_output/ directory (FL_rai.nii.gz, T2_rai.nii.gz, T1_rai.nii.gz, T1CE_rai.nii.gz), outputs are the registered-to-T1-post images (FL_to_T1CE.nii.gz, T2_to_T1CE.nii.gz, T1_to_T1CE.nii.gz).

Required package: greedy (part of CaPTk install)



## <u> Visually check registration & auto-segmentation results </u>

(1) Bash scripts that generate images of slices for checking each registration (reg_flair/FL_to_T1CE_registration.png, reg_t1_pre/T1_to_T1CE_registration.png, reg_t2/T2_to_T1CE_registration.png), as well as the auto-segmentation results ("segmentation_results.png") within each subject's session directory. Additionally, a CSV file (no_auto_seg_results.csv) is generated containing a list of subjects with no auto-segmentation results (i.e., brainTumorMask_to_T1CE.nii.gz contains no labeled voxels).

(2) Bash scripts to loop through each subject and open the images generated in #1. Waits for user's key press (any key) in command line to open each image. Prints current subject directory (C-ID) to command line (for user to reference).

Required software: FSL (for #1)



## <u> Upload results to Flywheel </u>

Python script to upload results files (T1CE.nii.gz, T1_to_T1CE.nii.gz, T2_to_T1CE.nii.gz, FL_to_T1CE.nii.gz, brainTumorMask_to_T1CE.nii.gz) and PNG images (places all images into a "results" acquisition) for each subject to Flywheel. Expects the acquisitions to not already exist on Flywheel (otherwise skips).

Required package: flywheel-sdk



## <u> (optional) Check that upload was successful </u>

Python script to check that all results were uploaded to Flywheel. Prints QA info (missing files) to the command line.

Required package: flywheel-sdk
