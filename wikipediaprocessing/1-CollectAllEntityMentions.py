# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import os, json,pickle, pathlib
import multiprocessing as mp
from urllib.parse import quote
from bs4 import BeautifulSoup

def process_doc(doc):
    content = open(proessed_docs+folder+"/"+doc).read()
    soup = BeautifulSoup(content).findAll("doc")
    pages = []
    for page in soup:
        r = find_mentions(page)
        pages.append(r)
    return pages

def find_mentions(page):
    mentions = [x.text for x in page.findAll("a") if x.has_attr("href")]
    return mentions


# %%
processed_docs = "../resources/wikipedia/processedWiki/"

# how many cpu to be used
N= mp.cpu_count()-2

all_mentions = []

if __name__ == '__main__':


    for folder in os.listdir(processed_docs):
        if folder != ".gitkeep":
            with mp.Pool(processes = N) as p:
                res = p.map(process_doc, os.listdir(processed_docs+folder))
                
            res = list(set([z for x in res for y in x for z in y]))
            all_mentions +=res
            all_mentions = list(set(all_mentions))


all_mentions_dict = {x for x in all_mentions}


# %%
out = '../resources/wikipedia/extractedResources/'

pathlib.Path(out).mkdir(parents=True, exist_ok=True)

with open(out+'all_mentions.pickle', "wb") as fp:
    pickle.dump(all_mentions_dict, fp)


