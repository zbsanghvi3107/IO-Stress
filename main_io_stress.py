####################################################
#                  Revision: 1.0                   #
#              Updated on: 11/06/2015              #
####################################################

####################################################
#                                                  #
#   This file check Read & Write errors, extracts  #
#   data for F2 & F3 Menu, creates 2 DPSLD files.  #
#   Which are useful to generate report.           #
#                                                  #
#   Author: Zankar Sanghavi                        #
#                                                  #
#   © Dot Hill Systems Corporation                 #
#                                                  #
####################################################
import time
start_time = time.time()

import os
import sys


###################################
#  Importing from other Directory
###################################
os.chdir('..')
c_path = os.getcwd()
sys.path.insert(0, r''+str(c_path)+'/Common Scripts')

import report_functions
import extract_lists
import modify_word_docx
import fixed_data_ICS
import user_inputs_ICS

###################################
#  Importing from Current Directory
###################################
sys.path.insert(0, r''+str(c_path)+'/IO Stress')

import pandas
import csv
import numpy as np
import log_functions
import extract_data
import time
import zipfile
import generate_final_word
import pdb

from docx import Document
from docx.shared import Inches
from docx.shared import Pt
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.table import WD_TABLE_DIRECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Cm
import re



###################################
#  To call functions from different
#  files. 
###################################
lf=log_functions.Log_Functions
ed= extract_data.Extract_Data
ui= user_inputs_ICS.User_Inputs
fd= fixed_data_ICS.Fixed_Data
rf= report_functions.Report_Functions
gfw= generate_final_word.Generate_Final_Word 


###################################
#  To store user inputs for number
#  of Files 
###################################
csv_file_list=[]
usr_before_list=[]
usr_after_list=[]
model_no_names=[]
cap_names=[]
fw_no_names=[]
product_fnames=[]
vendor_names=[]
eco_names=[]
chassis_names=[]
cntrllr_names=[]


###################################
#  Strings which will qualify 
#  User Inputs for Log Files. 
###################################
bfr_str= 'logsbefore'
bfr_str1= 'Beforelogs'
bfr_str2= 'BeforeLogs'
bfr_str3= 'beforeLogs'
bfr_str4= 'beforelogs'

aftr_str= 'logsafter'
aftr_str1= 'Afterlogs'
aftr_str2= 'AfterLogs'
aftr_str3= 'afterLogs'
aftr_str4= 'afterlogs'


###################################
#  Questions / User Inputs
###################################
HP_dec = ui.hp_question() # HP drive or BB/SSD?
fw_type = ui.fw_type() #Qualification / Regression?


###################################
#  To make sure, User inputs enters  
#  a numeric character.
###################################
no_of_files='abc' #dummy string
while not no_of_files.isnumeric():
    no_of_files= input('\nPlease enter number of files to'
                        +' concatenate: ')
        
    no_of_files.isnumeric()
no_of_files=int(no_of_files)


######################################
#  This loop will collect all inputs
#  from User, for specified number of 
#  files. And store it in List, which 
#  is used to process later. 
######################################
for nof in range(no_of_files):
    csv_file = input('Enter full file path of .csv file for File'+
                    '# ' +str(nof+1)+ ': ' )
              
    csv_file_list.append(csv_file)
    
    #########################
    # Before .zip file path 
    #########################
    while True:
        usr_before = input('\nPlease enter path of Before zipped'
                            +' file for File # '
                            +str(nof+1)+ ': ' ) 
                            # Before log file
                
        usr_before=str(usr_before).replace('"','') 
        #removing double quotes
        
        if bfr_str in usr_before: 
            break
        elif bfr_str1 in usr_before:
            break
        elif bfr_str2 in usr_before:
            break
        elif bfr_str3 in usr_before:
            break
        elif bfr_str4 in usr_before:
            break    
        else:
            print('\nIt is not a Before file!')
    usr_before_list.append(usr_before)
    
    
    #########################
    # After .zip file path
    #########################
    while True:
        usr_after =input('\nPlease enter path of After zipped'
                        +'file for File # '+str(nof+1)+ ': ' ) 
                        # After log file

 
                                              
        usr_after=str(usr_after).replace('"','') 
        #removing double quotes
        
        if aftr_str in usr_after: 
            break
        elif aftr_str1 in usr_after:
            break
        elif aftr_str2 in usr_after:
            break
        elif aftr_str3 in usr_after:
            break
        elif aftr_str4 in usr_after:
            break
        else:
            print('\nIt is not a After file!')
    usr_after_list.append(usr_after)
    
    
    #########################
    # Ask and check for a 
    # valid Model number.
    # It will also return
    # Model number's Capacity
    # Firmware, Vendor Name, 
    # ECO number, and Product
    # Name. 
    #########################
    [temp_model,
    temp_capacity,
    temp_fw,
    temp_vendor,
    temp_eco,
    temp_product_name] = ui.hdd_model(HP_dec) #model number
    
    model_no_names.append(temp_model) 
    # Appending or Making list to process later
    cap_names.append(temp_capacity)
    fw_no_names.append(temp_fw) 
    product_fnames.append(temp_product_name)
    vendor_names.append(temp_vendor)
    eco_names.append(temp_eco) 

    
    #########################
    # Chassis No. from a 
    # predefined list. 
    #########################
    chassis_no = ui.chassis_in(nof) #chassis number
    chassis_names.append(fd.chassis_list_d[int(chassis_no)])
    
    
    #########################
    # Controller No. from a 
    # predefined list. 
    #########################
    cntrller_no = ui.cntrller_in(nof)
    cntrllr_names.append(fd.cntrllr_list_d[int(cntrller_no)])
    
    
#########################
# Enter Word Template
#########################
word_file = ui.word_in()


#########################################
#  Find list of Model Number and its 
#  Firmware with same Family Name.
#########################################
new_list= lf.find_model_fw(HP_dec, product_fnames)

if fd.fw_type_d[fw_type]=='Qualification':
    temp_fw_type='Initial release of'
else:
    temp_fw_type='Firmware regression for'

    
####################################
# Replace KEYWORDS in Word Template
####################################
fixed_dir=os.path.dirname(r''+str(word_file))
fixed_dir=str(fixed_dir).replace('"','') 
#removing double quotes

file_name=word_file[-(len(word_file)-len(fixed_dir)-1):]
part_no=file_name[:19] # Part no for Footer
rev_no=part_no[-1] # Revision no of the table
print(part_no,rev_no)


###################################
#  Error check to write result
# (PASS/FAIL) in Final Report 
###################################
# error_collection=[]
# for f in range(no_of_files):
            
            # ub_data= lf.unzip_pull_log(usr_before_list[f], 'store') #pull Before .logs file from zip folder
            # ua_data= lf.unzip_pull_log(usr_after_list[f], 'store') #pull After .logs file from zip folder
            
            # ###################################
            # #  Error check to write result
            # # (PASS/FAIL) in Final Report 
            # ###################################
            # [error_flag, hw_list, host_list, sasmap_list]= ed.generate_data_tables(csv_file_list[f], ub_data, ua_data)
            # error_collection.append(error_flag)

# error_qual=''
# for i in range(len(error_collection)):
    # if error_collection[i] != 0:
        # error_qual = int(i)
        # print('File #' +str(i+1)+ ' has errors')
        # break

# if error_qual.isnumeric():
    # pass_fail_dec= 'FAILS'
# else:
    # pass_fail_dec= 'PASSES'

###########################
# FIND TODAY'S DATE 
###########################
date=time.strftime("%m/%d/%Y") 


###########################
# KEYWORDS to be replaced 
# in Word Template.
###########################
replaceText = {"INITIAL": str(temp_fw_type),
                "VENDOR" : str(vendor_names[0]),
                "MDLLIST" : new_list,
                "FWLIST": str(fw_no_names[0]),
                "MODEL" : str(model_no_names[0]),
                "FW": str(fw_no_names[0]),
                "DATE":str(date),
                "ECONUM":str(eco_names[0]),
                "PRODUCT":str(product_fnames[0]),
                "REV":str(rev_no)}
                #"RSLT":str(pass_fail_dec)}

replaceText_f = {"FOOTER":str(part_no)}


###########################
# So that we can change
# name for different tests.
###########################
test_name=' SFT IO Stress Final Report'
if os.path.isfile(r''+str(fixed_dir)+'\\'+str(part_no)
                    +str(test_name)+'.docx'):
                    
    os.remove(r''+str(fixed_dir)+'\\'+str(part_no)
                +str(test_name)+'.docx')

if os.path.isfile(r''+str(fixed_dir)+'\\temp_doc.docx'):
    os.remove(r''+str(fixed_dir)+'\\temp_doc.docx')


mwd= modify_word_docx
#pdb.set_trace()

#Modifying Word Document
mwd.Modify_Word_Docx(word_file,fixed_dir,part_no,replaceText
                    ,replaceText_f,test_name) 
                    

if os.path.isfile(''+str(fixed_dir)+'\\temp_doc.docx'):
    os.remove(r''+str(fixed_dir)+'\\temp_doc.docx')
    
    
#####################################
# To access files generated by 
# "generate_data_tables" function.
#####################################
file_name='\DPSLD'
file_name1='\DPSLD2'    


#####################################
# writing files to report 
#####################################
t_fw_type= fd.fw_type_d[fw_type]

error_collection= gfw.generate_final_report(file_name, file_name1
        , fixed_dir, part_no, test_name, no_of_files
        , csv_file_list, usr_before_list, usr_after_list 
        , fw_no_names, chassis_names, cntrllr_names,t_fw_type )
 
os.remove(r"C:/temp.xml")
os.remove(r"C:/temp1.xml")
os.remove(r''+ str(fixed_dir) +str(file_name) +'.csv')
os.remove(r''+ str(fixed_dir) +str(file_name1) +'.csv')
       
print('\nYour Report is ready!\n')  
 
os.chdir(r''+str(c_path)+'/IO Stress')

elapse_time =round((time.time() - start_time),2) # seconds
if elapse_time < 60 :
    print("Elapsed time: %s seconds" % elapse_time )
else:
    print("Elapsed time: %s minutes" % round(((time.time() - start_time)/60),2))

#%reset -f
sys.modules[__name__].__dict__.clear()
#####################################
#              END                  #
#####################################
