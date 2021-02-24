from urllib.parse import unquote

def show_top_entity_candidates(mention,mention_to_entities):
    cands = [["/wiki/"+unquote(x).replace(" ","_"),score] for x,score in mention_to_entities[mention].most_common(3)]
    return cands

def generate_wikilink(text,mention,entity,aspect):
    if aspect!=None and len(aspect)>1:
        entity = entity+"#"+aspect
    
    link = '<a href="https://en.wikipedia.org/wiki/'+entity+'">'+mention+'</a>'
    text = text.replace(mention,link)
    return text