__authors__ = 'Lorenzo De Mattei, Andrea Meini, Vincenzo Rizza'
__license__ = "GPL"
__email__ = 'lorenzo.demattei@gmail.com, ndrmeini@gmail.com, vincenzorizza6@gmail.com'

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import music_analysis as ma
import operator


def print_vectors(artists):
    genres = []
    for artist in artists:
        for genre in artists[artist].terms:
            if not(genre in genres):
                genres.append(genre)
    artist_vectors = {}
    for artist in artists:
        artist_vectors[artist] = []
        for genre in genres:
            if not(genre in artists[artist].terms):
                artist_vectors[artist].append(0)
            else:
                artist_vectors[artist].append(artists[artist].terms[genre])
    out_file = open('data/artists_vector.csv', 'w+')
    for artist in artist_vectors:
        out_file.write(artist.encode('utf-8'))
        for i in artist_vectors[artist]:
            out_file.write(',' + unicode(i))
        out_file.write('\n')
    out_file.close()
    genres_vectors = {}
    for genre in genres:
        genres_vectors[genre] = []
        for artist in artists:
            if not(genre in artists[artist].terms):
                genres_vectors[genre].append(0)
            else:
                genres_vectors[genre].append(artists[artist].terms[genre])
    out_file = open('data/genres_vector.csv', 'w+')
    for genre in genres_vectors:
        out_file.write(genre.encode('utf-8'))
        for i in genres_vectors[genre]:
            out_file.write(',' + unicode(i))
        out_file.write('\n')
    out_file.close()


def community_statistics(communities, output_file):
    out_file = open('community/' + output_file + '.txt', 'w+')
    out_file.write('Number of communities: ' + str(len(communities)) + '\n')
    average_density = 0
    node_distribution = []
    for community in communities:
        average_density += len(community)
        node_distribution.append(len(community))
    average_density /= float(len(communities))
    out_file.write('Average density: ' + str(average_density) + '\n')
    out_file.write('Density standard deviation: ' + str(np.std(node_distribution, axis=0)) + '\n')
    out_file.close()

    node_distribution.sort()
    plt.plot(node_distribution, color='r')
    plt.ylabel('number of nodes')
    plt.savefig('community/' + output_file + '_distribution.png', format='png')
    plt.close()

    plt.boxplot(node_distribution)
    plt.savefig('community/' + output_file + '_boxplot.png', format='png')
    plt.close()


def community_listening(communities, listening, artists, output_file):
    artists_distribution = {}
    genres_distribution = dict()

    # initialize total distribution to 0 for each artist
    artists_distribution['total'] = {}
    genres_distribution['total'] = {}
    for artist in artists:
        artists_distribution['total'][artist] = 0
    # initialize total distribution to 0 foreach genres
    for user in listening:
        for listen in listening[user]:
            for genre in listen[2]:
                genres_distribution['total'][genre] = 0

    # compute total distribution
    for user in listening:
        for listen in listening[user]:
            artists_distribution['total'][listen[0]] += 1 / float(len(listening) * len(listening[user]))
            for genre in listen[2]:
                genres_distribution['total'][genre] += \
                    listen[2][genre] / float(len(listening) * len(listening[user]))

    # count the users that have at least 100 listening for each community
    count = {}
    for i, c in enumerate(communities):
        count['c' + str(i)] = 0
        for user in c:
            if user in listening:
                if ('c' + str(i)) in count:
                    count['c' + str(i)] += 1

    # initialize communities distributions to 0 for each artist
    for i, c in enumerate(communities):
        # keep only the communities that have at least
        # 10 users with at least 100 listening
        if count['c' + str(i)] > 10:
            artists_distribution['c' + str(i)] = {}
            genres_distribution['c' + str(i)] = {}
            for artist in artists:
                artists_distribution['c' + str(i)][artist] = 0
            for user in listening:
                for listen in listening[user]:
                    for genre in listen[2]:
                        genres_distribution['c' + str(i)][genre] = 0

    # compute the distributions foreach community
    for i, c in enumerate(communities):
        # keep only the communities that have at least
        # 10 users with at least 100 listening
        if count['c' + str(i)] > 10:
            for user in c:
                try:
                    for listen in listening[user]:
                        artists_distribution['c' + str(i)][listen[0]] +=\
                            1 / float(count['c' + str(i)] * len(listening[user]))
                        for genre in listen[2]:
                            genres_distribution['c' + str(i)][genre] += \
                                listen[2][genre] / float(count['c' + str(i)] * len(listening[user]))
                # handling the users that are not in listening list
                # cause they have less than 100 listening
                except KeyError:
                    pass

    # compute euclidean mean distances between total
    # and communities distributions for artists and genre vectors
    artist_vectors = {}
    genre_vectors = {}
    for c in artists_distribution:
        artist_vectors[c] = []
        genre_vectors[c] = []
        for artist in artists_distribution['total']:
            artist_vectors[c].append(artists_distribution[c][artist])
        artist_vectors[c] = np.array(artist_vectors[c])
        for genre in genres_distribution['total']:
            genre_vectors[c].append(genres_distribution[c][genre])
        genre_vectors[c] = np.array(genre_vectors[c])
    distances_artist = {}
    for c in artists_distribution:
        if c != 'total':
            distances_artist[c] = np.linalg.norm(artist_vectors['total']-artist_vectors[c])
    distances_genre = {}
    for c in genres_distribution:
        if c != 'total':
            distances_genre[c] = np.linalg.norm(genre_vectors['total']-genre_vectors[c])

    # printing distances
    out_file = open('community/' + output_file + '_artist_euclidean_distances.txt', 'w+')
    for c in distances_artist:
        out_file.write(c + ' ' + str(distances_artist[c]) + '\n')
    out_file.close()
    out_file = open('community/' + output_file + '_genre_euclidean_distances.txt', 'w+')
    for c in distances_genre:
        out_file.write(c + ' ' + str(distances_genre[c]) + '\n')
    out_file.close()

    total_artist_sorted = sorted(artists_distribution['total'].items(), key=operator.itemgetter(1))
    total_genre_sorted = sorted(genres_distribution['total'].items(), key=operator.itemgetter(1))
    diff_artist = {}
    for c in artists_distribution:
        if c != 'total':
            diff_artist[c] = {}
            for artist in total_artist_sorted:
                diff_artist[c][artist] = artists_distribution[c][artist[0]] - artist[1]
    diff_genre = {}
    for c in genres_distribution:
        if c != 'total':
            diff_genre[c] = {}
            for genre in total_genre_sorted:
                diff_genre[c][genre] = genres_distribution[c][genre[0]] - genre[1]

    # print top 10 relevant artist foreach community
    out_file = open('community/' + output_file + '_top10_relevant_artist.txt', 'w+')
    for c in diff_artist:
        out_file.write(c.encode('utf-8') + '\n')
        diff_sorted = sorted(diff_artist[c].items(), key=operator.itemgetter(1), reverse=True)
        for i in range(10):
            out_file.write(str(i + 1) + '\t' + diff_sorted[i][0][0].encode('utf-8')
                           + '\t' + str(diff_sorted[i][0][1])
                           + '\t' + str(diff_sorted[i][1]) + '\n')
        out_file.write('\n')
    out_file.close()

    # print top 10 relevant genre foreach community
    out_file = open('community/' + output_file + '_top10_relevant_genre.txt', 'w+')
    for c in diff_genre:
        out_file.write(c.encode('utf-8') + '\n')
        diff_sorted = sorted(diff_genre[c].items(), key=operator.itemgetter(1), reverse=True)
        for i in range(10):
            out_file.write(str(i + 1) + '\t' + diff_sorted[i][0][0].encode('utf-8')
                           + '\t' + str(diff_sorted[i][0][1])
                           + '\t' + str(diff_sorted[i][1]) + '\n')
        out_file.write('\n')
    out_file.close()


def main():
    # reads from file and building the LastFm network
    artists, net = ma.read_data()
    listening = ma.get_node_listening(artists)
    print_vectors(artists)
    communities = list(nx.k_clique_communities(net, 5))
    community_statistics(communities, 'k-clique')

    community_listening(communities, listening, artists, 'k-clique')


if __name__ == '__main__':
    main()
