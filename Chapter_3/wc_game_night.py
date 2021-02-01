import requests
import bs4
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt # Set up matplotlib for WSL2 using https://stackoverflow.com/questions/43397162/show-matplotlib-plots-and-other-gui-in-ubuntu-wsl1-wsl2
from wordcloud import WordCloud, STOPWORDS


FILM_URLS = [
    'https://en.wikipedia.org/wiki/Hot_Rod_(2007_film)',
    'https://en.wikipedia.org/wiki/The_Emperor%27s_New_Groove',
    'https://en.wikipedia.org/wiki/March_of_the_Penguins',
    'https://en.wikipedia.org/wiki/Jay-Z'
]


def get_text_from_url(url):
    page = requests.get(url)
    page.raise_for_status()
    soup = bs4.BeautifulSoup(page.text, 'html.parser')
    p_elems = [element.text for element in soup.find_all('p')]
    all_text = ' '.join(p_elems)
    return all_text


def make_wordcloud(text):
    wc = WordCloud(
        min_word_length=4,
        stopwords=STOPWORDS
    ).generate(text)
    return wc


def display_wordcloud(wc):
    plt.figure()
    plt.title('What movie is this?')
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.show()


def main():
    texts = [get_text_from_url(url) for url in FILM_URLS]
    wordclouds = [make_wordcloud(text) for text in texts]
    for i, wordcloud in enumerate(wordclouds):
        plt.figure()
        plt.title('What movie is this?')
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()
    return 0


if __name__ == "__main__":
    main()
