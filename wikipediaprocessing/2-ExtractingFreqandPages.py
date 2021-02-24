# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import nltk,re, pickle, os, json
from bs4 import BeautifulSoup
from collections import Counter
from urllib.parse import quote
import multiprocessing as mp
from wikimapper import WikiMapper
import wptools

mapper = WikiMapper("/resources/wikidata2wikipedia/index_enwiki-20190420.db")

def get_all_ngrams(text,ngram_up_to):
    
    global all_mentions

    # removing html tags
    content = re.sub('<[^>]+>', '', text)
    
    #word tokenize
    tokens = nltk.word_tokenize(text)
    
    all_ngrams = [" ".join(x) for n in range(1,ngram_up_to+1) for x in nltk.ngrams(tokens,n)]        
     
    all_ngrams = [x for x in all_ngrams if x in all_mentions]
    
    return all_ngrams

def clean_page(page):
    
    global ngram_up_to
    
    entities = [x for x in page.findAll("a") if x.has_attr("href")]
     
    page_text = page.text
    all_ngrams = get_all_ngrams(page_text,ngram_up_to)

    content_ngrams= Counter(all_ngrams)
    
    box_mentions = Counter([x.text for x in entities])
    box_entities = Counter([x["href"] for x in entities])
        
    mentions_dict = {x:[] for x in box_mentions}
    for e in entities:
        mentions_dict[e.text].append(e["href"])
    
    mentions_dict = {x:Counter(y) for x,y in mentions_dict.items()} 
    
    return [box_mentions,content_ngrams,box_entities,mentions_dict]


# %%
def get_sections (page):
    page = page.text.strip().split("\n")
    sections = {"Main":{"order":1,"content":[]}}
    dict_key = "Main"
    ct = 1
    for line in page:
        if not "Section::::" in line:
            sections[dict_key]["content"].append(line)
        else:
            ct+=1
            dict_key = line.replace("Section::::","")[:-1]
            sections[dict_key] = {"order":ct,"content":[]}
            
    sections = {x:y for x,y in sections.items() if len(y["content"])>0}
    return sections


# %%
def process_doc(doc):
    content = open(proessed_docs+folder+"/"+doc).read()
    content = BeautifulSoup(content,"lxml").findAll("doc")
    pages = []
    for page in content:
        title = page["title"]
        wikidata_id = mapper.title_to_id(title.replace(" ","_"))
        if wikidata_id is None:
            try:
                wikidata_id = wptools.page(title,silent=True).get_wikidata().data["wikibase"]
            except LookupError:
                wikidata_id = None
        sections = {"wikidata_id":wikidata_id,"title":title,"sections": get_sections(page)}
        r = [title]+ clean_page(page) + [sections]
        pages.append([r])
    return pages


# %%
# load the set of all possible mentions 

with open("/resources/wikipedia/extractedResources/all_mentions.pickle", "rb") as f:
    all_mentions = pickle.load(f)


# %%
# the output already used before, coming from WikiExtractor

proessed_docs = "/resources/wikipedia/processedWiki/"

ngram_up_to = 3

# again, the number of cpu
N= mp.cpu_count()-2

if __name__ == '__main__':
    
    step = 1

    for folder in os.listdir(proessed_docs):
        
            with mp.Pool(processes = N) as p:
                res = p.map(process_doc, os.listdir(proessed_docs+folder))

            res = [y for x in res for y in x]
            
            # separating frequency counts from aspects
            freq_res = [x[0][:-1] for x in res]
            sections = [x[0][-1] for x in res]
            
            # saving sections independently
            for sect in sections:
                title = sect["title"]
                wikidata_id = sect["wikidata_id"]
                if wikidata_id is not None:
                    s = sect["sections"]
                    try:
                        with open('/resources/wikipedia/extractedResources/Pages/'+wikidata_id+".json", 'w') as fp:
                            json.dump(s, fp)
                    except OSError as e:
                        print (e)
                        continue
                else:
                    print ("Missing:",title)
            # storing counts, still divided in folders       
            with open('/resources/wikipedia/extractedResources/Store-Counts/'+str(step)+".json", 'w') as fp:
                json.dump(freq_res, fp)
            
            print("Done %s folders over %s" % (step, len(os.listdir(proessed_docs))))
            step+=1


# %%



