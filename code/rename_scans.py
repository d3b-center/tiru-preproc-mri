# Setup for Liquid Biopsy - batch 2
#      Renames the directories so proper naming in subsequent DICOM>Nifti conversion
#   March 2021
#   amf
#
#       REQUIRES: pydicom

import pydicom
import csv
import os

sub_ids=next(os.walk('data/'))[1]


## First, find FLAIR, T2, and T1-mprage scans based on expected file names
flair_paths=[]
t2_paths=[]
t1_paths=[]
for (root, __, __) in os.walk('data/'):
    ##   FLAIR
    if 'tra_dark-fluid' in root or \
        'T2 FLAIR AXIAL' in root or \
        'ax flair mpr' in root:
        flair_paths.append(root)
    if 'T2 FLAIR COR' in root and \
        'data/C2832936/5949d_B_brain' in os.path.split(root)[0]:
        flair_paths.append(root)

    ##   T2
    if 't2_tse_tra' in root or \
        'Ax T2' in root :
        T2=1
        t2_paths.append(root)

    ##   T1
    if 't1_mprage' in root:
        t1_paths.append(root)

## Split t1-mprage files into pre/post-gad & rename directories
num_tag = pydicom.tag.Tag(int('0020', 16), int('0011', 16)) # series number tag
for sub in sub_ids:

    ## this section is for handling 4 specific subjects that did not match the expected file names
    if 'C2832936' in sub:
        os.rename('data/C2832936/5949d_B_brain/T1 MPR SAG 0.9 MM recon trans 2mm', \
                  'data/C2832936/5949d_B_brain/T1_pre')
        os.rename('data/C2832936/5949d_B_brain/t1_mpr_tra_iso', \
                  'data/C2832936/5949d_B_brain/T1_post')
    elif 'C2795298' in sub:
        os.rename('data/C2795298/3520d_BP_brain_pituitary/T1 MPR SAG 0.9 MM recon trans 2mm_0', \
                  'data/C2795298/3520d_BP_brain_pituitary/T1_pre')
        os.rename('data/C2795298/3520d_BP_brain_pituitary/T1 MPR SAG 0.9 MM recon trans 2mm', \
                  'data/C2795298/3520d_BP_brain_pituitary/T1_post')
    elif 'C2774265' in sub:
        os.rename('data/C2774265/2195d_B_brain/t1_mprage_sag_p2_iso', \
                  'data/C2774265/2195d_B_brain/T1_pre')
        os.rename('data/C2774265/2195d_B_brain/Ax T1 MPRAGE', \
                  'data/C2774265/2195d_B_brain/T1_post')
    elif 'C2624574' in sub:
        os.rename('data/C2624574/1040d_B_brain/T1 MPR SAG 0.9 MM recon trans 2mm', \
                  'data/C2624574/1040d_B_brain/T1_pre')
        os.rename('data/C2624574/1040d_B_brain/T1 MPR SAG 0.9 MM recon tran&cor 2mm', \
                  'data/C2624574/1040d_B_brain/T1_post')

    ## for the rest of the subjects, find the SeriesNumber DICOM tag (describes order of scan acquisitions)
    ## for both t1 files. Then, use this value to figure out which one is pre-contrast (lower SeriesNumber)
    ## and which one is post-contrast (higher SeriesNumber)
    series_nums=[]
    fn_paths = list(filter(lambda x: sub in x, t1_paths)) # grab paths for this sub
    if len(fn_paths) == 2:
        for fn_path in fn_paths:
            ds = pydicom.dcmread(fn_path+'/'+os.listdir(fn_path)[0]) # grab first DICOM file in the folder
            series_nums.append(int(ds[num_tag].value)) # grab series number from DICOM tag
        ## label the earlier acq 'pre' and later acq 'post'
        if series_nums[0]<series_nums[1]: # pre, post
            os.rename(fn_paths[0], os.path.split(fn_paths[0])[0]+'/T1_pre')
            os.rename(fn_paths[1], os.path.split(fn_paths[1])[0]+'/T1_post')
        elif series_nums[1]<series_nums[0]: # post, pre
            os.rename(fn_paths[0], os.path.split(fn_paths[0])[0]+'/T1_post')
            os.rename(fn_paths[1], os.path.split(fn_paths[1])[0]+'/T1_pre')
    elif len(fn_paths) == 3: # checked that this works for this specific group (subj's w/3 t1-mprage files)
        os.rename(fn_paths[0], os.path.split(fn_paths[0])[0]+'/T1_pre')
        os.rename(fn_paths[1], os.path.split(fn_paths[1])[0]+'/T1_post')

##  rename FLAIR & T2 file directories
for subs in range(len(sub_ids)): # should base this on len(file names) instead
    # FLAIR
    if not os.path.isdir(os.path.split(flair_paths[subs])[0]+'/T2_flair'):
        os.rename(flair_paths[subs], os.path.split(flair_paths[subs])[0]+'/T2_flair')
    # T2
    if not os.path.isdir(os.path.split(t2_paths[subs])[0]+'/T2'):
        os.rename(t2_paths[subs], os.path.split(t2_paths[subs])[0]+'/T2')



## QA: check if the number of files that match expected names EQUALS the number of subjects in the dataset
T1_pre=0
T1_post=0
T2=0
FLAIR=0
for (root, __, __) in os.walk('data/'):
    if os.path.split(root)[1]=='T1_pre':
        T1_pre=T1_pre+1
    elif os.path.split(root)[1]=='T1_post':
        T1_post=T1_post+1
    elif os.path.split(root)[1]=='T2':
        T2=T2+1
    elif os.path.split(root)[1]=='T2_flair':
        FLAIR=FLAIR+1
print('T1-pre: '+str(T1_pre))
print('T1-post: '+str(T1_post))
print('T2: '+str(T2))
print('FLAIR: '+str(FLAIR))



