# Python script to upload data to Flywheel
#       uses flywheel-sdk to upload processed data
#
#   created March 24, 2021
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

# ====== user input ====== 
fw_proj_label='Liquid_Biopsy'
fw_group_label='d3b'
api_key='<insert-API-key-here>' # Flywheel API key




#  ************** REQUIRED FUNCTION(S) **************
def upload_file_to_acquistion(acquistion, fp, update=True, **kwargs):
    """Upload file to Acquisition container and update info if `update=True`
    
    Args:
        acquisition (flywheel.Acquisition): A Flywheel Acquisition
        fp (Path-like): Path to file to upload
        update (bool): If true, update container with key/value passed as kwargs.        
        kwargs (dict): Any key/value properties of Acquisition you would like to update.        
    """
    basename = os.path.basename(fp)
    if not os.path.isfile(fp):
        raise ValueError(f'{fp} is not file.')
        
    if acquistion.get_file(basename):
        return
    else:
        acquistion.upload_file(fp)
        while not acquistion.get_file(basename):   # to make sure the file is available before performing an update
            acquistion = acquistion.reload()
            time.sleep(1)
            
    if update and kwargs:
        f = acquisition.get_file(basename)
        f.update(**kwargs)



#  ************** MAIN PROCESSES **************

import flywheel
import os
import time
# import shutil

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

    ## get session directory name for this subj
    session_label=next(os.walk('data/'+sub))[1][0]

    ## get existing containers from Flywheel
    sub_cntnr = proj_cntnr.subjects.find_first(f'label={sub}')
    session = sub_cntnr.sessions.find_first(f'label={session_label}')

    ## upload main files to new acqusition containers
    ##   first, copy T1CE_rai to T1CE, just to have clean file names
    file_path='data/'+sub+'/'+session_label+'/BRATS_output/'
    if not os.path.exists(file_path+'T1CE.nii.gz'):
        shutil.copy(file_path+'T1CE_rai.nii.gz',file_path+'T1CE.nii.gz')

    files = ['T1CE.nii.gz',\
             'T1_to_T1CE.nii.gz',\
             'T2_to_T1CE.nii.gz',\
             'FL_to_T1CE.nii.gz']
    for file in files:
        acq_label=os.path.splitext(os.path.splitext(file)[0])[0] # parse label from file name (remove '.nii.gz')
        if not session.acquisitions.find_first(f'label={acq_label}'): # if acquisition doesn't already exist on Flywheel
            acquisition = session.add_acquisition(label=acq_label) # create new acquisition container
            upload_file_to_acquistion(acquisition, file_path+file)
        else:
            print('Skipping '+sub+' '+file+' upload - acquisition already exists on Flywheel!')

    ## upload images of registrations & segmentations
    file_path='data/'+sub+'/'+session_label+'/'
    acq_label='results'
    files = ['reg_flair/FL_to_T1CE_registration.png',\
             'reg_t1_pre/T1_to_T1CE_registration.png',\
             'reg_t2/T2_to_T1CE_registration.png']
    if not session.acquisitions.find_first(f'label={acq_label}'): # if acquisition doesn't already exist on Flywheel
        acquisition = session.add_acquisition(label=acq_label) # create new acquisition container
        for file in files:
            upload_file_to_acquistion(acquisition, file_path+file)

        if os.path.exists(file_path+'segmentation_results.png'):
            upload_file_to_acquistion(acquisition, file_path+'segmentation_results.png')
    else:
        print('Skipping '+sub+' images upload - results already exist on Flywheel!')

    ## auto seg results
    ##   fw.delete_acquisition(acquisition.id)
    if os.path.exists(file_path+'segmentation_results.png'):
        file_path='data/'+sub+'/'+session_label+'/BRATS_output/'
        file='brainTumorMask_to_T1CE.nii.gz'
        acquisition=fw.lookup(fw_group_label+'/'+fw_proj_label+'/'+sub+'/'+session_label+'/'+acq_label)
        # fw.delete_acquisition_file(acquisition.id,file)
        upload_file_to_acquistion(acquisition, file_path+file)
    else:
        print('Skipping '+sub+' auto-seg results upload - no results for this subject!')

    ## zip BRATS-output folder & upload
    # file_path='data/'+sub+'/'+session_label+'/'
    # if not os.path.exists(file_path+'BRATS_output.tar.gz'): # acquistion.get_file(basename)
    #     file_path='data/'+sub+'/'+session_label+'/BRATS_output/'
    #     file_name='BRATS_output.tar'
    #     # shutil.make_archive(file_path, 'zip', 'data/'+sub+'/'+session_label)
    #     target='data/'+sub+'/'+session_label+'/'+file_name
    #     os.system("tar -cvf "+target+" "+file_path)
    #     os.system("gzip "+target)
    #     acquisition=fw.lookup(fw_group_label+'/'+fw_proj_label+'/'+sub+'/'+session_label+'/'+acq_label)
    #     upload_file_to_acquistion(acquisition, target+'.gz')
    # else:
    #     print('Skipping '+sub+' zip upload - no file found!')

