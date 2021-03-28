# Python function to download session data from Flywheel
#       uses flywheel-sdk to download data based on a user inputted list (CSV)
#
#   created March 23, 2021
#   amf
#
#   INPUTS:
#     input_fn              CSV file with subjects and sessions to download
#                               - should include header row ("C_ID","Session")
#                               - each subsequent row should correspond to one subject
#     fw_proj_label         name of Flywheel project to download data from (user must have appropriate read permissions for this project)
#     fw_group_label        name of Flywheel group that the project is associated with
#     api_key               user's unique Flywheel api key
#     files                 list of nifti acquisitions to download (assumes acquisition label matches file name)
#                               If not specified, downloads entire session
#     include (optional)    list of file types to include, e.g., ['dicom'], or ['nifti'] - only if "files" is empty
#     exclude (optional)    list of file types to exclude - only if "files" is empty
#
#   OUTPUT:
#     data/ directory with one folder per subject
#
#           REQUIRED DEPENDENCIES:  flywheel-sdk

# ====== user input ====== 
api_key='<insert-API-key-here>' # Flywheel API key

input_fn="subj_list.csv" # CSV file name
fw_proj_label='Liquid_Biopsy'
fw_group_label='d3b'
files=['T1CE.nii.gz','T1_to_T1CE.nii.gz','T2_to_T1CE.nii.gz','FL_to_T1CE.nii.gz','brainTumorMask_to_T1CE.nii.gz'] # files to download
# include=['nifti'] # file types to include (optional, if not specified will download all available)
# exclude=[''] # file types to exclude (optional) 


#  ************** MAIN PROCESSES **************
import csv
import flywheel
import tarfile
import os
import shutil

# ====== access the flywheel client for the instance ====== 
fw = flywheel.Client(api_key)

# ====== load subj list CSV file ====== 
input_file = csv.DictReader(open(input_fn, "r", encoding="utf-8-sig"))

#   loop through each subject/session (each row in input file)
#   if this subject's directory doesn't already exist, make a new one
#   and download their data
for row in input_file:
    c_id = row["C_ID"]
    session = row["Session"]

    if not os.path.isdir('data/'+c_id): # if the subject's directory doesn't already exist
        if not os.path.isdir('data'):
            os.makedirs('data')

        # ====== download this subj's data from Flywheel ======
        session_ptr = fw.lookup(fw_group_label+'/'+fw_proj_label+'/'+c_id+'/'+session)

        if files==None or files==['']:
            session_ptr.download_tar('data/'+c_id+'.tar', include_types=include, exclude_types=exclude) # exclude_types=['dicom'] (optional, list)

            # ====== clean up file/dir structure ====== 
            #   unzip & delete the .tar
            my_tar = tarfile.open('data/'+c_id+'.tar')
            my_tar.extractall('./data/'+c_id) # specify which folder to extract to
            my_tar.close()
            os.remove('data/'+c_id+'.tar')

            #   remove uncessary nested directories
            #   this is set up to be specific to the Flywheel directory structure:
            #       instance > group > project > subject > session
            #           process is a bit messy but gets the job done
            cntr=0
            for (path, __, __) in os.walk('data/'+c_id):
                if cntr==1:
                    inst_path=path
                elif cntr==2:
                    grp_path=path
                elif cntr==3:
                    proj_path=path
                elif cntr==4:
                    subj_path=path
                elif cntr==5:
                    shutil.move(path, 'data/'+c_id) # move session directory up to main subject dir
                cntr=cntr+1
            os.rmdir(subj_path)
            os.rmdir(proj_path)
            os.rmdir(grp_path)
            os.rmdir(inst_path)

            # if downloaded DICOM files, unzip them
            cntr=0
            if 'dicom' in include:
                for (path, __, file_names) in os.walk('data/'+c_id):
                    if cntr>1:
                        thispath=path
                        thispath+='/'
                        thispath+=file_names[0]
                        shutil.unpack_archive(thispath,path)
                        os.remove(thispath)
                    cntr=cntr+1

        else: # download acquisitions in "files"
            
            if not os.path.isdir('data/'+c_id):
                os.makedirs('data/'+c_id+'/'+session)

            for file in files:
                # acq_ptr = fw.lookup(fw_group_label+'/'+fw_proj_label+'/'+c_id+'/'+session+'/'+file)
                acq_label=os.path.splitext(os.path.splitext(file)[0])[0] # parse label from file name (remove '.nii.gz')
                if session_ptr.acquisitions.find_first(f'label={acq_label}'):
                    acq_ptr = session_ptr.acquisitions.find_first(f'label={acq_label}')
                    acq_ptr.download_file(file,'data/'+c_id+'/'+session+'/'+file) # exclude_types=['dicom'] (optional, list)
        print('Done: '+c_id)

    else:
        print('Skipping '+c_id+' - Subject directory already found! To download, delete the directory and try again')
