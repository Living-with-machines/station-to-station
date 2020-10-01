from bs4 import BeautifulSoup as bs
import re

def preprocess_title(tp):
    t = tp
    
    # Initial preprocessing
    t = t.strip()
    t = re.sub(r",$", "", t)
    
    # Regex to capture appositions
    re_appo = r".+(\(.+\))"
    
    # Common location descriptors:
    descr = ["Great", "Little", "Low", "High", "Higher", "East", "West", "North", "South", "Lower", "Upper", "New", "Old", "Castle", "Church", "The"]
    
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
    
    # Text in parentheses is moved to the apposition:
    if re.match(re_appo, t):
        apposition = re.match(re_appo, t).group(1)
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
    # 7. Filter out if toponym is exactly one of common specifying adjectives:
    alts_toponym = [a for a in alts_toponym if not a in descr]
    
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
    alts_context = [a for a in alts_context if not a in descr]

    return alts_toponym, alts_context

def process_content(ctnt):
    clean_text = []
    ctnt_bs = bs(ctnt, 'lxml')
    paragraphs = ctnt_bs.findAll("para")
    for p in paragraphs:
        clean_text.append(p.get_text())
    return clean_text