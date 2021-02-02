import requests
import string
import bs4
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt # Set up matplotlib for WSL2 using https://stackoverflow.com/questions/43397162/show-matplotlib-plots-and-other-gui-in-ubuntu-wsl1-wsl2
from wordcloud import WordCloud, STOPWORDS


URLS = [
    'https://en.wikipedia.org/wiki/Hot_Rod_(2007_film)',
    'https://en.wikipedia.org/wiki/The_Emperor%27s_New_Groove',
    'https://en.wikipedia.org/wiki/March_of_the_Penguins',
    'https://en.wikipedia.org/wiki/Jay-Z',
    'https://en.wikipedia.org/wiki/Glacier'
]


def get_words_from_soup(soup, elem_type):
    elems = [element.text for element in soup.find_all(elem_type)]
    all_text = ' '.join(elems)
    punctuation_chars = set(string.punctuation)
    all_text = ''.join(char for char in all_text if char not in punctuation_chars)
    all_text = all_text.lower()
    words = all_text.split(' ')
    return words


def get_text_from_url(url):
    page = requests.get(url)
    page.raise_for_status()
    soup = bs4.BeautifulSoup(page.text, 'html.parser')
    p_elems = [element.text for element in soup.find_all('p')]
    all_text = ' '.join(p_elems)
    titles = get_words_from_soup(soup, 'h1')
    return all_text, titles


def make_wordcloud(text, stopwords):
    wc = WordCloud(
        min_word_length=4,
        stopwords=stopwords
    ).generate(text)
    return wc


def make_wordcloud_from_url(url):
    text, titles = get_text_from_url(url)
    print(titles)
    stopwords = set(titles) | STOPWORDS
    return make_wordcloud(text=text, stopwords=stopwords)



def display_wordcloud(wc):
    plt.figure()
    plt.title('Guess the topic.')
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')


def save_wordcloud(file_name):
    plt.savefig(file_name)
    plt.close()


def main():
    for i, url in enumerate(URLS):
        wordcloud = make_wordcloud_from_url(url)
        display_wordcloud(wordcloud)
        save_wordcloud(file_name=f'img/{i}.png')
    return 0


if __name__ == "__main__":
    main()
