__author__ = 'Lorenzo De Mattei, Andrea Meini, Vincenzo Rizza'
__license__ = "GPL"
__email__ = 'lorenzo.demattei@gmail.com, ndrmeini@gmail.com, vincenzorizza6@gmail.com'

import networkx as nx
import codecs
import operator
import math


class ArtistInfo:
    def __init__(self, hotness):
        self.terms = {}
        self.hotness = float(hotness)

    def insert_genres(self, terms):
        tot = 0
        for i in terms:
            tot += float(terms[i][1])
        for i in terms:
            terms[i] = float(terms[i][1]) / tot
        self.terms = terms


def average_medium_hotness(artists, k):
    genres = {}
    for artist in artists:
        for genre in artists[artist].terms:
            if genre not in genres:
                genres[genre] = ([(artists[artist].hotness, artists[artist].terms[genre])], 1)
            else:
                freq = genres[genre][1] + 1
                genres[genre] = (genres[genre][0], freq)
                genres[genre][0].append((artists[artist].hotness, artists[artist].terms[genre]))
    avg_ht_freq_ratio = 0
    for genre in genres:
        tot = 0
        for i in genres[genre][0]:
            tot += i[1]
        avg_ht = 0
        for i in genres[genre][0]:
            avg_ht += i[0]*(i[1]/tot)
        avg_ht_freq_ratio += avg_ht / genres[genre][1]
    avg_ht_freq_ratio /= len(genres)
    c = 1 / avg_ht_freq_ratio * k
    print c
    for genre in genres:
        tot = 0
        for i in genres[genre][0]:
            tot += i[1]
        avg_ht = 0
        for i in genres[genre][0]:
            avg_ht += i[0]*(i[1]/tot)
        genres[genre] = math.log(avg_ht * c + genres[genre][1])

    return genres


def main():
    # reads from file and building the LastFm network
    net = nx.Graph()
    with codecs.open('data/network_cleaned.csv', 'r', 'utf-8') as fp:
        for line in fp:
            line = line.strip().split(',')
            net.add_edge(line[0], line[1])

    # reads data from file and building the artists dictionary
    artists = {}
    info = []
    with codecs.open('data/hotttness.csv', 'r', 'utf-8') as fp:
        next(fp)
        for line in fp:
            line = line.strip().split(',')
            info.append(ArtistInfo(line[1]))
            artists[line[0]] = info[-1]

    # reads data from file and add genres information
    artist = None
    terms = []
    with codecs.open('data/genres.csv', 'r', 'utf-8') as fp:
        next(fp)
        for line in fp:
            line = line.strip().split(',')
            if (artist == line[0]) or (artist is None):
                terms.append((line[1], line[2], line[3]))
            else:
                genres = {}
                for i in terms:
                    genres[i[0]] = (i[1], i[2])
                artists[artist].insert_genres(genres)
                del terms[:]
                terms.append((line[1], line[2], line[3]))
            artist = line[0]

    avg_htn = average_medium_hotness(artists, 10)
    avg_htn = sorted(avg_htn.items(), key=operator.itemgetter(1))

    artist_sort = {}
    for i in artists:
        artist_sort[i] = artists[i].hotness

    artist_sort = sorted(artist_sort.items(), key=operator.itemgetter(1))
    print artist_sort

if __name__ == '__main__':
    main()