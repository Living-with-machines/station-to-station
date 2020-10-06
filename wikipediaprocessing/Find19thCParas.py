# -*- coding: utf-8 -*-

import json
import spacy
import dateparser
from urllib.parse import quote
from argparse import ArgumentParser

nlp = spacy.load("en_core_web_sm")

matches = ["xix century","xviii century","19th century","18th century","19thc","18thc","19th c","18th c","nineteenth century","eighteenth century", "turn of the century", "fin de siècle"]

def keep_only_19_century(content):
    paras = []
    for para in content:
        if any([True if match in para.lower() else False for match in matches]):
            paras.append(para)
        else:
            doc = nlp(para)
            ents = [e.text for e in doc.ents if e.label_ == "DATE" or e.label == 'TIME']

            years = [dateparser.parse(x).year for x in ents if dateparser.parse(x) != None]
            
            if any([True if 1789 <year and year < 1914 else False for year in years]):
                paras.append(para)
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

    for k,v in sorted_sections.items():
        print (k)
        for line in v["content"]:
            print (line)
        print ()
