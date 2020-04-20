import requests
import requests_cache
import lxml.html as lh
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

base_url = 'https://cfrsearch.nictusa.com/documents/473261/details/filing/contributions?schedule=1A&changes=0'
requests_cache.install_cache(cache_name='whitmer_donor_cache', backend='sqlite', expire_after=180)

#Scrape Table Cells
page = requests.get(base_url)
doc = lh.fromstring(page.content)
tr_elements = doc.xpath('//tr')
#print([len(T) for T in tr_elements[:12]])

#Parse Table Header
tr_elements = doc.xpath('//tr')
col = []
i = 0
for t in tr_elements[0]:
    i += 1
    name = t.text_content()
    print('%d:"%s"'%(i,name))
    col.append((name,[]))

###Create Pandas Dataframe###
for j in range(1,len(tr_elements)):
    T = tr_elements[j]
    if len(T)!=9:
        break
    i = 0
    for t in T.iterchildren():
        data = t.text_content() 
        if i>0:
            try:
                data = int(data)
            except:
                pass
        col[i][1].append(data)
        i+=1
#print([len(C) for (title,C) in col])

###Format Dataframe###
Dict = {title:column for (title,column) in col}
df = pd.DataFrame(Dict)
df = df.replace('\n','', regex=True)
df = df.replace('  ', '', regex=True)
df['Receiving Committee'] = df['Receiving Committee'].apply(lambda x : x.strip().capitalize())

###Print Dataframe###
with pd.option_context('display.max_rows', 10, 'display.max_columns', 10):  # more options can be specified also
    print(df)

###Create Sql Database###
conn = sqlite3.connect('Gretchen_Whitmer_Donors_2018.db')
c = conn.cursor()
c.execute('CREATE TABLE WHITMER_DONORS (df)')
conn.commit()
df.to_sql('WHITMER_DONORS', conn, if_exists='replace', index = False)

###Sql Statements###
