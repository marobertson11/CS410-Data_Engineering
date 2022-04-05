import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
%matplotlib inline
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pylab import rcParams
url = "http://www.hubertiming.com/results/2017GPTR10K"
html = urlopen(url)
soup = BeautifulSoup(html, 'lxml')
type(soup)
#Get the title
title = soup.title
#print(title)

#print text
text = soup.get_text()
#print(soup.text)

#soup.find_all('a')

#all_links = soup.find_all("a")
#for link in all_links:
#    print(link.get("href"))

rows = soup.find_all('tr')
#print(rows[:10])

for row in rows:
    row_td = row.find_all('td')
#print(row_td)
#type(row_td)

str_cells = str(row_td)
cleantext = BeautifulSoup(str_cells, "lxml").get_text()
#print(cleantext)

list_rows=[]
for row in rows:
    cells = row.find_all('td')
    str_cells = str(cells)
    clean = re.compile('<.*?>')
    clean2 = (re.sub(clean, '', str_cells))
    clean3 = re.compile('\\n')
    clean4 = (re.sub(clean3,'', str_cells))
    clean5 = re.compile('\\r')
    clean6 = (re.sub(clean, '', str_cells))
    list_rows.append(clean2)
#print(clean2)
#type(clean2)

df = pd.DataFrame(list_rows)
df.head(10)

df1 = df[0].str.split(',',expand = True)
df1[0] = df1[0].str.strip('[')
df1.head(10)

col_labels = soup.find_all('th')
all_header=[]
col_str = str(col_labels)
cleantext2 = BeautifulSoup(col_str, "lxml").get_text()
all_header.append(cleantext2)
#print(all_header)

df2 = pd.DataFrame(all_header)
df2.head()

df3 = df2[0].str.split(',',expand = True)
df3.head()

frames = [df3,df1]
df4 = pd.concat(frames)
df4.head(10)

df5 = df4.rename(columns=df4.iloc[0])
df5.head()

#df5.info()
df5.shape

df6 = df5.dropna(axis=0, how='any')
#df6.info()
df6.shape

df7 = df6.drop([0])
df7.head()

df7.rename(columns = {'[Place': 'Place'}, inplace=True)
df7.rename(columns = {' Team]': 'Team'}, inplace=True)
df7.head()

df7['Team'] = df7['Team'].str.strip(']')
df7.head()

time_list = df7[' Chip Time'].tolist()
time_mins=[]
for i in time_list:
    if(len(i.split(':')) == 3):
        h, m, s = i.split(':')
    else:
        h=0
        m, s = i.split(':')
    math = (int(h) * 3600 + int(m) * 60 + int(s)) / 60
    time_mins.append(math)
#print(time_mins)

df7['Runner_mins'] = time_mins
df7.tail()

df7.describe(include=[np.number])

rcParams['figure.figsize'] = 15, 5
 
df7.boxplot(column='Runner_mins')
plt.grid(True, axis='y')
plt.ylabel('Chip Time')
plt.xticks([1], ['Runners'])
plt.show()

x = df7['Runner_mins']
ax = sns.distplot(x, hist=True, kde=True, rug=False, color='m', bins=25, hist_kws={'edgecolor':'black'})
plt.show()

f_fuko = df7.loc[df7[' Gender']==' F']['Runner_mins']
m_fuko = df7.loc[df7[' Gender']==' M']['Runner_mins']
sns.distplot(f_fuko, hist=True, kde=True, rug=False, hist_kws={'edgecolor':'black'}, label='Female')
sns.distplot(m_fuko, hist=False, kde=True, rug=False, hist_kws={'edgecolor':'black'}, label='Male')
plt.legend()

g_stats = df7.groupby(" Gender", as_index=True).describe()
print(g_stats)

df7.boxplot(column='Runner_mins', by=' Gender')
plt.ylabel('Chip Time')
plt.suptitle("")
