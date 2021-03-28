#   (1) Maps tissue labels from BRATS output to target label descriptions for subsequent editing in ITK-snap
#   (2) Registers resulting mask to T1CE
#
#   Input labels (BRATS-preproc output):
#       1 = necrotic core
#       2 = edema
#       3 = non-enhancing core
#       4 = enhancing core
#
#   Output labels:
#       1 = enhancing core
#       2 = non-enhancing core
#       3 = cystic (core)
#       (4 = cystic (reactive))
#       5 = edema
#
#   REQUIRES: FSL, greedy

cd data

for sub in */ ; do
    cd ${sub}
    for ses in */ ; do
        cd ${ses}

        # rm BRATS_output/brainTumorMask_SRI_newLabels.nii.gz
        rm BRATS_output/brainTumorMask_to_T1CE.nii.gz

        im=BRATS_output/brainTumorMask_SRI.nii.gz
        range=`fslstats $im -R`
        max=${range:9:10}
        if [[ ${max:0:1} == 0 ]]; then # if there are no labels in the BRATS segmentation file, write C-ID to CSV
            echo "Skipping $sub - no auto-seg results!"
        else
            # split mask file into separate files per layer & adjust the label value according to new mapping
            for label in {1..4} ; do
                file=BRATS_output/temp_brainTumorMask_SRI_${label}.nii.gz
                if [[ ${label} == 1 ]] ; then # 1 > 3
                    new_label=3
                    fslmaths ${im} -thr ${label} -uthr ${label} ${file} # grab only voxels with this value
                    fslmaths ${file} -add 2 -thr ${new_label} ${file} # transform it accordingly
                elif [[ ${label} == 2 ]] ; then # 2 > 5
                    new_label=5
                    fslmaths ${im} -thr ${label} -uthr ${label} ${file}
                    fslmaths ${file} -add 3 -thr ${new_label} ${file}
                elif [[ ${label} == 3 ]] ; then # 3 > 2
                    new_label=2
                    fslmaths ${im} -thr ${label} -uthr ${label} ${file}
                    fslmaths ${file} -sub 1 -thr ${new_label} ${file}
                elif [[ ${label} == 4 ]] ; then # 4 > 1
                    new_label=1
                    fslmaths ${im} -thr ${label} -uthr ${label} ${file}
                    fslmaths ${file} -sub 3 -thr ${new_label} ${file}
                fi

                # register to T1CE
                reg_file=BRATS_output/temp_brainTumorMask_SRI_${label}_reg.nii.gz
                greedy -d 3 -rf BRATS_output/T1CE_rai.nii.gz \
                        -rm ${file} ${reg_file} -r BRATS_output/T1CE_to_SRI.mat,-1

                # thresold to remove all non-integer values (b/c interpolation during registration
                #   causes )
                fslmaths ${reg_file} -thr ${new_label} -uthr ${new_label} ${reg_file}

            done

            # combine new layers back into single file
            fslmaths BRATS_output/temp_brainTumorMask_SRI_1_reg.nii.gz -add \
                     BRATS_output/temp_brainTumorMask_SRI_2_reg.nii.gz -add \
                     BRATS_output/temp_brainTumorMask_SRI_3_reg.nii.gz -add \
                     BRATS_output/temp_brainTumorMask_SRI_4_reg.nii.gz \
                     BRATS_output/brainTumorMask_to_T1CE.nii.gz

            # remove separate layer files
            rm temp_*

            echo "Done: $sub"
        fi

        cd ..
    done
    cd ..
done

cd ..

