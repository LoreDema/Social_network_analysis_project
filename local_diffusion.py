__authors__ = 'Lorenzo De Mattei, Andrea Meini, Vincenzo Rizza'
__license__ = "GPL"
__email__ = 'lorenzo.demattei@gmail.com, ndrmeini@gmail.com, vincenzorizza6@gmail.com'

import networkx as nx
import codecs
import datetime
import operator
from operator import itemgetter
import sys
import itertools
from datetime import datetime
import types


class ArtistInfo:
    def __init__(self, hotness):
        self.terms = {}
        self.hotness = float(hotness)

    def __repr__(self):
        return "<Hotness: %s | Terms: %s>" % (self.hotness, self.terms)

    def __str__(self):
        return "Hotness: %s | Terms: %s" % (self.hotness, self.terms)

    def insert_genres(self, terms):
        tot = 0
        for i in terms:
            tot += float(terms[i][1])
        for i in terms:
            terms[i] = float(terms[i][1]) / tot
        self.terms = terms


def build_tree(list, threshold):
    added = []
    newlist = []
    net = nx.Graph()

    for item in list:
        if item[1] not in added:
            added.append(item[1])
            newlist.append(item)

    for i in range(1, len(newlist)):
        time_diff = (newlist[i][0] - newlist[0][0]).total_seconds()
        if time_diff < threshold:
            net.add_edge(newlist[0][1], newlist[i][1], weight=time_diff)

    return net


def unicode_to_date(date_posted):
    return datetime.strptime(date_posted, '%Y-%m-%d %H:%M:%S')


def get_listeners(artists):
    listenings = []
    with codecs.open('data/cleaned_listenings.csv', 'r', 'utf-8') as fp:
        for line in fp:
            line = line.strip().split(',')
            try:
                if line[0] not in listenings:
                    if line[2] in artists:
                        listenings.append([unicode_to_date(line[4]), line[0], (line[2])])
                else:
                    if line[2] in artists:
                        # listenings[unicode_to_date(line[4])].append(line[0], (line[2])
                        listenings.append([unicode_to_date(line[4]), line[0], (line[2])])
            # handles Index Error caused by non utf-8 characters
            except IndexError:
                continue
        new_list = sorted(listenings, key=itemgetter(0))
    return new_list


def read_data():
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

    return artists


def select_artists(artists, n, threshold):

    # exclude artist with hotness < threshold
    new_artists = []
    for i, row in itertools.takewhile(lambda (i, val): i < len(artists), enumerate(artists)):
        if row[1].hotness < threshold:
            break
        else:
            new_artists.append(row)

    # create a subset of n artist
    list = []
    block = len(new_artists)/n
    for count in range(0, len(new_artists), block):
        if n > 0:
            list.append(new_artists[count])
        n -= 1

    return list


def into_dict(list):
    my_dict = {}
    for index, item in enumerate(list):
        my_dict[item[0]] = item[1]

    return my_dict


def main():
    # reads data from files
    artists = read_data()

    # sort artists for hotness value
    # transform dict in list
    artists = sorted(artists.items(), key=lambda x: x[1].hotness, reverse=True)

    # select subset of n artist with minimum hotness
    # selectArtists(list, n, hotness)
    subset = select_artists(artists, 5, 0.30)

    # transform subset into dictionary
    subset_dict = into_dict(subset)

    # get listeners list of an artist ordered by ascending date
    # TO-DO: ciclare su tutto subset_dict
    # TO-Do: salvare risultati in csv per grafici
    listeners_list = get_listeners(subset_dict.items()[0])

    one_day = 86400
    days_threshold = one_day * 30
    # for each listeners_list build a tree
    # where two users are connected if their listening
    # is under the days_threshold
    net = build_tree(listeners_list, days_threshold)
    print list(net.edges_iter(data=True))

if __name__ == '__main__':
    main()