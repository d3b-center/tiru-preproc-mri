#!/bin/bash
#
#   delete unecessary acquisitions for Liquid Biopsy project

cd data
for sub in */ ; do
    cd ${sub}
    for ses in */ ; do
        cd ${ses}
        rm -r *ep2d_*
        rm -r *localizer*
        rm -r *Perfusion*
        rm -r *Images*
        rm -r *resolve*
        rm -r *asl_3d*
        rm -r *relCBF*
        rm -r *MoCoSeries*
        rm -r *Range*
        rm -r *hydro*
        cd ..
    done
    cd ..
done
cd ..

cd ..
