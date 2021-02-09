import re
import json
import string
from difflib import SequenceMatcher

# From Quicks intro:
with open('companies.txt') as json_file:
    companies = json.load(json_file)

# From Quicks intro:
stntypes = ["AOT", "CLO", "CO", "CO N", "CO TT", "ND", "NG", "NON-TT", "OP", "P", "REOP", "TT", "HL", "LL", "HB", "HBA", "NG", "TT"]

# Most common last tokens:
keywords = ["PLATFORM", "PLATFORMS", "HALT", "INTERNATIONAL", "JUNCTION", "CAMP", "CENTRAL", 'ROAD', 
            'JUNCTION', 'BRIDGE', 'STREET', 'PARK', 'LANE', 'HILL', 'COLLIERY', 'TOWN', 'GREEN', 
            'CENTRAL', 'CROSSING', 'NORTH', 'LEVEL', 'EAST', 'DOCK', 'WEST', 'GATE', 'CROSS', 'HALT', 
            'SOUTH', 'MILL', 'END', 'SIDING', 'HALL', 'HOUSE']

# Main station XPATHs:
mainstation_xpath = './w:r[not(preceding-sibling::w:r//w:t)][not(w:rPr/w:sz[@w:val=\"16\"])][..//w:b[not(@w:val=\"0\")]]/w:t[1]'
mainstation_xpath2 = './w:r[not(preceding-sibling::w:r//w:t)][not(w:rPr/w:sz[@w:val=\"16\"])][../w:pPr[w:pStyle]/w:rPr/w:b[@w:val=\"0\"]]/w:t[1]'
mainstation_xpath3 = './w:r[not(preceding-sibling::w:r//w:t)][not(w:rPr/w:sz[@w:val=\"16\"])][../w:pPr[w:pStyle[@w:val=\"Heading1\" or @w:val=\"Heading2\" or @w:val=\"Heading3\" or @w:val=\"Heading4\"]]/w:rPr]/w:t[1]'

# The first "w:r" of a paragraph has a child w:text:
first_token_para_xpath = './w:r[//w:t]/w:t[1]'
        

# -----------------------------------------------
def is_mainst(para, mainstation, counter, ns):
    """
    Function that identifies a main station given an xpath.
    
    Arguments:
        para (lxml.etree._Element object): xpath of a paragraph.
        mainstation (str): previous mainstation, empty if first.
        counter (int): mainstation counter, 0 if first.
        ns (dict): namespace for xpath.
        
    Returns:
        mainstation (str): newly identified mainstation, if match
                           is positive, otherwise previous mainstation.
        counter (int): updated counter.
    """
    
    # Set initial letter of main station (to filter out substations 
    # such as Y BOOTHAM JUNCTION referring to a York substation):
    initial_letter = ""
    if mainstation:
        initial_letter = mainstation[0]
                
    paraxp = para.xpath(first_token_para_xpath, namespaces=ns)
    mainxpath = ""
    
    # If the first "w:r" of a paragraph has a child w:text:
    if paraxp:
        
        # If text is capitalized (with exception for stations starting with "Mc"):
        if paraxp[0].text.isupper() or (paraxp[0].text.startswith("Mc") and paraxp[0].text[2:].isupper()):
            
            # See if xpath matches a mainstation xpath:
            mainxpath = para.xpath(mainstation_xpath, namespaces=ns)
            if not mainxpath:
                mainxpath = para.xpath(mainstation_xpath2, namespaces=ns)
            if not mainxpath:
                mainxpath = para.xpath(mainstation_xpath3, namespaces=ns)
                
            # Filter out:
            #   * station names of length 1,
            #   * station names that start with initial of previous main station (e.g. "Y BOOTHAM JUNCTION"),
            #   * station names that start with an open square bracket or parenthesis:
            # If mainstation is not found, return previous mainstation with previous counter.
            if mainxpath and len(mainxpath[0].text.strip()) > 1 and not mainxpath[0].text.startswith(initial_letter + " ") and not mainxpath[0].text.startswith("[") and not mainxpath[0].text.startswith("("):
                counter += 1
                mainstation = mainxpath[0].text
                return mainstation, counter
            
            else:
                return mainstation, counter
        else:
            return mainstation, counter
    else:
        return mainstation, counter
    

# -----------------------------------------------
def process_decription(mainst, description, substationId):
    """
    Function that finds all substations for a given main station.
    
    Arguments:
        mainst (str): main station name.
        description (list): list of strings with the description of a station.
        substationId (int): substation index of previous substation.
        
    Returns:
        dSubstations (dict): dictionary where key is a tuple (substationId,
        substation name) and value is a string with the description of the
        station.
    """
    
    # Remove original source formatting error such as "DYKEBAR [", "Cal]"
    if mainst.endswith("["):
        mainst = mainst[:-1]
        description[0] = "[" + description[0]
    
    dSubstations = dict()
    
    rsubst = r"[A-Z ?\-?\&? ?]+ "
    rsubstInitial = r"^(" + mainst[0] + "[ |\-]([A-Z ?\-?\&? ?]+)+) "
    
    substname = ""
    for line in description:
        match1 = re.match(rsubst, line)
        match2 = re.match(rsubstInitial, line)
        # Find strings that match a substation that is abbreviated
        # by its mainstation initial (e.g. "A TOWN" for "ABBEY TOWN"):
        if match2:
            if not match2.group(0).strip() in companies:
                substname = match2.group(0).strip()
                substationId += 1
        # Find any other substation (e.g. "BARGOED & ABERBARGOED"):
        elif match1:
            if len(match1.group(0).strip()) > 1 and not match1.group(0).strip() in companies:
                substname = match1.group(0).strip()
                substationId += 1
        
        # Case for which a description line corresponds to the main station:
        if substname == "":
            substname = mainst
            substationId += 1
            
        # Create substations dictionary:
        stup = (substationId, substname)
        if not stup in dSubstations:
            line = re.sub(r"^" + substname, "", line)
            dSubstations[stup] = line.strip()
        else:
            dSubstations[stup] += " " + line.strip()
                
    return dSubstations, substationId


# -----------------------------------------------
def subst_rename(main, sub):
    """
    Function that renames substation to its full name according
    to its main station name (e.g. "COMMONHEAD A NORTH" is "COMMONHEAD
    AIRDRIE NORTH", because it's a substation of "AIRDRIE").
    
    Arguments:
        main (str): main station.
        sub (str): substation as appears in Quicks.
        
    Returns:
        A string with the full substation name.
    """
    
    sub = sub.replace("&", " AND ")
    sub = re.sub(' +', ' ', sub)
    rsub = []
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation)) #map punctuation to space
    main = main.translate(translator).split()
    sub = sub.translate(translator).split()
    if sub != main:
        
        # Sometimes, first token is split by whitespace. Join split tokens:
        # e.g. ['F', 'ISHPONDS']
        if len(sub) == 2:
            if sub[0] + sub[1] == main[0]:
                sub = [sub[0] + sub[1]]
        # e.g. ['L', 'ITTLE', 'ORMESBY']
        if len(sub) > 2:
            if sub[0] + sub[1] == main[0]:
                sub = [sub[0] + sub[1]] + sub[2:]
        
        # Sometimes, first token is split by whitespace. Join split tokens:
        # e.g. 'CROSS KEYS' and 'CROSSKEYS'
        if len(main) == 2:
            if main[0] + main[1] == sub[0]:
                main = [main[0] + main[1]]
        # e.g. 
        if len(main) > 2:
            if main[0] + main[1] == sub[0]:
                main = [main[0] + main[1]] + main[2:]
                
        # CASE 1: Main station is just one token, substation is more than one token:
        if len(main) == 1 and len(sub) > 1:
            
            # e.g. 'ALTON' and 'ALTON PARK'
            if main[0] == sub[0]:
                rsub += sub
            
            # e.g. 'BONNYRIGG' and 'BONNYRIGGE DEPOT'
            elif sub[0].startswith(main[0]):
                rsub += sub
            
            # e.g. 'BIRMINGHAM' and 'B NEW STREET'
            elif main[0][0] == sub[0][0] and len(sub[0]) == 1:
                rsub.append(main[0])
                rsub += sub[1:]
            
            # e.g. 'BARGEDDIE' and 'BARGE DDI E'
            elif "".join(sub) == main[0]:
                rsub += main
                
            # e.g. 'ALLOA' and 'SOUTH ALLOA'
            elif any(x == main[0] for x in sub):
                rsub += sub
            
            # e.g. 'AIRDRIE' and 'COMMONHEAD A NORTH'
            elif any(len(x) == 1 and x[0] == main[0][0] for x in sub):
                for x in sub:
                    if len(x) == 1 and x[0] == main[0][0]:
                        rsub.append(main[0])
                    else:
                        rsub.append(x)
                        
            # e.g. 'CAERNARVON' and 'CARNARVON CASTLE'
            elif any(SequenceMatcher(None, x, main[0]).ratio() >= 0.8 for x in sub):
                rsub = sub
                
            # e.g. 'SOUTHPORT' and 'STEAMPORT MUSEUM'
            else:
                rsub.append(main[0])
                rsub += sub
                
        # CASE 2: Substation has length 1, mainstation length > 1
        elif len(sub) == 1 and len(main) > 1:
            
            # e.g. 'CLYDACH ON TAWE' and 'CLYDACH'
            if any(SequenceMatcher(None, x, sub[0]).ratio() >= 0.8 for x in main):
                rsub = sub
                
            # e.g. 'HIGHGATE ROAD' and 'HL'
            elif sub[0] in keywords or sub[0] in stntypes:
                rsub += main
                rsub += sub
                
            # e.g. 'BLAENAU FFESTINIOG' and 'DINAS'
            else:
                rsub = sub
                
        # CASE 3: Substation has length 1, mainstation length 1
        elif len(sub) == 1 and len(main) == 1:
            
            # e.g. 'BELMONT' and 'JUNCTION'
            if sub[0] in keywords or sub[0] in stntypes:
                rsub += main
                rsub += sub
            
            # e.g. 'SELHURST' and 'SELHUST'
            elif SequenceMatcher(None, sub[0], main[0]).ratio() >= 0.8:
                rsub += main
            
            # e.g. 'WALKER' and 'WALKERGATE'
            elif sub[0].startswith(main[0]):
                rsub += sub
                
            # e.g. 'TILBURY' and 'BERTHS'
            else:
                rsub += main
                rsub += sub
        
        # CASE 4: otherwise
        # e.g. 'FINCHLEY ROAD' and 'F R AND FROGNAL'
        # e.g. 'B ON S AND QUORN' and 'BARROW ON SOAR AND QUORN'
        else:
            tsub = []
            for x in sub:
                if len(x) == 1:
                    for m in main:
                        if m.startswith(x) and not m in tsub:
                            tsub.append(m)
                            break
                    if not any(m.startswith(x) for m in main):
                        tsub.append(x)
                else:
                    tsub.append(x)
                    
            rsub = [x for x in tsub]
            
            # e.g. "ST A" or "S C" as substation names:
            if len(max(rsub, key=len)) <= 2:
                rsub = main
                
        rsub = " ".join(rsub)
        if re.search(r"\bLL\b", rsub):
            rsub = re.sub(r"\bLL\b", "LOW LEVEL", rsub)
        if re.search(r"\bHL\b", rsub):
            rsub = re.sub(r"\bHL\b", "HIGH LEVEL", rsub)
            
        return rsub
    else:
        return " ".join(sub)
    
    
# -----------------------------------------------
def format_for_candranker(gazname, unique_placenames_array):
    """
    This function returns the unique alternate names in a given gazetteer
    in the format required by DeezyMatch candidate ranker.
    
    Arguments:
        gazname (str): output name of the DeezyMatch query file.
        unique_placenames_array (list): unique names that will be Deezy
                                        Match queries.
    """
    with open(gazname + ".txt", "w") as fw:
        for pl in unique_placenames_array:
            pl = pl.strip()
            if pl:
                pl = pl.replace('"', "")
                fw.write(pl.strip() + "\t0\tfalse\n")