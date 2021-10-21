import requests
from bs4 import BeautifulSoup
import csv
import nltk
from wordcloud import WordCloud
from natasha import (
    Segmenter,
    MorphVocab,

    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,

    PER,
    LOC,
    NamesExtractor,
    DatesExtractor,
    MoneyExtractor,
    AddrExtractor,

    Doc
)

segmenter = Segmenter()
morph_vocab = MorphVocab()

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)

names_extractor = NamesExtractor(morph_vocab)

stopwords = nltk.corpus.stopwords.words('russian')
stemmer = nltk.SnowballStemmer("russian")


manual_stopwords = ['|',"'",',','.',')',',','(','m',"'m","n't",'e.g',"'ve",'s',
                    '#','/','``',"'s","''",'!','r',']','=','[','s','&','%','*','...',
                    '1','2','3','4','5','6','7','8','9','10','--',"''",';','-',':', 'р',
                    'of', 'and', 'or', 'there', 'the', 'в', '«', '»', 'м', 'р', 'г', 'н',
                    '№', '—', 'i', '^']


URL = 'https://habr.com/ru/search/?q=адаптивность%20интерфейсов&target_type=posts&order=relevance'
HEADERS = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36 OPR/79.0.4143.72', 'accept' : '*/*'}
HOST ='https://habr.com/ru'
ANN = 'Анотация '
AUTHOR = 'Автор '
# FILE = 'Articles.csv'



def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r

"""
 def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Название', 'Ссылка', 'Аннотация'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['ANN']])
"""
def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagenation = soup.find_all('a', class_='tm-pagination__page')
    if pagenation:
        return int(pagenation[-1].get_text())
    else:
        return 1


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('article', class_='tm-articles-list__item' )

    articles = []

    for item in items:
        articles.append({
            'title': item.find('h2', class_='tm-article-snippet__title tm-article-snippet__title_h2').get_text(strip=True),
          #  'author': item.find('a', class_='tm-user-info__username').get_text(),
            'link': HOST + item.find('a', class_='tm-article-snippet__title-link').get('href'),
            'ANN': ANN + item.find('div', class_='article-formatted-body article-formatted-body_version-1').get_text().replace('\n\r\n', ' '),
        })
    return(articles)

def parse ():
    html= get_html(URL)
    if html.status_code == 200:
        articles = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count-1):
            print(f'Парсинг страницы {page} из {pages_count}...')
            html = get_html(URL, params={'page':page})
            articles.extend(get_content(html.text))
       # save_file(articles, FILE)
        return(articles)
    else:
        print('ERROR')

def stopwordFilter(stopword, words):
        filtered = [word for word in words if word not in stopword]
        return filtered

def prepareData(text):
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    for token in doc.tokens:
        token.lemmatize(morph_vocab)

    doc.parse_syntax(syntax_parser)
    doc.tag_ner(ner_tagger)
    for span in doc.spans:
        span.normalize(morph_vocab)

    for span in doc.spans:
        if span.type == PER:
            span.extract_fact(names_extractor)
    return doc

def exstractFacts(doc):
    lems = {_.text: _.lemma for _ in doc.tokens}
    lems = list(lems.values())
    lems = stopwordFilter(stopwords, lems)
    lems = stopwordFilter(manual_stopwords, lems)
    return lems

def extractNames(doc):
    names_dict = {_.normal: _.fact.as_dict for _ in doc.spans if _.fact}
    return (list(names_dict.keys()))

def createWordCloud(words):
    text = ''
    for word in words.keys():
        text +=  (word + ' ') * words[word]
    wordcloud = WordCloud(width=3000,
                          height=3000,
                          random_state=1,
                          background_color='black',
                          margin=20,
                          colormap='Pastel1',
                          collocations=False).generate(text)

    wordcloud.to_file('words_cloud.png')

articles = parse()

facts = {}
names = []
for elem in articles
    elem.__class__ = Article
    factText = elem.getText()
    docFact = prepareData(factText)
    listFacts = exstractFacts(docFact)
    for fact in listFacts:
        if fact not in facts:
            facts[fact] = 1
        else:
            facts[fact] = facts[fact] + 1
    names += extractNames(docName)


print("Список слов-фактов и их количество:")
print(facts)
createWordCloud(facts)
