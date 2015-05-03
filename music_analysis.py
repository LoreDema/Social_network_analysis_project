__authors__ = 'Lorenzo De Mattei, Andrea Meini, Vincenzo Rizza'
__license__ = "GPL"
__email__ = 'lorenzo.demattei@gmail.com, ndrmeini@gmail.com, vincenzorizza6@gmail.com'

import networkx as nx
import codecs
import operator
import math
import matplotlib.pyplot as plt


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


def chunk_list(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


def get_artists_frequencies(users_info):
    artists_frequencies = {}
    for user in users_info:
        for listen in users_info[user]:
            if listen[0] not in artists_frequencies:
                artists_frequencies[listen[0]] = 1
            else:
                artists_frequencies[listen[0]] += 1

    return artists_frequencies


def get_genre_frequencies(users_info):
    genre_frequencies = {}
    for user in users_info:
        for listen in users_info[user]:
            for genre in listen[2]:
                if genre not in genre_frequencies:
                    genre_frequencies[genre] = listen[2][genre]
                else:
                    genre_frequencies[genre] += listen[2][genre]

    return genre_frequencies


def get_node_listening(artists):
    users_listening = {}
    with codecs.open('data/cleaned_listenings.csv', 'r', 'utf-8') as fp:
        for line in fp:
            line = line.strip().split(',')
            try:
                if line[0] not in users_listening:
                    if line[2] in artists:
                        users_listening[line[0]] = [(line[2], artists[line[2]].hotness, artists[line[2]].terms)]
                else:
                    if line[2] in artists:
                        users_listening[line[0]].append((line[2], artists[line[2]].hotness, artists[line[2]].terms))
            # handles Index Error caused by non utf-8 characters
            except IndexError:
                continue
    to_delete = []
    for user in users_listening:
        if len(users_listening[user]) < 100:
            to_delete.append(user)
        else:
            users_listening[user] = users_listening[user][:100]

    for el in to_delete:
        del users_listening[el]

    return users_listening


def average_genre_hotness(artists, k):
    genres = {}
    for artist in artists:
        for genre in artists[artist].terms:
            if genre not in genres:
                genres[genre] = ([(artists[artist].hotness, artists[artist].terms[genre])],
                                 artists[artist].terms[genre])
            else:
                freq = genres[genre][1] + artists[artist].terms[genre]
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
    for genre in genres:
        tot = 0
        for i in genres[genre][0]:
            tot += i[1]
        avg_ht = 0
        for i in genres[genre][0]:
            avg_ht += i[0]*(i[1]/tot)
        genres[genre] = math.log(avg_ht * c + genres[genre][1])

    return genres


def read_data():
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

    return artists, net


def centrality_chunks(net, artists, measure):
    if measure == 'closeness':
        net_cl = nx.closeness_centrality(net)
    elif measure == 'betweness':
        net_cl = nx.betweenness_centrality(net)
    else:
        print 'Measure not valid'
        return None
    net_cl = sorted(net_cl.items(), key=operator.itemgetter(1))

    users_info = get_node_listening(artists)
    to_del = []
    for i, value in enumerate(net_cl):
        if value[0] not in users_info:
            to_del.append(i)

    net_cl[:] = [item for i, item in enumerate(net_cl) if i not in to_del]

    chunks_clc = chunk_list(net_cl, 4)
    return chunks_clc, users_info


def plot_artist_distribution(chunks, artists_frequencies, users_info, artists, measure):
    for i, chunk in enumerate(chunks):
        list_af = []
        list_ah = []
        chunk_users_info = {}
        for user in chunk:
            chunk_users_info[user[0]] = users_info[user[0]]
        list_caf = get_artists_frequencies(chunk_users_info)
        list_caf = sorted(list_caf.items(), key=operator.itemgetter(1))
        to_del = []
        for j, artist in enumerate(list_caf):
            if artists[artist[0]].hotness <= 0:
                to_del.append(j)
            list_af.append(artists_frequencies[artist[0]])
            list_ah.append(artists[artist[0]].hotness)

        list_caf[:] = [float(item[1]) for j, item in enumerate(list_caf) if j not in to_del]
        list_af[:] = [float(item) for j, item in enumerate(list_af) if j not in to_del]
        list_ah[:] = [item for j, item in enumerate(list_ah) if j not in to_del]

        r_caf = 10.0/max(list_caf)
        r_af = 10.0/max(list_af)
        r_ah = 10.0/max(list_ah)

        list_caf = [math.log(j * r_caf) for j in list_caf]
        list_af = [math.log(j * r_af) for j in list_af]
        list_ah = [math.log(j * r_ah) for j in list_ah]

        plt.plot(list_af, label='Global artist frequency', color='r')
        plt.plot(list_ah, label='Artist hotness', color='y')
        plt.plot(list_caf, label='Chunk artist frequency', color='b')
        # plt.legend()
        plt.savefig('listening_analysis/artist_chunk_' + measure + '_' + str(i + 1) + '.png', format='png')
        plt.close()


def plot_frequencies_distribution(chunks, genre_frequencies, users_info, avg_htn_genres, measure):
    for i, chunk in enumerate(chunks):
        list_gf = []
        list_gh = []
        chunk_users_info = {}
        for user in chunk:
            chunk_users_info[user[0]] = users_info[user[0]]
        list_cgf = get_genre_frequencies(chunk_users_info)
        list_cgf = sorted(list_cgf.items(), key=operator.itemgetter(1))
        to_del = []
        for j, genre in enumerate(list_cgf):
            if avg_htn_genres[genre[0]] <= 0:
                to_del.append(j)
            list_gf.append(genre_frequencies[genre[0]])
            list_gh.append(avg_htn_genres[genre[0]])

        list_cgf[:] = [float(item[1]) for j, item in enumerate(list_cgf) if j not in to_del]
        list_gf[:] = [float(item) for j, item in enumerate(list_gf) if j not in to_del]
        list_gh[:] = [item for j, item in enumerate(list_gh) if j not in to_del]

        r_caf = 10.0/max(list_cgf)
        r_gf = 10.0/max(list_gf)
        r_gh = 10.0/max(list_gh)

        list_cgf = [math.log(j * r_caf) for j in list_cgf]
        list_gf = [math.log(j * r_gf) for j in list_gf]
        list_gh = [math.log(j * r_gh) for j in list_gh]

        plt.plot(list_gf, label='Global genre frequency', color='r')
        plt.plot(list_gh, label='Genre hotness', color='y')
        plt.plot(list_cgf, label='Chunk artist frequency', color='b')
        # plt.legend()
        plt.savefig('listening_analysis/genre_chunk_' + measure + '_' + str(i + 1) + '.png', format='png')
        plt.close()


def get_key(value):
    get_hot = operator.itemgetter(1)
    return get_hot(value).hotness


def artists_chunk_genres(artists, n_chunks):

    artists = artists.items()
    artists = sorted(artists, key=get_key)

    artists_chunk = chunk_list(artists, n_chunks)

    chunk_genres_frequncies = []
    for chunk in artists_chunk:
        genre_frequencies = {}
        for artist in chunk:
            for genre in artist[1].terms:
                if genre not in genre_frequencies:
                    genre_frequencies[genre] = artist[1].terms[genre]
                else:
                    genre_frequencies[genre] += artist[1].terms[genre]
        genre_frequencies = sorted(genre_frequencies.items(), key=operator.itemgetter(1))
        chunk_genres_frequncies.append(genre_frequencies)


def print_genre_hotness(avg_htn_genres):
    out_file = open('listening_analysis/genre_hotness.csv', 'w+')
    for genre in avg_htn_genres:
        out_file.write(genre.encode('utf-8') + ',' + str(avg_htn_genres[genre]).encode('utf-8') + '\n')
    out_file.close()


def main():

    # reads data from files
    artists, net = read_data()

    artists_chunk_genres(artists, 6)

    # calculates the medium hotness for each genres
    # setting the constant k = 10
    avg_htn_genres = average_genre_hotness(artists, 10)
    print_genre_hotness(avg_htn_genres)

    # calculates and sorts the closeness centrality
    # for each node of the LastFM network
    # then chunks the node into 4 groups
    chunks_clc, users_info = centrality_chunks(net, artists, 'closeness')
    artists_frequencies = get_artists_frequencies(users_info)
    genre_frequencies = get_genre_frequencies(users_info)
    # calculates and plot chunk and global distributions
    # compared with hotness for artists and genres
    plot_artist_distribution(chunks_clc, artists_frequencies, users_info, artists, 'closeness')
    plot_frequencies_distribution(chunks_clc, genre_frequencies, users_info, avg_htn_genres, 'closeness')

    # calculates and sorts the closeness centrality
    # for each node of the LastFM network
    # then chunks the node into 4 groups
    chunks_clb, users_info = centrality_chunks(net, artists, 'betweness')
    artists_frequencies = get_artists_frequencies(users_info)
    # calculates and plot chunk and global distributions
    # compared with hotness for artists and genres
    plot_artist_distribution(chunks_clb, artists_frequencies, users_info, artists, 'betweness')
    plot_frequencies_distribution(chunks_clb, genre_frequencies, users_info, avg_htn_genres, 'betweness')

if __name__ == '__main__':
    main()