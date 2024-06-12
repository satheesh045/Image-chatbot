import re
import os
from helpers import *
import pprint as pp
import json 


def split_page(text,min_length=200,include_line_breaks=False):
    paragraphs = re.split("\n\n(?=\u2028|[A-Z-0-9])", text)
    list_par = []
    temp_para = ""  # variable that stores paragraphs with length<min_length
                # (considered as a line)
    for p in paragraphs:
                    if not p.isspace():  # checking if paragraph is not only spaces
                        if include_line_breaks:  # if True, check length of paragraph
                            if len(p) >= min_length:
                                if temp_para:
                                    # if True, append temp_para which holds concatenated
                                    # lines to form a paragraph before current paragraph p
                                    list_par.append(temp_para.strip())
                                    temp_para = (
                                        ""
                                    )  # reset temp_para for new lines to be concatenated
                                    list_par.append(
                                        p.replace("\n", "")
                                    )  # append current paragraph with length>min_length
                                else:
                                    list_par.append(p.replace("\n", ""))
                            else:
                                # paragraph p (line) is concatenated to temp_para
                                line = p.replace("\n", " ").strip()
                                temp_para = temp_para + f" {line}"
                        else:
                            # appending paragraph p as is to list_par
                            list_par.append(p.replace("\n", ""))
                    else:
                        if temp_para:
                            list_par.append(temp_para.strip())
    return list_par


#function to update knowlegde base with text of new uploaded images 
def insert_into_KB(page,filename): #input image text and name 
    paragraphs=[]
    p_threshold=150 #set threshold on paragraph length to 150 chars
    fname = os.path.join(os.getcwd(),"static/KB/output.json")                        
    KB = json.load(open(fname,'r')) # load the current data from knowledge base 
    if (len(page) > p_threshold) :
        #split page text into small paragraphs
        paragraphs= split_page(page)
        for p in paragraphs: 
            if len(p)> p_threshold :
                    #store image name to be retrived to the user in chat 
                    data_dict= {"image":filename ,"body":p}
                    print(data_dict,"\n")
                    KB.append(data_dict) # append the new dictionary to the KB list
    # dump it to KB json file.
    json.dump(KB, open(fname, 'w'))






    

