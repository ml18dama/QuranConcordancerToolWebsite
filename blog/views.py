from django.http import HttpResponse
import datetime
from django import template
from django.shortcuts import render
from django.conf import settings
import re
import pandas as pd
import json
from wordcloud import WordCloud

currdir = 'blog/'
quran_corpus = currdir+'data/arabic-original.csv'  # Arabic quran corpus
# Arabic verses interpretation corpus
interpretation_corpus = currdir+'data/ar.jalalayn.xml'
# a concordances dataset (quran words and their concordance)
concordances_dataset_json = currdir+'data/concordances_dataset.json'
# Words dictionary (quran words)
words_dictionary_json = currdir+'data/words_dictionary.json'
# Roots dictionary (quran root words)
roots_dictionary_json = currdir+'data/roots_dictionary.json'
# unique quran words (exclude stopwords)
cleaned_corpus_text = currdir+'data/cleaned_corpus.txt'
arabic_stopwords = currdir+'data/arabic_stopwords.txt'


def main_page(request):
    top_20 = most_frequent_words()
    return render(request, 'main/index.html', {'top_20': top_20})


def result(request):
    vserses_by_word = []
    search_word = request.POST.get('word', 'This is a default value')

    vserses_by_word = word_concordance(search_word)
    count = vserses_by_word.count()

    derived_words = find_derived_words(search_word)
    verses_by_derived = root_concordance(search_word)

    top_20 = most_frequent_words()

    return render(request, 'main/index.html', {"search_word": search_word, "verses_by_word": vserses_by_word.items(), "count": count, "search_word": search_word,
                                               "derived_words": derived_words, 'top_20': top_20})

# ----------------------- Implement most frequent words function ----------------------------------------------------


def most_frequent_words():
    wordCounter = {}
    with open(cleaned_corpus_text, mode='r', encoding='utf-8') as fh:
        for line in fh.readlines():
            # spit the line into a list.
            word_list = line.split()
            for word in word_list:
                # Adding  the word into the wordCounter dictionary.
                if word not in wordCounter:
                    wordCounter[word] = 1
                else:
                    # if the word is already in the dictionary update its count.
                    wordCounter[word] = wordCounter[word] + 1

    top_10 = sorted(wordCounter.items(), reverse=True,
                    key=lambda x: x[1])[:100]
    return top_10


# def quran_word_cloud():
#     file = codecs.open(os.path.join(cleaned_corpus_text), 'r', 'utf-8')
#     mask = np.array(Image.open(os.path.join(currdir, "cloud.png")))
#     wc = WordCloud(background_color="white",
#                    mask=mask,
#                    max_words=200,
#                    stopwords=arb_stopwords,
#                    font_path='data/Shoroq-Font.ttf')
#     # Make text readable for a non-Arabic library like wordcloud
#     text = arabic_reshaper.reshape(file.read())
#     text = get_display(text)
#     # Generate a word cloud image
#     wc.generate(text)
#     # Export an image to file
#     wc.to_file(os.path.join(currdir, "CSV_wc.png"))
#     # Show an image
#     img = Image.open('data/CSV_wc.png')
#     return img


def word_concordance(word):
    verses_concordances_list = []
    aa = pd.read_csv(quran_corpus, sep='|',
                     encoding="UTF-8", usecols=['verse'])

    clean_text = aa['verse'].map(lambda x: re.sub('[ًٌٍَُِّٰۘۚۙ~ْۖۗ]', '', x))

    word_con_rows = clean_text[clean_text.str.contains(
        '|'.join(word.split(' ')))]
    rows_index = word_con_rows.index.tolist()

    #  verses concordance count
    con_count = (clean_text.str.count(word).sum())
    for i in rows_index:
        row = aa.iloc[i]
        verses_concordances_list.append(row.verse)
    df = pd.Series(verses_concordances_list)
    return df


def find_derived_words(root_word):
    with open(roots_dictionary_json,  mode='r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get(root_word, [])


def root_concordance(word):
    verses_by_derived = {}
    with open(roots_dictionary_json, mode='r', encoding='utf-8') as f:
        data = json.load(f)
    derived_list = data.get(word, [])
    for Derived_Word in derived_list:
        verses_by_derived[Derived_Word] = word_concordance(Derived_Word)

    return verses_by_derived
