#!/bin/bash
#
#	Apply affine transformation matrix (output of BRATS-preproc pipeline)
#
#		REQUIRES greedy

cd data

for sub in */ ; do
	cd ${sub}
	for ses in */ ; do
		cd ${ses}

		cd BRATS_output
		# ====== apply reg matrix to orig images ====== 
		#	https://sites.google.com/view/greedyreg/quick-start
		# rf = fixed
		# rm = moving
		# inverse affine: -r affine.mat,-1
		greedy -d 3 -rf T1CE_rai.nii.gz -rm FL_rai.nii.gz FL_to_T1CE.nii.gz -r FL_to_T1CE.mat # FLAIR
		greedy -d 3 -rf T1CE_rai.nii.gz -rm T2_rai.nii.gz T2_to_T1CE.nii.gz -r T2_to_T1CE.mat # T2
		greedy -d 3 -rf T1CE_rai.nii.gz -rm T1_rai.nii.gz T1_to_T1CE.nii.gz -r T1_to_T1CE.mat # T1 pre-contrast

		cd ..

		cd ..
	done
	cd ..
done

cd ..