# -*- coding: utf-8 -*-

import json
import os
import re
import spacy
import dateparser
from urllib.parse import quote
from argparse import ArgumentParser

nlp = spacy.load("en_core_web_sm")

matches = ["xix century","xviii century","19th century","18th century","19thc","18thc","19th c","18th c","nineteenth century","eighteenth century","nineteenth-century","eighteenth-century","19th-century","18th-century","early 20th c","early twentieth c"]

match_decades = r'.*\b(1[789][0-9]0)s\b.*'
match_between = r'.*between (1[789][0-9][0-9]) and (1[789][0-9][0-9]).*'
match_fromto = r'.*from (1[789][0-9][0-9]) to (1[789][0-9][0-9]).*'
match_around = r'.*around (1[789][0-9][0-9])\b.*'

def keep_only_19_century(content):
    paras = []
    for para in content:
        
        if any([True if match in para.lower() else False for match in matches]):
            paras.append(para)
            ### --------------------------------
            ### Uncomment to check which century-strings is matched in the paragraph:
            # print(matches)
            # print([match if match in para.lower() else False for match in matches])
            # print(para)
            # print()
            ### --------------------------------
        else:
            doc = nlp(para)
            ents = [e.text for e in doc.ents if e.label_ == "DATE"]
            
            years = []
            for x in ents:
                # This regex captures decades in strings (e.g. "1860s"), strips the "s" and keeps the year.
                if re.match(match_decades, x):
                    years.append(re.match(match_decades, x).group(1))
                # This regex captures between-years expressions in strings (e.g. "between 1841 and 1843"), keeps the years.
                elif re.match(match_between, x):
                    years += re.match(match_between, x).groups()
                # This regex captures from-to expressions in strings (e.g. "from 1841 to 1843"), keeps the years.
                elif re.match(match_fromto, x):
                    years += re.match(match_fromto, x).groups()
                # This regex captures around-years expressions in strings (e.g. "around 1841"), keeps the year.
                elif re.match(match_around, x):
                    years.append(re.match(match_around, x).group(1))
                # This turns the time expression into datetime, we keep the year.
                else:
                    dtime = dateparser.parse(x)
                    if dtime != None:
                        # The following line is to avoid a preference of dateparser of turning all-numerical strings
                        # with a lenght different from four digits into hours, minutes, and seconds, while defaulting
                        # the year to 1900. E.g. "A666" to "1900-01-01 06:06:06", or
                        # "886" to "1900-01-01 08:08:06", or "200000" to "1900-01-01 20:00:00".
                        if not (x.isnumeric() and len(x) != 4 and dtime.year == 1900 and dtime.month == 1 and dtime.day == 1):
                            years.append(dtime.year)
                    
                    ### --------------------------------
                    ### Uncomment to check which DATE-strings did not return a match:
                    #     else:
                    #         print("==>", x) 
                    # else:
                    #     print("==>", x)
                    ### --------------------------------
                    
            # Make sure all years are integers:
            years = [int(year) for year in years]
            
            if any([True if 1789 <year and year < 1914 else False for year in years]):
                paras.append(para)
                
                ### --------------------------------
                ### Uncomment to check which years are matched in the paragraphs:
                # print(years)
                # print([year if 1789 <year and year < 1914 else False for year in years])
                # print(para)
                # print()
                ### --------------------------------
                
    if len(paras)>0:
        return paras

def parse_input_commands():
    """
    read inputs from the command line
    return the entity to be searched
    """    

    parser = ArgumentParser()
    parser.add_argument("-e", "--entity", help="The entity to be searched and processed",)
    args = parser.parse_args()
    entity = args.entity
    if entity:
        return entity
    else:
        parser.exit("ERROR: The entity is missing, you should query it for instance using -e Barack%20Obama")

def get_XIX_sections (aspects):

    XIX_sections = {}

    for section,structure in aspects.items():
            content = structure["content"]
            order = structure["order"]
            processed_content = keep_only_19_century(content)
            if processed_content:
                XIX_sections[section] = {"content":processed_content,"order":order}
    return XIX_sections
            
if __name__ == "__main__":

    entity = parse_input_commands()
    entity = quote(entity)
    with open("/resources/wikipedia/extractedResources/Aspects/"+entity+".json") as json_file:   
        aspects = json.load(json_file)
    XIX_sections = get_XIX_sections (aspects)

    sorted_sections = {k: v for k, v in sorted(XIX_sections.items(), key=lambda item: item[1]["order"])}

    if os.path.isdir("outputs") == False:
        os.mkdir("outputs")

    if os.path.exists("outputs/"+entity+".txt"):
        os.remove("outputs/"+entity+".txt")

    for k,v in sorted_sections.items():
        print (k)
        f = open("outputs/"+entity+".txt", "a+")
        f.write(k+"\n")
    
        for line in v["content"]:
            print (line)
            f = open("outputs/"+entity+".txt", "a+")
            f.write("-"+line+"\n")
        print ()
        f = open("outputs/"+entity+".txt", "a+")
        f.write("\n")
        f.close()
        
