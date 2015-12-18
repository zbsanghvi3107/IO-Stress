####################################################
#                  Revision: 1.0                   #
#              Updated on: 11/06/2015              #
####################################################

####################################################
#                                                  #
#   This file checks Read & Write errors, extracts #
#   data for F2 & F3 Menu, creates 2 DPSLD files.  #
#   Which are useful to generate report.           #
#                                                  #
#   Author: Zankar Sanghavi                        #
#                                                  #
#   © Dot Hill Systems Corporation                 #
#                                                  #
####################################################

import pandas
import csv
import numpy as np
import log_functions

class Extract_Data:

    def generate_data_tables(csv_file, usr_before
                             , usr_after,fixed_dir):
        #################################################
        #   This step will check Read and Write Errors
        #   in .csv file. It will also raise an error_flag
        #   if it is present.
        #################################################
        lf=log_functions.Log_Functions
        [write_sum, read_sum] = lf.check_errors(csv_file)

        
        ####################################################
        #   This step will check Read and Write Errors
        #   in .csv file. It will also raise an error_flag
        #   if it is present.
        #
        #   User Decision is by default is Yes, it will only 
        #   change if there is an error. 
        ####################################################
        # usr_dec = 'Y' 

        # if error_flag> 0:
            # print('.csv file has errors!')
            # usr_dec = input ('Do you want to continue(Y/N) ? :')
            

        # if error_flag==0:
            # if str(usr_dec)=='Y':
            
        ub = usr_before
        ua = usr_after
        
        # file_name1='temp_ua_file'

        # with open (r''+ str(fixed_dir)+'\\'+file_name1+ '.csv','w') as out_file:
                    
            # out_string= ''
            # #out_string+= heading
            # out_string+= ''
            # #out_string+= header_list_new
            # for i in range(len(ua)):
                # out_string+= '\n'
                # out_string += ua[i]
    
                
            # out_file.write(out_string)
        
        #########################
        #
        # For Hardware Info
        #
        #########################
        hw_info= '        --- Current Hardware Information ---'
        int_info= 'Internal RAIDIO SN'
        
        hw_index = lf.find_index(ua,hw_info) 
        # Finding index where this string
        
        int_index = lf.find_index(ua,int_info)
        
        hw_data_list = ua[hw_index[1]:int_index[1]+1]
        
        
        #########################
        #
        # For Software Info
        #
        #########################
        sw_info='        --- Current Software Configuration ---'
        
        sw_index = lf.find_index(ua,sw_info) 
        # Finding index where this string
            
        search_string_h='HOST'
        ua_host_list = lf.str_lister(search_string_h,sw_index,ua)
        
        search_string_s='SASMap'
        ua_sasmap_list = lf.str_lister(search_string_s
                                        ,sw_index,ua)
        
        
        #########################
        #
        # For DPSLD Info
        #
        #########################
        dpsld_str='DPSLD'
        
        dpsld_index_b= lf.find_index(ub,dpsld_str) #before
        dpsld_list_b=ub[dpsld_index_b[0]+1:dpsld_index_b[1]]
        
        dpsld_list_b=lf.strip_extras(dpsld_list_b)
        dpsld_list_b=lf.eliminate_last_space(dpsld_list_b,-5)
        
        dpsld_index_a= lf.find_index(ua,dpsld_str) #after
        dpsld_list_a=ua[dpsld_index_a[0]+1:dpsld_index_a[1]]
        
        dpsld_list_a=lf.strip_extras(dpsld_list_a)
        dpsld_list_a=lf.eliminate_last_space(dpsld_list_a,-5)
        
        
        header_list='SLOT,PHY,Invalid DWORD Count,'\
                     'Running Disparity Err Count,'\
                     'Loss of DWORD Sync,Phy Reset Problem,'\
                     'DFE Values,SLOT,PHY,Invalid DWORD Count,'\
                     'Running Disparity Err Count,'\
                     'Loss of DWORD Sync,'\
                     'Phy Reset Problem,DFE Values'\
                     
        lf.generate_dpsld(dpsld_list_b,dpsld_list_a,header_list
                            ,fixed_dir)

        
        #########################################
        #
        # Compare: Invalid DWORD count, Running
        # Disparity Err Count, Loss of DWORD Sync,
        # Phy Reset Problem.
        #
        #########################################
        final_compare= lf.compare_columns(fixed_dir) 
        
        final_compare_a=[]
        final_compare_b=[]
        for i in range(len(final_compare)):
            if i%2 ==0:
                final_compare_a.append(final_compare[i])
            else:
                final_compare_b.append(final_compare[i])
             
             
        ##################################
        # Extracting 1st table: PhyStats
        ##################################
        dpsld_1st_str ='Location'
        end_str= '------------------------------------------------------------------------------------\n'
        
        fw_info= lf.extract_fw_info(ua, dpsld_1st_str, end_str)
        #print(len(fw_info))
        
        
        ##############################
        # Extracting 2nd DPSLD table
        #############################       
        dpsld_2nd_str ='Status       Encl Slot Vendor  Model'\
                        '              Serial Number'\
                        '            Size'
        dpsld_2nd_data= lf.extract_2nd_table(ua, dpsld_2nd_str
                                             , end_str)
        #print(len(dpsld_2nd_data))
        
        
        #############################
        # Fixed table Titles.
        #############################
        header_list_new='Status,Encl,Slot,Vendor,Model No.,'\
                        'Serial Number,Capacity,FW Rev.,'\
                        'Inv DW Cnt,Rng Disp. Cnt,Lost DW Sync,'\
                        'Phy Reset,Inv DW Cnt,Rng Disp. Cnt,'\
                        'Lost DW Sync,Phy Reset' 
        
        lf.generate_dpsld_2nd(dpsld_2nd_data, fw_info,
                                final_compare_a, final_compare_b,
                                header_list_new,fixed_dir)
        
        return [write_sum, read_sum, hw_data_list 
                , ua_host_list, ua_sasmap_list]
        
        
#####################################
#              END                  #
#####################################