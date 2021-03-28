# Python script to check that data was properly uploaded to Flywheel
#
#   created March 28, 2021
#   amf
#
#       Based on: https://docs.flywheel.io/hc/en-us/articles/1500001422482-Upload-Data-To-A-New-Project
#
#   INPUTS:
#     fw_proj_label         name of Flywheel project to download data from (user must have appropriate read permissions for this project)
#     fw_group_label        name of Flywheel group that the project is associated with
#     api_key               user's unique Flywheel api key
#
#
#           REQUIRED DEPENDENCIES:  flywheel-sdk
#
#   To do: create corresponding functions

# ====== user input ====== 
fw_proj_label='Liquid_Biopsy'
fw_group_label='d3b'
api_key='<insert-API-key-here>'




#  ************** MAIN PROCESSES **************

import flywheel
import os

# ====== access the flywheel client for the instance ====== 
fw = flywheel.Client(api_key)

# ====== loop through subjects & upload files to Flywheel ====== 
## get existing containers from Flywheel
grp_cntnr = fw.lookup(fw_group_label)
proj_cntnr = grp_cntnr.projects.find_first(f'label={fw_proj_label}')

## get list of all subject folders in data/
sub_ids=next(os.walk('data/'))[1]
# sub_ids=['C136653'] # for debugging

for sub in sub_ids:
    missing=0
    ## get session directory name for this subj
    session_label=next(os.walk('data/'+sub))[1][0]

    ## get existing containers from Flywheel
    sub_cntnr = proj_cntnr.subjects.find_first(f'label={sub}')
    session = sub_cntnr.sessions.find_first(f'label={session_label}')

    ## check main files
    files = ['T1CE.nii.gz',\
             'T1_to_T1CE.nii.gz',\
             'T2_to_T1CE.nii.gz',\
             'FL_to_T1CE.nii.gz']
    for file in files:
        file_exists=0
        acq_label=os.path.splitext(os.path.splitext(file)[0])[0] # parse label from file name (remove '.nii.gz')
        acquisition = session.acquisitions.find_first(f'label={acq_label}')
        if not acquisition:
            print(sub+': acquisition labeled '+acq_label+' does not exist on Flywheel!')
            missing = missing+1
        else:
            for acq_files in acquisition.files: # each file has corresponding dictionary
                this_dict = acq_files
                for k, v in this_dict.items():
                    if k=='name' and v==file:
                        file_exists=1
            if file_exists==0:
                print(sub+': acquisition labeled '+acq_label+' exists on Flywheel but no corresponding file found!')
                missing = missing+1

    ## check images of registrations
    acq_label='results'
    files = ['FL_to_T1CE_registration.png',\
             'T1_to_T1CE_registration.png',\
             'T2_to_T1CE_registration.png']
    acquisition = session.acquisitions.find_first(f'label={acq_label}')
    if not acquisition:
        print(sub+': acquisition labeled '+acq_label+' does not exist on Flywheel!')
        missing = missing+1
    else:
        for file in files:
            file_exists=0
            for acq_files in acquisition.files: # each file has corresponding dictionary
                this_dict = acq_files
                for k, v in this_dict.items():
                    if k=='name' and v==file:
                        file_exists=1
            if file_exists==0:
                print(sub+': acquisition labeled '+acq_label+' exists on Flywheel but '+file+' not found!')
                missing = missing+1

        ## check image of segmentation (if expected to exist)
        file_path='data/'+sub+'/'+session_label+'/'
        if os.path.exists(file_path+'segmentation_results.png'):
            file = 'segmentation_results.png'
            file_exists=0
            for acq_files in acquisition.files: # each file has corresponding dictionary
                this_dict = acq_files
                for k, v in this_dict.items():
                    if k=='name' and v==file:
                        file_exists=1
            if file_exists==0:
                print(sub+': acquisition labeled '+acq_label+' exists on Flywheel but '+file+' not found!')
                missing = missing+1

    ## check auto-seg file
    if os.path.exists(file_path+'segmentation_results.png'):
        file = 'brainTumorMask_to_T1CE.nii.gz'
        acq_label = os.path.splitext(os.path.splitext(file)[0])[0] # parse label from file name (remove '.nii.gz')
        acquisition = session.acquisitions.find_first(f'label={acq_label}')
        if not acquisition:
            print(sub+': acquisition labeled '+acq_label+' does not exist on Flywheel!')
            missing = missing+1
        else:
            file_exists=0
            for acq_files in acquisition.files: # each file has corresponding dictionary
                this_dict = acq_files
                for k, v in this_dict.items():
                    if k=='name' and v==file:
                        file_exists=1
            if file_exists==0:
                print(sub+': acquisition labeled '+acq_label+' exists on Flywheel but no corresponding file found!')
                missing = missing+1

    print(sub+' is missing '+str(missing)+' files')
