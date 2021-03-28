#!/bin/bash
#
#	https://cbica.github.io/CaPTk/preprocessing_brats.html
#	NOTE: This applications takes ~30 minutes to finish on an 8-core Intel i7 with 16GB of RAM.
#
#	1. Re-orientation
#	2. rigid registration to atlas ([bias correction], post>atlas, pre/flair/t2>post)
#	3. normalization
#	4. DL skull strip (DeepMedic)
#	5. DL tumor segementation (DeepMedic, trained on BRaTS 2017)
#
#
#		REQUIRES: CaPTk

cd data

for sub in */ ; do
	cd ${sub}
	for ses in */ ; do
		cd ${ses}

		mkdir BRATS_output

		BraTSPipeline \
			-t1 T1_pre.nii.gz \
			-t1c T1_post.nii.gz \
			-t2 T2.nii.gz \
			-fl T2_flair.nii.gz \
			-o BRATS_output

		cd ..
	done
	cd ..
done

cd ..