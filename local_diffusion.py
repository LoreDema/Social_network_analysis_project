__authors__ = 'Lorenzo De Mattei, Andrea Meini, Vincenzo Rizza'
__license__ = "GPL"
__email__ = 'lorenzo.demattei@gmail.com, ndrmeini@gmail.com, vincenzorizza6@gmail.com'

import networkx as nx
import codecs
import datetime
from datetime import datetime
import itertools
import matplotlib.pyplot as plt
import music_analysis as ma_func
import operator
from operator import itemgetter
import sys
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
    tmp = []
    net = nx.DiGraph()

    '''

    # Exclude multiple listening of same user
    for item in list:
        if item[1] not in added:
            added.append(item[1])
            tmp.append(item)

    # Sort list obtained by data time
    list = tmp
    list = sorted(list, key=itemgetter(0))
    for user in list:
        print user[0], " - ", user[1]

    '''

    # Assign the root to a new list
    newlist = [list[0]]

    # From root cycle over list (second cycle)
    # If the time between root listening and the node is < threshold...
    # ... create a net edge and add the node to newList
    # If the root has at least one child -> newList increased...
    # ... and the first cycle continue with a new root
    for root in newlist:
        for i in range(1, len(list)):
            if (list[i] != root) and (list[i] not in newlist):
                time_diff = (list[i][0] - root[0]).total_seconds()
                if time_diff < threshold:
                    # print "Padre: ", root[1], " - ", root[0]
                    # print "Figlio: ", list[i][1]
                    # print "TIME: ", time_diff
                    newlist.append(list[i])
                    net.add_edge(root[1], list[i][1], weight=time_diff)

    # print "Final list: "
    # print newlist

    return net


def unicode_to_date(date_posted):
    return datetime.strptime(date_posted, '%Y-%m-%d %H:%M:%S')


# Return a list of listeners of one artist
# Each tuple has [played_on, username, artist]
# List is ascending sorted by played_on value
def get_listeners(artist):
    listenings = []
    with codecs.open('listening_analysis/firsts_listening.csv', 'r', 'utf-8') as fp:
        c = 1
        for line in fp:
            # print c, ", ",
            c += 1
            line = line.strip().split(',')
            try:
                if line[0] not in listenings:
                    if line[1] in artist:
                        listenings.append([unicode_to_date(line[2]), line[0], (line[1])])
                else:
                    if line[1] in artist:
                        listenings.append([unicode_to_date(line[2]), line[0], (line[1])])
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


def select_artists(artists, frequencies, n, threshold):

    # exclude artist with hotness < threshold
    new_artists = []
    for i, row in itertools.takewhile(lambda (i, val): i < len(artists), enumerate(artists)):
        if row[1].hotness < threshold:
            break
        else:
            new_artists.append(row)

    # create n subsets of artists divided by hotness
    list = []
    top = new_artists[0][1].hotness
    block = (top - threshold)/n
    j = 0

    # foreach block take the artist with maximum frequencies
    for i in range(0, n):
        list.append(new_artists[j])
        while (j < len(new_artists)) and (new_artists[j][1].hotness > top - block * (i + 1)):
            try:
                if frequencies[new_artists[j][0]] > frequencies[list[i][0]]:
                    if new_artists[j][0] != '[unknown]':
                        list[i] = new_artists[j]
            except KeyError:
                pass
            j += 1

    return list


def into_dict(list):
    my_dict = {}
    for index, item in enumerate(list):
        my_dict[item[0]] = item[1]

    return my_dict


def main():
    # reads data from files
    artists = read_data()
    users_info = ma_func.get_node_listening(artists)
    artists_frequencies = ma_func.get_artists_frequencies(users_info)

    # sort artists for hotness value
    # transform dict in list
    artists = sorted(artists.items(), key=lambda x: x[1].hotness, reverse=True)

    # Select subset of _n_ artist and excludes those with a low hotness
    # In each block of artist select who has the maximum frequency
    # selectArtists(list, list_frequencies, _n_, minimum hotness)
    subset = select_artists(artists, artists_frequencies, 5, 0.45)

    # transform subset into dictionary
    subset_dict = into_dict(subset)

    # get listeners list of an artist ordered by ascending date
    # TO-DO: ciclare su tutto subset_dict
    # TO-Do: salvare risultati in csv per grafici
    for artist in subset_dict:
        listeners_list = get_listeners(artist)

        out_file = open('listening_analysis/local_diffusion/listening_' + artist + '.csv', 'w+')
        for user in listeners_list:
            print user
            out_file.write(user[2].encode('utf-8') + "," + user[1].encode('utf-8') + "," + str(user[0]).encode('utf-8') + '\n')
        out_file.close()

        one_day = 86400
        days = 5
        days_threshold = one_day * days
        # for each listeners_list build a tree
        # where two users are connected if their listening
        # is under the days_threshold
        net = build_tree(listeners_list, days_threshold)
        ts = nx.topological_sort(net)
        print(ts)
        print list(net.edges_iter(data=True))
        # t = nx.dfs_tree(net, 0)
        # print t.edges()
        # nx.draw_networkx(net, with_labels=True)
        pos = nx.spring_layout(net)  # positions for all nodes

        # nodes
        nx.draw_networkx_nodes(net, pos, node_size=700)

        # edges
        nx.draw_networkx_edges(net, pos, width=6)

        # labels
        nx.draw_networkx_labels(net, pos, font_size=20, font_family='sans-serif')

        plt.axis('off')
        plt.savefig("listening_analysis/local_diffusion/local_diffusion_" + str(days) + "_" + artist + ".png")
        plt.show() # display

if __name__ == '__main__':
    main()