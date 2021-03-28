#!/bin/bash
#
#   Created March 24, 2021
#   amf
#
#   Script for generating images of segmentation results using FSL's slicer command
#   & logging subjects with no successful auto-seg results ("no_auto_seg_results.csv" output)
#
#       REQUIRES FSL

function slice_the_image () {
    #####################################################################

    #Required : $1 -  .nii(.gz) from which creates a 4x6 montage.
    #Required : $2 -  .nii(.gz) to overlay in red outline on $1.
    #Optional:
    #   $3 - Bottom slice to include. Default 0 [100].
    #   $4 - Top slice to include.  Default 130 [230].
    #Christopher Benjamin May 13 2018
    #   Modified March 24 2021 by Ariana Familiar
#   https://cogneuro.net/imaging-resources/2018/5/14/fmri-create-a-single-montage-png-from-a-nifti-nii-in-fsl

    #####################################################################

    ## Specify inputs.

    #####################################################################

    image_to_slice=$1
    image_to_overlay=$2

    #Count the number of slices in your image
    number_of_slices=`fslval $image_to_slice dim3`

    #Specify the upper and lower-most slices you want to cut.
    if [ -z $3 ] ; then
      slice_bottom=0;   #Slice you will start slicing from
    else
      slice_bottom=$3;
    fi
    if [ -z $4 ] ; then
      slice_top=130;      #Slice you will stop slicing at
    else
      slice_top=$4;
    fi

    #Calculate the number of actual slices of brain you want to slice from.
    dead_space_above_brain=`echo "$number_of_slices-$slice_top" | bc -l`
    n_slices_of_actual_brain=`echo "$number_of_slices-$slice_bottom-$dead_space_above_brain" | bc -l`

    #Calculate the max spacing necessary to allow 24 slices to be cut
    let slice_increment=($n_slices_of_actual_brain+24-1)/24

    #####################################################################

    ## Run loop to slice and stitch montage

    #####################################################################

    count=1
    col_count=7
    row=0

    #Slice the image.
    for (( N = $slice_bottom; N <= $slice_top; N += $slice_increment )); do
      FRAC=$(echo "scale=2; $N / $number_of_slices" | bc -l);
      # slicer "$image_to_slice" -L -z $FRAC "${image_to_slice}_$count.png";
      slicer "$image_to_slice" "$image_to_overlay" -L -z $FRAC "${image_to_slice}_$count.png";

      #Add current image to a row.
      #If you have the first image of a new row (i.e., column 7), create new row
      if [[ $col_count == 7 ]] ; then
        row=$(echo "${row}+1" | bc -l);
        mv "${image_to_slice}_$count.png" montage_row$row.png
        col_count=2;
        just_started_a_new_row=1;
      #Otherwise, append your image to the existing row.
      else
        pngappend montage_row$row.png + "${image_to_slice}_$count.png" montage_row$row.png
        col_count=$(echo "${col_count}+1" | bc -l);
        just_started_a_new_row=0;
        rm "${image_to_slice}_$count.png"
      fi
      count=$(echo "${count}+1" | bc -l);
    done

    #####################################################################

    ## Stitch your rows into a single montage

    #####################################################################

    label=`basename $output_file .nii.gz`

    mv montage_row1.png segmentation_results.png
    pngappend segmentation_results.png - montage_row2.png segmentation_results.png
    pngappend segmentation_results.png - montage_row3.png segmentation_results.png
    pngappend segmentation_results.png - montage_row4.png segmentation_results.png
    rm montage_row*

}



log_fn=no_auto_seg_results.csv
rm ${log_fn}
echo "C-ID" > ${log_fn}

cd data

for sub in */ ; do
    cd ${sub}
    for ses in */ ; do
        cd ${ses}

        im=BRATS_output/brainTumorMask_T1CE.nii.gz
        range=`fslstats $im -R`
        max=${range:9:10}
        if [[ ${max:0:1} == 0 ]]; then # if there are no labels in the BRATS segmentation file, write C-ID to CSV
            echo "$sub" >> ../../../${log_fn}
        else
            z_sz=`fslval BRATS_output/T1CE_rai.nii.gz dim3`
            let top_slice=z_sz-20
            slice_the_image "BRATS_output/T1CE_rai.nii.gz" "${im}" 40 $top_slice
        fi

        echo "Done: ${sub}"

        cd ..
    done
    cd ..
done

cd ..



# background_image=data/C136653/3503d_B_brain/BRATS_output/T1CE_to_SRI.nii.gz
# overlay_image=data/C136653/3503d_B_brain/BRATS_output/brainTumorMask_SRI.nii.gz
# output_file=output

# Usage: overlay <colour_type> <output_type> [-c] 
#           <background_image> <bg_min> <bg_max>
#           <stat_image_1> <s1_min> <s1_max>
#           [stat_image_2 s2min s2max]
#           <output_image> [cbartype] [cbarfilename]
# colour_type: 0=solid 1=transparent colours
# output_type: 0=floating point (32 bit real) 1=integer (16 bit signed integer)
# -c : use checkerboard mask for overlay
# <bg_min> <bg_max> can be replaced by -a for automatic estimation of background display range or -A to use the full image range
# valid cbartypes colours are: ybg, valid cbartypes options are: s (stack) 

# overlay 1 0 ${background_image} -a ${overlay_image} 0 9 ${output_file}

# This adds overlay as red outline:
# slicer ${background_image} ${overlay_image} -a ${output_file}.png
