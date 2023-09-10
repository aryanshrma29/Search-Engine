# -*- coding: utf-8 -*-


import time
import schedule
def crawler():
    print('Crawling Started')
    import json
    import os
    from urllib.robotparser import RobotFileParser
    import nltk
    nltk.download("stopwords")
    from nltk.corpus import stopwords
    nltk.download("punkt")
    from nltk.tokenize import word_tokenize
    from nltk.stem import PorterStemmer
    from bs4 import BeautifulSoup
    import requests

    url = "https://pureportal.coventry.ac.uk/en/organisations/research-centre-for-computational-science-and-mathematical-modell/publications/"

    def is_allowed(url):
       rp = RobotFileParser()
       rp.set_url(url + '/robots.txt')
       rp.read()
       return rp.can_fetch('*', url)

    def getsoup(url):
        user_agent = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        r= requests.get(url, headers= user_agent)
        soup = BeautifulSoup(r.text,'html.parser')
        return soup

    def getNextPage(soup):
        page=soup.find('nav', {'class':'pages'})
        if soup.find('li',{'class' : 'next'}):
            url= 'https://pureportal.coventry.ac.uk/' +  str(page.find('li', {'class': 'next'}).find('a')['href'])
            return url
        else:
            return

    print('Checking total number of links to be fetched')
    links_to_scan = []

    while True:
        soup = getsoup(url)
        for h3_tag in soup.find_all("h3"):
          a_tag = h3_tag.find('a')
          links_to_scan.append(a_tag.attrs['href'])
        url = getNextPage(soup)
        if not url:
            break
    print('Total number of links to be fetched: ',len(links_to_scan))

    import json

    results_dict = {}
    count = 0
    print('Retrieving Publications of CSM members only')
    for link in links_to_scan:
        if is_allowed(link):
              print('Link allowed for crawling')
              soup = getsoup(link)

              print(f'Retrieving data from link {count%50+1} Page {count//50+1} : {link}')
              title= soup.find('div',{'class' : 'rendering'}).find('h1').find('span').string

              #applying preprocessing to title:
              import re,string
              titlex = re.sub(r'[^\x00-\x7F]+', ' ', title)
                  # Removing Mentions
              titlex = re.sub(r'@\w+', '', titlex)
                  # Lowercase the document
              titlex = titlex.lower()
                  #Removing Punctuations
              titlex=re.sub(r'[%s]'% re.escape(string.punctuation),' ',titlex)
                  # Removing double space
              titlex = re.sub(r'\s{2,}', ' ', titlex)
              stop_words = stopwords.words('english')
              ps = PorterStemmer()
              tokens = word_tokenize(titlex)
              tmp = ""
              for w in tokens:
                  if w not in stop_words:
                       tmp += ps.stem(w) + " "
                  filtered_title = tmp

              url = link

              t = soup.find_all('a',{'class' : 'link person'})
              Author_dict = {}
              for x in t:
                Author = x.find('span').string
                author_url = x.get('href')
                current_author = {Author:author_url}
                Author_dict.update(current_author)

              year = soup.find('span',{'class' : 'date'}).string[-4:]
              Publication_details = {'Title':title,
                                     'url':url,
                                     'Authors':Author_dict,
                                     'Year':year}
              results = {'title':filtered_title,
                        'Publication Details':Publication_details}
              all_titles_dict = {count:results}
              results_dict.update(all_titles_dict)
              count += 1
              print(results['Publication Details'])


    #updating json file after all the links are fetched
    with open('data.json','w') as json_file:
               file_content = ''
    with open('data.json','w') as json_file:
               file_content += json.dumps(results_dict, indent=2)
               json_file.write(file_content)
    print('Crawler Paused\n')

crawler()
schedule.clear()
schedule.every(7).days.do(crawler)

while True:
  schedule.run_pending()
  time.sleep(1)



import json
with open('/content/data.json') as f:
    data = json.load(f)

all_authors = []
for x in data.values():
  for y in x['Publication Details']['Authors'].keys():
    if y not in all_authors:
      all_authors.append(y)

print(all_authors)
print('Total number of authors are:',len(all_authors))

import json
with open('/content/data.json') as f:
    data = json.load(f)
Filtred_titles = []
for publicationDetails in data:
  Filtred_titles.append(data[publicationDetails]["title"])
print(Filtred_titles)

def search_query(query):
      import re,string
      import nltk
      nltk.download("stopwords")
      from nltk.corpus import stopwords
      nltk.download("punkt")
      from nltk.tokenize import word_tokenize
      from nltk.stem import PorterStemmer
      x = re.sub(r'[^\x00-\x7F]+', ' ',str(query))
         # Removing Mentions
      x = re.sub(r'@\w+', '',x)
         # Lowercase
      x = x.lower()
         #Removing Punctuations
      x=re.sub(r'[%s]'% re.escape(string.punctuation),' ',x)
         # Remove the doubled space
      x = re.sub(r'\s{2,}', ' ',x)
      stop_words = stopwords.words('english')
      ps = PorterStemmer()
      tokens = word_tokenize(x)
      tmp = ""
      for w in tokens:
          if w not in stop_words:
                tmp += ps.stem(w) + " "
      filtered_search = tmp
      filtered_search_words = filtered_search.split()


      import operator
      count=0
      answer_indices = []
      answers_dict = {}

      for x in Filtred_titles:
        doc_words = x.split()
        common_words = []
        for y in doc_words:
          if y in filtered_search_words:
            common_words.append(y)
        if len(common_words) > 0:
          answer_indices.append(count)
          answers = {count:len(common_words)}
          answers_dict.update(answers)
        count+=1

      #print(answer_indices)
      desc_answers = dict(sorted(answers_dict.items(),key=operator.itemgetter(1), reverse = True))   #for ranked results

      for x,y in enumerate(desc_answers):
        print(data[str(y)]['Publication Details']['Title'])
        print(data[str(y)]['Publication Details']['url'])
        print('authors:')
        for a,b in data[str(y)]['Publication Details']['Authors'].items():
          print(f'{a} : {b}')
        year = data[str(y)]['Publication Details']['Year']
        print('Year of Publication : ',year)
        print('\n')

search_query('based quantum-behaved particle An SMT solver for non-linear')















!pip install schedule