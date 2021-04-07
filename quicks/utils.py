import re
import json
import string
import pandas as pd
import numpy as np
import dateparser
from pathlib import Path
from difflib import SequenceMatcher

# Load dictionary of companies from Quicks intro:
cmpdf = pd.read_csv("../resources/quicks/companies.tsv", sep="\t")
dCompanies = pd.Series(cmpdf["Wikidata ID"].values,index=cmpdf["Company"]).to_dict()

# Load index2map dictionary from Quicks appendix:
i2mdf = pd.read_csv("../resources/quicks/index2map.tsv", sep="\t")
dIndex2map = dict()
for i, row in i2mdf.iterrows():
    place = row["Place"]
    place = place.replace("S t", "St")
    place = " ".join([x for x in place.split() if x[0].isalpha() and x.split("-")[0].istitle()])
    if row["number"] in dIndex2map:
        if not place in dIndex2map[row["number"]]:
            dIndex2map[row["number"]].append(place)
    else:
        dIndex2map[row["number"]] = [place]

# Station types from Quicks intro:
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
            if not match2.group(0).strip() in dCompanies:
                substname = match2.group(0).strip()
                substationId += 1
        # Find any other substation (e.g. "BARGOED & ABERBARGOED"):
        elif match1:
            if len(match1.group(0).strip()) > 1 and not match1.group(0).strip() in dCompanies:
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
def detect_companies(description):
    
    # -----------------------------------
    # Remove non-printable characters:
    description = ''.join([x if x in string.printable else ' ' for x in description])
    
    # -----------------------------------
    # Remove extra white spaces:
    description = re.sub(' +', ' ', description)
    
    # Remove square and curly brackets (i.e. info on maps and additional notes):
    description = re.sub(r'\{[^}]*?\}', '', description)
    description = re.sub(r'\([^)]*?\)', '', description)
    
    detected_companies = []
    locinfo = ""
    rcmp = r"^(.{,30}?)\[(.*?)\]"
    if re.match(rcmp, description):
        locinfo, company = re.match(rcmp, description).groups()
        locinfo = locinfo.strip()
        if locinfo:
            # Keep locinfo only if it starts with "near", it's longer than 2 char
            # and first char of first token is a normally uppercased proper noun:
            locinfo = locinfo if locinfo.startswith("near ") or (locinfo.split()[0].istitle() and len(locinfo.split()[0]) > 1 and not locinfo.split()[0] in ["For", "From", "All", "Temp", "Both"]) else ""
        detected_companies = re.split(';|/', company)
        detected_companies = [c.strip() for c in detected_companies]
    
    # Companies in Quicks, linked to Wikidata (previously linked, manually):
    companiesWkdtMain = ""
    companiesWkdtAlt = []
    for c in detected_companies:
        if not companiesWkdtMain:
            companiesWkdtMain = dCompanies[c] if c in dCompanies else "-"
        else:
            companiesWkdtAlt.append(dCompanies[c])
            
    locinfo = [re.sub(r"^near ", "", locinfo)]
            
    return locinfo, detected_companies, companiesWkdtMain, companiesWkdtAlt


# -----------------------------------------------
# Process alternate names (from abbreviated name to full name)
def process_altnames(altnames, mainst, subst):
    repl = altnames[0]
    prev = altnames[1]
    altrn = altnames[2]
    added = altnames[3]
    dropped = altnames[4]

    # Add or drop tokens from main or sub station:
    # Often the description mentions that a token has been added to
    # or dropped from the station name, e.g. 
    # "op 1 January 1857; JUNCTION added 1 April 1864"
    # Here we're modifying the alternate names to add or drop these:
    modaltnames = []
    for x in list(added + dropped):
        if not x in mainst:
            modaltnames.append(mainst + " " + x)
        else:
            modaltnames.append(re.sub(r"\b%s\b" % x, "", mainst))
        if not x in subst:
            modaltnames.append(subst + " " + x)
        else:
            modaltnames.append(re.sub(r"\b%s\b" % x, "", subst))
    modaltnames = list(set(modaltnames))
    altnames = list(altnames)
    altnames.append(modaltnames)

    # Find full tokens:
    # Substations and alternate names are very often abbreviated, e.g.
    # "[...] became Y R & B P 1 November 1870 [...]",
    # where "Y R & B P" is short for "York Road and Battersea Park",
    # where full tokens are found either in the main station, substation
    # or in the alternate names. Therefore, in this step we are collecting
    # all full tokens and assume that an initial will refer to the first
    # mentioned token that starts with this initial.
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
    flt_altnames = [mainst]
    flt_altnames.append(subst)
    flt_altnames += list(set([item for sublist in altnames for item in sublist]))
    altname_tokens = []
    for altn in flt_altnames:
        altn = altn.translate(translator).split()
        altname_tokens += [x for x in altn if re.match(r"\b[A-Z]{2,}\b", x) and x not in altname_tokens and x not in ("AND", "FOR")]

    # Replace initials with token:
    proc_altnames = []
    for x in list(set(repl + prev + altrn + modaltnames)):
        tsub = []
        remsub = []
        initial_repl = False
        for w in x.split():
            if w == "&":
                w = "AND"
            if len(w) == 1:
                for altt in altname_tokens:
                    if altt.startswith(w) and not altt in tsub:
                        tsub.append(altt)
                        remsub.append(w)
                        break
                if not any(altt.startswith(w) for altt in altname_tokens):
                    tsub.append(w)
            else:
                tsub.append(w)

        proc_altnames.append(" ".join(tsub))

    # Only accept an alternate name if it's not a keyword in Quicks and has length of at least three characters:
    proc_altnames = [x for x in proc_altnames if len(x) >= 3 and not x in list(dCompanies.keys()) + stntypes + keywords and not x in (mainst, subst)]

    return proc_altnames


# -----------------------------------------------
# Detect alternate names in the description of an entry
def detect_altnames(description, mainst, subst):
    
    alternate_names = []
    
    # -----------------------------------
    # Remove non-printable characters:
    description = ''.join([x if x in string.printable else ' ' for x in description])
    
    # -----------------------------------
    # Remove notes (in parentheses), and text in curly and square brackets:
    description = re.sub(r'\([^)]*?\)', '', description)
    description = re.sub(r'\[[^)]*?\]', '', description)
    description = re.sub(r'\{[^)]*?\}', '', description)
    
    # -----------------------------------
    # Remove extra white spaces:
    description = re.sub(' +', ' ', description)
    
    # -----------------------------------
    # Capture alternate names...
    re_altname = r"(\b[A-Z]+(?:[A-Z \&\'\-(St|at|on|upon)])*[A-Z])+\b"
    
    # ... in their context:
    re_replacedby = r"\b(?:[Bb]ecame|[Rr]enamed|[Ll]ater|[Aa]ltered to|[Rr]eplaced by)\b " + re_altname
    re_previously1 = r"\b(?:as|[Ww]as|[Oo]riginally|[Aa]t first|[Ee]arly)\b:? " + re_altname
    re_previously2 = re_altname + " (?:until )(?:(?:[0-9]{1,2})? *(?:Jan ?(?:uary)?|Feb ?(?:ruary)?|Mar ?(?:ch)?|Apr ?(?:il)?|May ?|Jun ?(?:e)?|Jul ?(?:y)?|Aug ?(?:ust)?|Sep ?(?:tember)?|Oct ?(?:ober)?|Nov ?(?:ember)?|Dec ?(?:ember)?)? *(?:[12][0-9]{3}))"
    re_previously3 = re_altname + " (?:until)"
    re_previously3 = r"\b(?:[Uu]ntil [0-9]{4}) " + re_altname
    re_alternatively1 = r"\b(?:[Rr]eferred to|[Rr]efers to|[Ee]rratically|[Aa]lias|[Bb]rad had|hb had|[Ll]isted under|[Ii]ndiscriminately|[Nn]otice has|where)\b " + re_altname
    re_alternatively2 = re_altname + " (?:(?:(?:in )?(?:hb|[Bb]rad|NB|[Mm]urray))|(?:until renamed))"
    re_alternatively3 = re_altname + " (?:(?:[0-9]{1,2})? *(?:Jan ?(?:uary)?|Feb ?(?:ruary)?|Mar ?(?:ch)?|Apr ?(?:il)?|May ?|Jun ?(?:e)?|Jul ?(?:y)?|Aug ?(?:ust)?|Sep ?(?:tember)?|Oct ?(?:ober)?|Nov ?(?:ember)?|Dec ?(?:ember)?)? *(?:[12][0-9]{3}))"
    re_added1 = r"\b(?:[Aa]dded)\b " + re_altname
    re_added2 = re_altname + " (?:(?:was )?added)"
    re_dropped1 = r"\b(?:[Dd]ropped)\b " + re_altname
    re_dropped2 = re_altname + " (?:dropped)"
    re_referenced = r"\b(?:[Ss]ee|[Ss]ee under)\b " + re_altname
    
    # Find all occurrences of alternate names in the description:
    replacedby = re.findall(re_replacedby, description)
    previously = re.findall(re_previously1, description) + re.findall(re_previously2, description) + re.findall(re_previously3, description)
    alternatively = re.findall(re_alternatively1, description) + re.findall(re_alternatively2, description) + re.findall(re_alternatively3, description)
    added = re.findall(re_added1, description) + re.findall(re_added2, description)
    dropped = re.findall(re_dropped1, description) + re.findall(re_dropped2, description)
    referenced = re.findall(re_referenced, description)
    
    alternate_names = (replacedby, previously, alternatively, added, dropped)
    proc_altnames = process_altnames(alternate_names, mainst, subst)
    
    return proc_altnames, referenced
    
    
# -----------------------------------------------
def detect_mapsInfo(description):
    
    # -----------------------------------
    # Remove non-printable characters:
    description = ''.join([x if x in string.printable else ' ' for x in description])
    
    # -----------------------------------
    # Remove extra white spaces:
    description = re.sub(' +', ' ', description)
    
    # Extract location information from maps (enclosed in curly brackets)
    locsMapsIndex = ""
    locsMapsDescr = ""
    mapsinfo = re.match(r'.*?(\{.*?\}).*', description)
    if mapsinfo:
        mapnumber = re.match(r'\{map ([0-9]+).*\}.*', mapsinfo.group(1))
        if mapnumber:
            locsMapsIndex = mapnumber.group(1)
        else:
            locsMapsDescr = mapsinfo.group(1)
    
    return locsMapsIndex, locsMapsDescr


# -----------------------------------------------
def capture_dates(description):
    opening_dates = []
    closing_dates = []
    
    # -----------------------------------
    # Remove non-printable characters:
    description = ''.join([x if x in string.printable else ' ' for x in description])
    
    # -----------------------------------
    # Remove notes (in parentheses), and text in curly and square brackets:
    description = re.sub(r'\([^)]*?\)', '', description)
    description = re.sub(r'\[[^)]*?\]', '', description)
    description = re.sub(r'\{[^)]*?\}', '', description)
    
    # -----------------------------------
    # Remove extra white spaces:
    description = re.sub(' +', ' ', description)
    
    # -----------------------------------
    # Capture opening dates:
    re_op_date_standard = r"\b(?:[Rr]e)?[Oo]p(?:en(?:ed)?)?\b(?: \[(?:[A-Z].*?)\])? *((?:[0-9]{1,2})? *(?:Jan ?(?:uary)?|Feb ?(?:ruary)?|Mar ?(?:ch)?|Apr ?(?:il)?|May ?|Jun ?(?:e)?|Jul ?(?:y)?|Aug ?(?:ust)?|Sep ?(?:tember)?|Oct ?(?:ober)?|Nov ?(?:ember)?|Dec ?(?:ember)?) *(?:[12][0-9]{3}))"
    re_op_date_reverse = r"\b(?:[Rr]e)?[Oo]p(?:en(?:ed)?)?\b(?: \[([?:A-Z].*?)\])? *(?:(?:[12][0-9]{3}) *(?:Jan ?(?:uary)?|Feb ?(?:ruary)?|Mar ?(?:ch)?|Apr ?(?:il)?|May ?|Jun ?(?:e)?|Jul ?(?:y)?|Aug ?(?:ust)?|Sep ?(?:tember)?|Oct ?(?:ober)?|Nov ?(?:ember)?|Dec ?(?:ember)?) *(?:[0-9]{1,2})?)"
    re_op_date_nomark = r"\[[A-Za-z\&\;]+\] *((?:[0-9]{1,2})? *(?:Jan ?(?:uary)?|Feb ?(?:ruary)?|Mar ?(?:ch)?|Apr ?(?:il)?|May ?|Jun ?(?:e)?|Jul ?(?:y)?|Aug ?(?:ust)?|Sep ?(?:tember)?|Oct ?(?:ober)?|Nov ?(?:ember)?|Dec ?(?:ember)?) *(?:[12][0-9]{3}))"
    re_op_date_flexible = r"\b(?:[Rr]e)?[Oo]p(?:en(?:ed)?)?\b(?: \[(?:[A-Z].*?)\])? *(?:(?:[a-z]+) +)+((?:[0-9]{1,2})? *(?:Jan ?(?:uary)?|Feb ?(?:ruary)?|Mar ?(?:ch)?|Apr ?(?:il)?|May ?|Jun ?(?:e)?|Jul ?(?:y)?|Aug ?(?:ust)?|Sep ?(?:tember)?|Oct ?(?:ober)?|Nov ?(?:ember)?|Dec ?(?:ember)?) *(?:[12][0-9]{3}))"
    re_op_date_flexreverse = r"\b(?:[Rr]e)?[Oo]p(?:en(?:ed)?)?\b(?: \[(?:[A-Z].*?)\])? *(?:(?:[a-z]+) +)+((?:(?:[12][0-9]{3}) *(?:Jan ?(?:uary)?|Feb ?(?:ruary)?|Mar ?(?:ch)?|Apr ?(?:il)?|May ?|Jun ?(?:e)?|Jul ?(?:y)?|Aug ?(?:ust)?|Sep ?(?:tember)?|Oct ?(?:ober)?|Nov ?(?:ember)?|Dec ?(?:ember)?)? *(?:[0-9]{1,2})?))"
    re_op_date_flexnomark = r"\[[A-Za-z\&\;]+\] *(?:(?:[A-Za-z]+) +)+((?:[0-9]{1,2})? *(?:Jan ?(?:uary)?|Feb ?(?:ruary)?|Mar ?(?:ch)?|Apr ?(?:il)?|May ?|Jun ?(?:e)?|Jul ?(?:y)?|Aug ?(?:ust)?|Sep ?(?:tember)?|Oct ?(?:ober)?|Nov ?(?:ember)?|Dec ?(?:ember)?) *(?:[12][0-9]{3}))"
    re_op_firstinbrad = r"[Ff]irst *(?:(?:[a-z]+) +)+[Bb]rad*(?:(?:[a-z]+) +)+((?:[0-9]{1,2})? *(?:Jan ?(?:uary)?|Feb ?(?:ruary)?|Mar ?(?:ch)?|Apr ?(?:il)?|May ?|Jun ?(?:e)?|Jul ?(?:y)?|Aug ?(?:ust)?|Sep ?(?:tember)?|Oct ?(?:ober)?|Nov ?(?:ember)?|Dec ?(?:ember)?) *(?:[12][0-9]{3}))"
    
    opst = re.findall(re_op_date_standard, description)
    oprv = re.findall(re_op_date_reverse, description)
    opnm = re.findall(re_op_date_nomark, description)
    opfl = re.findall(re_op_date_flexible, description)
    opflrv = re.findall(re_op_date_flexreverse, description)
    opnmfl = re.findall(re_op_date_flexnomark, description)
    opfib = re.findall(re_op_firstinbrad, description)
    
    capturedOp = list(set(opst+oprv+opnm+opfl+opflrv+opnmfl))
    
    # If no openingdate has been found, add first-in-brad date if exists:
    if not capturedOp:
        capturedOp += opfib
    
    opening_dates = capturedOp
    
    # -----------------------------------
    # Capture closing dates:
    re_cl_date_standard = r"\b(?:re)?[Cc]?lo(?:sed)?\b *((?:[0-9]{1,2})? *(?:Jan ?(?:uary)?|Feb ?(?:ruary)?|Mar ?(?:ch)?|Apr ?(?:il)?|May ?|Jun ?(?:e)?|Jul ?(?:y)?|Aug ?(?:ust)?|Sep ?(?:tember)?|Oct ?(?:ober)?|Nov ?(?:ember)?|Dec ?(?:ember)?) *(?:[12][0-9]{3}))"
    re_cl_date_reverse = r"\b(?:re)?[Cc]?lo(?:sed)?\b *(?:(?:[12][0-9]{3}) *(?:Jan ?(?:uary)?|Feb ?(?:ruary)?|Mar ?(?:ch)?|Apr ?(?:il)?|May ?|Jun ?(?:e)?|Jul ?(?:y)?|Aug ?(?:ust)?|Sep ?(?:tember)?|Oct ?(?:ober)?|Nov ?(?:ember)?|Dec ?(?:ember)?) *(?:[0-9]{1,2})?)"
    re_cl_date_flexible = r"\b(?:re)?[Cc]?lo(?:sed)?\b *(?:(?:[A-Za-z]+) )+((?:[0-9]{1,2})? *(?:Jan ?(?:uary)?|Feb ?(?:ruary)?|Mar ?(?:ch)?|Apr ?(?:il)?|May ?|Jun ?(?:e)?|Jul ?(?:y)?|Aug ?(?:ust)?|Sep ?(?:tember)?|Oct ?(?:ober)?|Nov ?(?:ember)?|Dec ?(?:ember)?) *(?:[12][0-9]{3}))"
    re_cl_date_flexreverse = r"\b(?:re)?[Cc]?lo(?:sed)?\b *(?:(?:[A-Za-z]+) )+((?:(?:[12][0-9]{3}) *(?:Jan ?(?:uary)?|Feb ?(?:ruary)?|Mar ?(?:ch)?|Apr ?(?:il)?|May ?|Jun ?(?:e)?|Jul ?(?:y)?|Aug ?(?:ust)?|Sep ?(?:tember)?|Oct ?(?:ober)?|Nov ?(?:ember)?|Dec ?(?:ember)?)? *(?:[0-9]{1,2})?))"
    re_cl_date_last = r"[Ll]ast *(?:(?:[A-Za-z]+) +)*((?:[0-9]{1,2})? *(?:Jan ?(?:uary)?|Feb ?(?:ruary)?|Mar ?(?:ch)?|Apr ?(?:il)?|May ?|Jun ?(?:e)?|Jul ?(?:y)?|Aug ?(?:ust)?|Sep ?(?:tember)?|Oct ?(?:ober)?|Nov ?(?:ember)?|Dec ?(?:ember)?) *(?:[12][0-9]{3}))"
    clst = re.findall(re_cl_date_standard, description)
    clrv = re.findall(re_cl_date_reverse, description)
    clfl = re.findall(re_cl_date_flexible, description)
    clflrv = re.findall(re_cl_date_flexreverse, description)
    cllast = re.findall(re_cl_date_last, description)
    
    capturedClo = list(set(clst+clrv+clfl+clflrv))
    # If "still open" or "still in use" in description, add date of first edition (2001) as closing date:
    if "still open" in description.lower() or "still in use" in description.lower():
        capturedClo.append("31 December 2001")
        
    # If no closing date has been found, add last-in-brad date if exists:
    if not capturedClo:
        capturedClo += cllast
        
    closing_dates = capturedClo
    
    # Parse date string and convert to datetime
    opening_dtime = [dateparser.parse(d) for d in opening_dates]
    closing_dtime = [dateparser.parse(d) for d in closing_dates]
    
    # Do not keep None dates
    opening_dtime = [d for d in opening_dates if d]
    closing_dtime = [d for d in closing_dates if d]
    
    # Keep first opening date and last closing date
    # Has there been an interruption in the use of this railway station?
    # We consider there has been if there are two or more opening and/or closing dates.
    hiatus = False
    first_opening_date = None
    last_closing_date = None
    if opening_dtime:
        first_opening_date = min(opening_dtime)
        hiatus = True if len(opening_dates) > 1 else False
    if closing_dtime:
        last_closing_date = max(closing_dtime)
        hiatus = True if len(closing_dates) > 1 else False
    
    return first_opening_date, last_closing_date, hiatus
    
    
# -----------------------------------------------
def format_for_candranker(output_dir, output_filename,  unique_placenames_array):
    """
    This function returns the unique alternate names in a given gazetteer
    in the format required by DeezyMatch candidate ranker.
    
    Arguments:
        output_dir (str): directory where DeezyMatch query files are stored.
        outpuf_filename (str): filename of the query file.
        unique_placenames_array (list): unique names that will be Deezy
                                        Match queries.
    """
    gazname = output_dir + output_filename

    with open(gazname + ".txt", "w") as fw:
        for pl in unique_placenames_array:
            pl = pl.strip()
            if pl:
                pl = pl.replace('"', "")
                fw.write(pl.strip() + "\t0\tfalse\n")
                
                
# -----------------------------------------------
def prepare_alt_queries(parsedf, scen, split):
    mainId = []
    substId = []
    names = []
    for i, row in parsedf.iterrows():
        t = row["Altnames"]
        for x in t:
            mainId.append(row["MainId"])
            substId.append(row["SubId"])
            names.append(x)
    # Dataframe of alternate names:
    df_tmp = pd.DataFrame()
    df_tmp[scen] = names
    df_tmp["MainId"] = mainId
    df_tmp["SubId"] = substId
    df_tmp.to_pickle("../processed/quicks/quicks_" + scen.lower() + "_" + split.lower() + ".pkl")