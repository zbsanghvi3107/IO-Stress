####################################################
#                  Revision: 1.0                   #
#              Updated on: 11/06/2015              #
####################################################

####################################################
#                                                  #
#   This File contains all the Functions           #
#   used to generate IO Stress Report.             #
#                                                  #
#   Author: Zankar Sanghavi                        #
#                                                  #
#   © Dot Hill Systems Corporation                 #
#                                                  #
####################################################
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


###################################
#  Importing from Current Directory
###################################
sys.path.insert(0, r''+str(c_path)+'/IO Stress')

import pandas
import csv
import numpy as np
import zipfile
import codecs

class Log_Functions:

    #########################
    #
    #   For Software Info
    #
    #   To find a string in 
    #   .log or .txt file
    #########################
    def find_index(file,string):
        sw_index=[]
        for j in range(len(file)):
            if string in file[j]:
                #print(f[j])
                #break
                sw_index.append(j)
        return sw_index

        
    ###############################
    #
    #   This function will extract
    #   a list which will have all
    #   lines starting with a 
    #   "search_string"
    ###############################
    def str_lister(search_string, sw_index, file):
        
        f = file
        sw_host_index=[]
        
        for k in range(sw_index[0],len(f)):
            if search_string in f[k]:
                sw_host_index.append(k)

        host_lines=sw_host_index[1]-sw_host_index[0]

        for l in range(len(sw_host_index)-1):
            if sw_host_index[l]-sw_host_index[l-1]>host_lines:
                not_host_lines=l
                break
        exracted_list= f[sw_host_index[0]: sw_host_index[0]
                        +(host_lines*not_host_lines)]
        return exracted_list
       
       
    ##################################
    #  This Function will check for 
    #  Read and Write Errors and raise 
    #  an "error_flag" (i.e. it will be 
    #  1) if Error is present. 
    ##################################
    def check_errors(csv_file):
     
        csv_file=str(csv_file).replace('"','')
        csv_data = pandas.read_csv(r''+str(csv_file),skiprows=13
                                    ,header=None)
        
        rf= report_functions.Report_Functions
        
        
        ##################################
        #  Finding column Indices of Read 
        #  Errors & Write Errors.
        ##################################
        required_column= ['Read Errors','Write Errors']
        req_col=[]

        for i in range (len(required_column)):
            [count,index]=rf.find_string(csv_data,0,1
                                        ,required_column[i])
            req_col +=index
            
            
        ##################################
        #  Finding row Indices of DISKs.
        ##################################
        required_rows= ['DISK']
        req_rows=[]

        for i in range (len(required_rows)):
            [count,index]=rf.find_string(csv_data,0,0,
                                         required_rows[i])
            #req_col.append(index)
            req_rows +=index
            
        ##################################
        #  To check Read Errors 
        ##################################
        mod_data= csv_data[:][req_col[0]] #read errors
        mod_data=mod_data[req_rows]
        mod_data= np.array(mod_data)
        mod_data= mod_data.tolist()
        
        read_sum= 0
        
        for i in range(len(mod_data)):
            read_sum += int(mod_data[i])

        
        ##################################
        #  To check Write Errors 
        ##################################
        
        mod_data= csv_data[:][req_col[1]] #read errors
        mod_data=mod_data[req_rows]
        mod_data= np.array(mod_data)
        mod_data= mod_data.tolist()
        
        write_sum= 0
        
        for i in range(len(mod_data)):
            write_sum += int(mod_data[i])
        
        error_flag=0
        
        
        ########################################
        #  This will check errors in the .csv
        #  file and pass flag which help to 
        #  decide Report Generation.
        #
        #  If Error_flag =1; don't generate 
        #  report. Else generate a Report.
        #   
        ########################################
        if write_sum== 0 & read_sum == 0 :
            print('\nCSV File is error free ')
            
        if write_sum > 0 & read_sum== 0 :
            print('\nCSV File has total ' +str(write_sum)
                  + ' Write Errors ')
                  
            error_flag=1
            
        elif write_sum == 0 & read_sum > 0 :
            print('\nCSV File has total ' +str(read_sum)
                    + ' Read Errors ')
                    
            error_flag=1
            
        elif write_sum> 0 & read_sum> 0 :
            print('\nCSV File has total ' +str(read_sum)
                  + ' Read Errors ')
                  
            print('\nCSV File has total ' +str(write_sum)
                   + ' Write Errors ')
                   
            error_flag=1
            
        return [write_sum, read_sum]
        
        
    ########################################
    #  This will strip all new lines from 
    #  the list 
    ########################################
    def strip_new_lines(slist):
        for i in range(len(slist)):
            slist[i]=slist[i].strip('\n')
        return slist   

        
    ##########################################
    # This function will strip extra spaces,
    # tabs and replace will comma
    ##########################################    
    def strip_extras(slist):
        import re
        for i in range(len(slist)):
            slist[i]=slist[i].strip('\n')
            slist[i]=re.sub( '\s+', ' ', slist[i] ).strip()
            slist[i]=slist[i].replace(" ",',')
            slist[i]=slist[i].replace("-X",',')
        return slist
        
        
    ##########################################
    # Last column of DPSLD data has data 
    # discrepancies. That there is space
    # between data.
    # Example : 
    # 
    # Last column some values are 00000000,
    # while some are 0000 0000. 
    #
    # This makes us to read or write the data.
    # So to eliminate this. This Function is 
    # used.
    ##########################################
    def eliminate_last_space(elist,number):
        elist = np.array(elist)
        for i in range(len(elist)):
            
                temp_list = list(elist[i])
                if temp_list[number] == ',':
                    
                    del temp_list[number]
                    elist[i]="".join(temp_list)
                
        return elist
        
        
    ##########################################
    # This function combine DSPLD data from 
    # Before and After log files. And create
    # a .csv file
    ##########################################
    def generate_dpsld(dpsld_list_b,dpsld_list_a,header_list
                        ,fixed_dir):
                        
        #path=os.getcwd()
        file_name='\DPSLD'

        with open (r''+ str(fixed_dir) +str(file_name) 
                    +'.csv','w') as out_file:
                    
            out_string= ''
            #out_string+= header_bfr_aftr+ '\n'
            out_string+= header_list
            for i in range(len(dpsld_list_b)):
                out_string+= '\n'
                out_string += dpsld_list_b[i] + ','+dpsld_list_a[i]
                                
                             
            out_file.write(out_string)
            
            
    ##########################################
    # This function compares two columns. That
    # is subtracts after column with before 
    # column and returns the difference.
    ##########################################
    def one_diff(da,db):
        compare_results_invalid = []
        for i in range(1,len(da)):
            compare_results_invalid.append(int(da[i]) - int(db[i]))
        return compare_results_invalid
        
        
    ##########################################
    # This function compares all columns and 
    # returns comparison list.
    ##########################################    
    def compare_columns(fixed_dir):
        #path=os.getcwd()
        file_name='\DPSLD'
        dpsld_data = pandas.read_csv(open(r''+ str(fixed_dir) 
                        +str(file_name) +'.csv'),header=None)
        compare=[]
        for i in range(2,6):
            da= dpsld_data[:][i+7]
            db= dpsld_data[:][i]
            temp_list= Log_Functions.one_diff(da,db)
            compare+= temp_list
            
        final_compare=[]
        temp= int(len(compare)/4)
        for i in range(temp):
            final_compare.append([compare[i],compare[i+temp]
                         , compare[i+(2*temp)],compare[i+(3*temp)]])
            temp_final = str(final_compare[i])
            temp_final = temp_final.replace('[',',')
            temp_final = temp_final.replace(']','')
            final_compare[i] = temp_final
        return final_compare    
        
        
    ##########################################
    # This function extracts Firmware 
    # Information from 1st DSPLD Table.
    ##########################################
    # def extract_fw_info(ua, dpsld_1st_str, end_str):
        # dpsld_1st_index= Log_Functions.find_index(ua,dpsld_1st_str)
        # new_dpsld_1st= ua[dpsld_1st_index[0]:]

        # end_str_index_1st= Log_Functions.find_index(new_dpsld_1st,end_str)
        # dpsld_1st_data= new_dpsld_1st[end_str_index_1st[0]-1:end_str_index_1st[1]]
        # dpsld_1st_data= Log_Functions.strip_extras(dpsld_1st_data)
        
        # ####################################
        # # For FW number from table. 1
        # ####################################
        
        # fw_rev_index= new_dpsld_1st[0].find('Rev')
        # fw_info=[]
        # for i in range(len(dpsld_1st_data)):
            # temp= new_dpsld_1st[i]
            # fw_info.append(temp[fw_rev_index:fw_rev_index+4])

        # fw_info[0:2]=[]
        # #print(len(fw_info))
        # return fw_info
        
        
    ################### New ##################
    # This function extracts Firmware 
    # Information from 1st DSPLD Table.
    ##########################################   
    def extract_fw_info(ua, dpsld_1st_str, end_str):
        sw_index=[]
        #print(len(ua))
        
        for j in range(1,len(ua)):
            if dpsld_1st_str in str(ua[j]) :
                sw_index.append(j)
                #print(ua[j])
                
        #print(len(sw_index))
        serial_str='Serial Number'
        v_str='Vendor'
        rev_str='Rev'
         
        #print(sw_index)
        sw_index1=[]
        for i in range(len(sw_index)):
            temp_data = ua[sw_index[i]]
            if serial_str in temp_data: 
                if v_str in temp_data: 
                    if rev_str in temp_data:
                        sw_index1.append(i)
        #print(sw_index1)                    
        new_dpsld_1st =ua[sw_index[sw_index1[-1]]:]
        
        
        
        end_str_index_1st= Log_Functions.find_index(new_dpsld_1st
                                                    ,end_str)
                                                    
        dpsld_1st_data= new_dpsld_1st[end_str_index_1st[0]-1:
                                        end_str_index_1st[1]]
                                        
        dpsld_1st_data= Log_Functions.strip_extras(dpsld_1st_data)

        ####################################
        # For FW number from table. 1
        ####################################

        fw_rev_index= new_dpsld_1st[0].find(rev_str)
        fw_info=[]
        for i in range(len(dpsld_1st_data)):
            temp= new_dpsld_1st[i]
            fw_info.append(temp[fw_rev_index:fw_rev_index+4])

        fw_info[0:2]=[]
        return fw_info

    
    ##########################################
    # This function extracts 2nd DSPLD Table.
    ##########################################  
    # def extract_2nd_table(ua, dpsld_2nd_str, end_str):
        # dpsld_2nd_index= Log_Functions.find_index(ua,dpsld_2nd_str)
        # new_dpsld_2nd= ua[dpsld_2nd_index[0]:]

        # end_str_index_2nd= Log_Functions.find_index(new_dpsld_2nd,end_str)
        # dpsld_2nd_data= new_dpsld_2nd[:end_str_index_2nd[0]+1=]
        # #dpsld_2nd_data
        # for i in range(len(dpsld_2nd_data)):
            # if 'Not Present' in dpsld_2nd_data[i]:
                # del dpsld_2nd_data[i]
                
        # print(dpsld_2nd_data)        
        # dpsld_2nd_data= Log_Functions.strip_extras(dpsld_2nd_data)
        # #len(dpsld_2nd_data)
        # return dpsld_2nd_data
    def extract_2nd_table(ua, dpsld_2nd_str, end_str):
        dpsld_2nd_index= Log_Functions.find_index(ua
                                        ,dpsld_2nd_str)
                                        
        new_dpsld_2nd= ua[dpsld_2nd_index[0]:]

        end_str_index_2nd= Log_Functions.find_index(new_dpsld_2nd
                                                    ,end_str)
        dpsld_2nd_data= new_dpsld_2nd[end_str_index_2nd[0]+1
                                      :end_str_index_2nd[1]]

        
        ################################
        # To save row index which has 
        # Data present (i.e Eliminating 
        # Not present/available data)
        ################################
        req_row_index=[] 
        for i in range(len(dpsld_2nd_data)):
            if 'Not Present' not in dpsld_2nd_data[i]:
                    req_row_index.append(i)

        new_dpsld_data=[]
        for j in range(len(req_row_index)):
            new_dpsld_data.append(dpsld_2nd_data[req_row_index[j]])
        return Log_Functions.strip_extras(new_dpsld_data) 
            
            
    ##########################################
    # This writes a .csv file of 2nd table.
    ##########################################      
    def generate_dpsld_2nd(dpsld_2nd_data, fw_info, 
                            final_compare_a, final_compare_b
                            , header_list_new,fixed_dir):
        #path=os.getcwd()
        #path='C:\Test Files\IO Stress\Data Files'
        file_name='\DPSLD2'

        with open (r''+ str(fixed_dir) +str(file_name) 
                    +'.csv','w') as out_file:
                    
            out_string= ''
            #out_string+= heading
            #out_string+= '\n'
            out_string+= header_list_new
            for i in range(len(dpsld_2nd_data)):
                out_string+= '\n'
                out_string += dpsld_2nd_data[i] + ',' +fw_info[i] +final_compare_a[i] +final_compare_b[i] 
                             
                            
                    
                
                
            out_file.write(out_string)
    
    ##########################################
    # This function makes a list of Model No.
    # and FW to embedd in the Final Report.
    ##########################################  
    def find_model_fw(HP_dec, product_fnames):
        el= extract_lists.Extract_Lists
        
        [model_list, capacity_list, vendor_list, fw_list,
        eco_list, product_fname_list,model_list_HP, 
        capacity_list_HP, vendor_list_HP, fw_list_HP, 
        eco_list_HP, product_fname_list_HP]= el.get_data()
        
        
        ind_same_fname=[]

        if HP_dec=='N': #For BB/SSD drives
            for i in range(len(product_fname_list)):     
            # For find index of same Vendor Family name
            
                if product_fname_list[i]== (product_fnames[0]):
                    temp=i
                    ind_same_fname.append(temp)
            #print(model_list[ind_same_fname[0]], 
                    #fw_list[ind_same_fname[0]])
            
            model_alist=np.array(model_list)
            model_alist=model_alist[ind_same_fname]
            model_alist.tolist()
            
            fw_alist=np.array( fw_list)
            fw_alist=fw_alist[ind_same_fname]
            fw_alist.tolist()
            
            new_list=''
            for i in range(len(model_alist)):
                new_list += model_alist[i] 
                new_list += '-'
                new_list += fw_alist[i]
                new_list += ' '
            #print(new_list)

        elif HP_dec=='Y': # For HP drives
            for i in range(len( product_fname_list_HP)):     
            # For find index of same Vendor Family name
            
                if  product_fname_list_HP[i]==str(product_fnames[0]):
                    temp=i
                    ind_same_fname.append(temp)
            #print(model_list_HP[ind_same_fname[0]], fw_list_HP[ind_same_fname[0]])

            model_alist=np.array( model_list_HP)
            model_alist=model_alist[ind_same_fname]
            model_alist.tolist()
            
            fw_alist=np.array( fw_list_HP)
            fw_alist=fw_alist[ind_same_fname]
            fw_alist.tolist()
            
            new_list=''
            for i in range(len(model_alist)):
                new_list += model_alist[i] 
                new_list += '-'
                new_list += fw_alist[i]
                new_list += ' '
            #print(new_list)

        return new_list 
        
    ##########################################
    # This function unzips and pulls files
    # containing our required string.
    ########################################## 
    # def unzip_pull_log(ub_path, search_string):   
        # ub_temp= open(r''+str(ub_path),'rb')
        # ub_unzip= zipfile.ZipFile(ub_temp)
        # ub_zip_list = ub_unzip.namelist()
        # #print(zip_list)

        # for i in range(len(ub_zip_list)):
            # if search_string in ub_zip_list[i]:
                # string_index =i
                # break
                # #print(string_index)

        # with open(ub_unzip.extract(""+str(ub_zip_list[string_index]), "C:/"),encoding="utf8") as ub_data:
            # ub_data = ub_data.readlines()
        # return ub_data
    def unzip_pull_log(ub_path, search_string, file_type): 
        ub_temp= open(r''+str(ub_path),'rb')
        ub_unzip= zipfile.ZipFile(ub_temp)
        ub_zip_list = ub_unzip.namelist()
        #print(zip_list)

        for i in range(len(ub_zip_list)):
            if search_string in ub_zip_list[i]:
                string_index =i
                break
                #print(string_index)
        try:
            with open(ub_unzip.extract(r""
                +str(ub_zip_list[string_index]), "C:/")
                ,encoding="utf8") as ub_data:
                
                ub_data = ub_data.readlines()
            os.remove("C:/"+str(ub_zip_list[string_index]))
            
        except UnicodeDecodeError:
        
            print('Unicode Decode Error occured in: '+str(file_type)+'\nPlease except some delay in Report Generation!\n')
            targetFilePath = os.getcwd() 
            # get current current directory path
            
            import shutil  
            import io
            infile = "C:/"+str(ub_zip_list[string_index])
            with io.open(infile, errors='ignore') as source:
                with io.open(r'C:\log_temp.log', mode='w', encoding='cp1252') as target:
                    shutil.copyfileobj(source, target)
            # ub_final= ub_unzip.extract(r""
                # +str(ub_zip_list[string_index]))     
                    
            # BLOCKSIZE = 1048576 
            # # or some other, desired size in bytes
            
            # with codecs.open(ub_final, "r", "utf8") as sourceFile:
            
                # with codecs.open(r''+str(targetFilePath)
                    # +'\log_temp.log', "w", "utf8") as targetFile:
                    
                    # while True:
                        # try:
                            # contents = sourceFile.read(BLOCKSIZE)
                            # if not contents:
                                # break
                            # targetFile.write(contents)
                        # except UnicodeDecodeError:
                            # pass
                            
            with open(r'C:\log_temp.log') as ub_data:
                        
                ub_data = ub_data.readlines()
                
            os.remove("C:/"+str(ub_zip_list[string_index]))
            os.remove(r'C:\log_temp.log')
        return ub_data    
        
    ##########################################
    # This function finds Iterations from given 
    # unzipped log file. 
    ########################################## 
    def find_iterations(log_data):
        iter_info='AUTO TEST: Step 6: Backend cable pull'
        
        iter_index = Log_Functions.find_index(log_data,iter_info)
        req_str= log_data[iter_index[-1]]
        
        qual_str='#'
        
        req_index=(req_str).find(qual_str, 0, len(req_str))
        
        max_iter=(req_str[req_index+1:]).strip('\n')
        max_iter = int(max_iter) 
        return max_iter  


    ##########################################
    # This function finds Iterations from given 
    # unzipped log file for SDR files. 
    ########################################## 
    def find_iterations_SDR(log_data):
        iter_info='AUTO TEST: Step 14:'
        
        iter_index = Log_Functions.find_index(log_data,iter_info)
        req_str= log_data[iter_index[-1]]
        
        qual_str='#'
        
        req_index=(req_str).find(qual_str, 0, len(req_str))
        
        max_iter=(req_str[req_index+1:]).strip('\n')
        max_iter = int(max_iter) 
        return max_iter 
        
        
        
#####################################
#              END                  #
#####################################
