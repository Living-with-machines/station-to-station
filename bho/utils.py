from bs4 import BeautifulSoup as bs
import re


# ------------------- Process BHO xml files --------------------
# Given an xml-formatted string corresponding to a section in the
# BHO topographical dictionaries, return:
# * place_title: the title of the dictonary entry.
# * content: the content of the dictionary entry (with xml tags).
def clean_section(s):
    has_paragraph = False
    place_title = ""
    clean_lines = []
    lines = s.split("\n")
    for line in lines:
            
        if re.search("s[0-9]+\">", line): # If line does not contain sth like: s1">
            line = re.sub("s[0-9]+\">(.*)", r"\1", line)
            line = line.strip()
            if line:
                clean_lines.append(line)
        if re.search("</section>", line): # If line does not contain sth like: s1">
            line = line.strip()
            line = re.sub("(.*)</section>", r"\1", line)
            if line:
                clean_lines.append(line)
        else:
            clean_lines.append(line)
                
    lines = clean_lines
    clean_lines = []
                
    for line in lines:
        line = line.strip()
        if not re.match("s[0-9]+\">", line) and not line == "</section>": # If line does not have this shape: s1">
            if line.startswith("<para"):
                has_paragraph = True
                clean_lines.append(line)
            else:
                if has_paragraph == False:
                    place_title = line
                else:
                    clean_lines.append(line)
    content = " ".join(clean_lines)
    return place_title, content



# ------------------- Preprocess title --------------------
# This function takes the title of an entry and processes
# it, and outputs:
# * alts_toponym: a list of toponym and alternate names.
# * alts_context: a list of disambiguators, i.e. words that
#                 are neither parts of the toponym or alternate
#                 names but that are present in the entry
#                 title and can help disambiguate.
#
# Example:
# * Input: "Abbas-Combe, or Temple-Combe (St. Mary)"
# * Output:
#     * alts_toponym: ['Abbas-Combe', 'Temple-Combe']
#     # alts_context: ['St. Mary']
def preprocess_title(tp):
    t = tp
    
    # Initial preprocessing
    t = t.strip()
    t = re.sub(r",$", "", t)
    t = str(t.encode().decode("utf-8")).replace("&amp;ygrave;", "y")
    t = str(t.encode().decode("utf-8")).replace("&amp;Ygrave;", "Y")
    t = str(t.encode().decode("utf-8")).replace(" &amp;c.", " etc")
    t = str(t.encode().decode("utf-8")).replace(" &amp; ", " and ")
    
    # Regex to capture appositions
    re_appo = r".+(\(.+\))"
    
    # Common location descriptors:
    descr = ["Great", "Little", "Low", "High", "Higher", "East", "West", "North", "South", "Lower", "Upper", "New", "Old", "Castle", "Church", "The", "Street", "Above", "Below"]
    
    context = []
    apposition = ""
    redirected = False
    toponym = ""
    main_toponym = ""
    alts_toponym = []
    alts_context = []
    
    # Specific case of formatting with "St.": "Bride's (St.) Netherwent" into "St. Bride's Netherwent"
    if re.match("^(.+ )\(St\.\) ?(.*)", t):
        t = "St. " + "".join(re.match("^(.+ )\(St\.\) ?(.*)", t).groups())
    
    # Specific case of formatting with "St.": "Michael, St., Caerhays" into "St. Michael Caerhays"
    if re.match("^(.+ )St\., ?(.*)", t):
        groups = re.match("^(.+ )St\., ?(.*)", t).groups()
        ttmp = "St. "
        for g in groups:
            ttmp += g
        t = ttmp
    
    # Text in parentheses is moved to the apposition:
    if re.match(re_appo, t):
        apposition = re.match(re_appo, t).group(1)
        # If apposition stripped of paretheses is one of common location descriptors,
        # remove it as apposition and make it part of toponym, e.g. "Mawr (Higher)"
        # becomes "Higher Mawr":
        stripped_appo = apposition.strip()[1:-1]
        if stripped_appo in descr:
            ttmp = t.replace(apposition, "").strip()
            # Apposition is attached at the end of the string if it's one of the following:
            if stripped_appo in ["Above", "Below", "Street", "Castle", "Church"]:
                toponym = ttmp + " " + stripped_appo
            # Otherwise it's attached at the beginning of the string:
            else:
                toponym = stripped_appo + " " + ttmp
            t = toponym
            apposition = ""
        else:
            toponym = t.replace(apposition, "")
            toponym = re.sub(" +", " ", toponym)
            apposition = apposition.replace("(", "")
            apposition = apposition.replace(")", "")
            apposition = apposition.strip()
    else:
        toponym = t
        
    dels_topalt = r",? [Oo]r |,? [Oo]therwise "        
    dels_ctxtalt = r",? [Ww]ith |, [Aa]nd | - "

    # Clean the toponym with the following steps
    # ==========================================
    # 1. Split place_title if "(, )?with" is in the name, where
    # the first element is the toponym, the following elements
    # are part of the context:
    tmp_withsplit = re.split(dels_ctxtalt, toponym)
    toponym = tmp_withsplit[0]
    tmp_context = tmp_withsplit[1:]
    # 2. Split place_title if it contains the word "or" or
    # "otherwise". All resulting elements are altnames of
    # the same place.
    tmp_toponym = []
    tmp_orsplit = re.split(dels_topalt, toponym)
    if len(tmp_orsplit) > 1:
        main_toponym = tmp_orsplit[0]
        tmp_toponym = tmp_orsplit[1:]
    else:
        main_toponym = tmp_orsplit[0]
    # 3. If the toponym is composed of two comma-separated elements,
    # (e.g. "Anstey, East"), join them in reverse order (i.e. "East
    # Anstey"). We only do this transformation to the first toponym
    # because the convention is that this format occurs only in the
    # first toponym of the entry title (e.g. it is "Marlow, or Great
    # Marlow" and not "Marlow, or Marlow, Great").
    if len(main_toponym.split(", ")) == 2:
        main_toponym = main_toponym.split(", ")[1].strip() + " " + main_toponym.split(", ")[0].strip()
    # 4. Keep non-empty string alternate names only:
    alts_toponym = [main_toponym]
    alts_toponym += tmp_toponym
    alts_toponym = [a.strip() for a in list(set(alts_toponym)) if a]
    # 5. Remove connector words "or", "otherwise" if necessary, and end of string comma:
    alts_toponym = [re.sub(r"^[Oo]r |^[Oo]therwise |,$", "", a).strip() for a in alts_toponym]
    # 6. Split any remaining comma-separated altname and flatten resulting list of lists:
    alts_toponym = [a.split(", ") for a in alts_toponym if a]
    alts_toponym = [item for sublist in alts_toponym for item in sublist]
    # 7. Filter out if toponym is exactly one of common specifying adjectives, unless
    # this is the full name of the location:
    alts_toponym = [a for a in alts_toponym if not (a in descr and not t == a and len(alts_toponym) > 1)]
    
    # Clean the context with similar steps
    # ====================================
    # Clean context with the same steps:
    tmp_context.append(apposition)
    tmp_context = list(set(tmp_context))
    # 1. Split place title according to the following delimiters:
    dels = r",? [Ww]ith |,? [Oo]r |,? [Oo]therwise |, [Aa]nd | - "
    for ctxt in tmp_context:
        alts_context += re.split(dels, ctxt)
    # 2. Keep non-empty string alternate names only:
    alts_context = [a.strip() for a in list(set(alts_context)) if a]
    # 3. Remove connector words "or", "otherwise", "with", and "and", and end of string comma:
    alts_context = [re.sub(r"^[Oo]r |^[Oo]therwise |^[Ww]ith |^[Aa]nd |,$", "", a) for a in alts_context]
    # 4. Split any remaining comma-separated altname and flatten resulting list of lists:
    alts_context = [a.split(", ") for a in alts_context if a]
    alts_context = [item for sublist in alts_context for item in sublist]
    # 5. Remove altname if it's just a descriptor:
    alts_context = [a for a in alts_context if not (a in descr and not t == a)]

    return alts_toponym, alts_context



# ------------------- Preprocess content --------------------
# Given an xml-formatted string (in this case the content/description
# of an entry), return a list of clean-text strings, corresponding to
# where each string corresponds to a paragraph.
def process_content(ctnt):
    clean_text = []
    ctnt_bs = bs(ctnt, 'lxml')
    paragraphs = ctnt_bs.findAll("para")
    for p in paragraphs:
        clean_text.append(p.get_text())
    return clean_text



# ------------------- Format queries for DeezyMatch candranker --------------------
def format_for_candranker(gazname, unique_placenames_array):
    """
    This function returns the unique alternate names in a given gazetteer
    in the format required by DeezyMatch candidate ranker."""
    with open(gazname + ".txt", "w") as fw:
        for pl in unique_placenames_array:
            pl = pl.strip()
            if pl:
                if not any(char.islower() for char in pl):
                    pl = pl.title()
                fw.write(pl.strip() + "\t0\tfalse\n")