import pdfkit
from bs4 import BeautifulSoup
import urllib.request
from multiprocessing import Pool
import sys
sys.setrecursionlimit(20000)

class G4G:

    base_url = None

    def __init__(self, url):

        G4G.base_url = url

    @staticmethod
    def get_page_soup(url):

        req = urllib.request.Request(url, headers={'User-Agent': "Mozilla"})
        try:
            page = urllib.request.urlopen(req)
            return BeautifulSoup(page, 'html5lib')
        except Exception as e:
            print(url, e)
            return False

    def get_head(self):

        page = self.get_page_soup(url=self.base_url)
        html = page.new_tag('html')
        html.insert(1, page.find('head'))
        html.insert(2, page.new_tag('body'))
        html.find('link', attrs={
            'href': '//cdnjs.cloudflare.com/ajax/libs/cookieconsent2/3.0.3/cookieconsent.min.css'}).decompose()
        html.find('script', attrs={
            'src': '//cdnjs.cloudflare.com/ajax/libs/cookieconsent2/3.0.3/cookieconsent.min.js'}).decompose()
        return html

    def get_links(self):

        page = self.get_page_soup(url=self.base_url)
        article_links = [self.base_url]
        temp = page.select('article a')
        for link in temp:
            try:
                if link['href'] != self.base_url and link['href'][0] != '#' and link['href'] not in article_links:
                    article_links.append(link['href'])
                    page = self.get_page_soup(link['href'])
                    if page:
                        article = page.find_all('article')
                        if len(article) > 1:
                            articles = self.get_multiple_articles(page, link['href'], temp)
                            if articles:
                                for article in articles:
                                    article_links.append(article)
            except Exception as e:
                print(e)
                continue
        return article_links

    @staticmethod
    def safe_remove(tag, article, attrs=None):

        try:
            if attrs:
                article.find(tag, attrs=attrs).decompose()
            else:
                article.find(tag).decompose()
        except Exception:
            pass
        return article

    def get_multiple_articles(self, page, z, e_link):

        articles_links = []
        next_href = ''
        count = 0
        e_links = []
        for link in e_link:
            try:
                e_links.append(link['href'])
            except:
                continue
        while next_href is not None:
            links = page.select('article header h2 a')
            for link in links:
                if link['href'] not in e_links:
                    articles_links.append(link['href'])
            next_href = page.find('a', attrs={'class': 'nextpostslink'})
            if next_href:
                next_href = next_href['href']
                page = self.get_page_soup(next_href)
            else:
                page = None
            count += 1
            print(count, 'done')
        return articles_links

    def clean_article(self, article):

        article = self.safe_remove('div', article, attrs={'id': 'improvedBy'})
        article = self.safe_remove('div', article, attrs={'class': 'author_info_box'})
        article = self.safe_remove('div', article, attrs={'class': 'no-p-tag'})
        article = self.safe_remove('footer', article)
        return article

    def get_articles(self, link):

        print(link)
        page = self.get_page_soup(link)
        if page:
            article = page.find('article')
            article = self.clean_article(article)
            if article:
                return article
        print(link, 'done')
        return None

    def pool_articles(self, links):

        p = Pool(32)
        articles = p.map(self.get_articles, links)
        p.close()
        p.join()
        br = len(articles)//5
        for i in range(1, 6):
            html = self.get_head()
            article = articles[(i-1)*br:i*br]
            print(len(article),  i)
            for data in article:
                if data:
                    html.body.append(data)
            for script in html('script'):
                script.decompose()
            file = open(str(i)+'.html', 'w')
            file.write(str(html))
            file.close()
        # print('append done1')
        # for article in articles:
        #     if article:
        #         html.body.append(article)
        # print('append done')
        #
        # # html1 = open('python.html', 'w')
        # # html1.write(str(html))
        return 0

    @staticmethod
    def generate_pdf():

        pdfkit.from_file('java.html', 'java.pdf')


soup = G4G('https://www.geeksforgeeks.org/java/')
articles_link = soup.get_links()
for link in articles_link:
    print('link', link)
pages = soup.pool_articles(articles_link)
html = open('java.html', 'w')
html.write(str(pages))
soup.generate_pdf()
