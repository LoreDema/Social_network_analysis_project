__authors__ = 'Lorenzo De Mattei, Andrea Meini, Vincenzo Rizza'
__license__ = "GPL"
__email__ = 'lorenzo.demattei@gmail.com, ndrmeini@gmail.com, vincenzorizza6@gmail.com'

import music_analysis as ma
import numpy as np
import operator
import networkx as nx
import itertools
import matplotlib.pyplot as plt


def get_vector(listening):
    users_vectors = {}
    genres = {}
    for user in listening:
        users_vectors[user] = []
        for listen in listening[user]:
            for genre in listen[2]:
                if not (genre in genres):
                    genres[genre] = None

    for genre in genres:
        for user in listening:
            freq = 0
            for listen in listening[user]:
                if genre in listen[2]:
                    freq += listen[2][genre]
            users_vectors[user].append(freq)

    for user in users_vectors:
        users_vectors[user] = np.array(users_vectors[user])

    return users_vectors


def distance(users_vectors, net):
    distances = {}
    # for user in itertools.combinations(users_vectors, 2):
    for user in nx.edges(net):
        try:
            distances[(user[0], user[1])] = np.linalg.norm(users_vectors[user[0]] - users_vectors[user[1]])
        except KeyError:
            continue
    return sorted(distances.items(), key=operator.itemgetter(1))


def graph_stats(distance_couple, net):
    distances = []
    common_neighbors = []
    jaccard = []
    adamic = []
    for couple in distance_couple:
        distances.append(couple[1])
        common_neighbors.append(len(list(nx.common_neighbors(net, couple[0][0], couple[0][1]))))
        jaccard.append(list(nx.jaccard_coefficient(net, [(couple[0][0], couple[0][1])]))[0][2])
        adamic.append(list(nx.adamic_adar_index(net, [(couple[0][0], couple[0][1])]))[0][2])

    r_dist = 10.0/max(distances)
    r_n = 10.0/max(common_neighbors)
    r_j = 10.0/max(jaccard)
    r_a = 10.0/max(adamic)

    distances = [j * r_dist for j in distances]
    common_neighbors = [j * r_n for j in common_neighbors]
    jaccard = [j * r_j for j in jaccard]
    adamic = [j * r_a for j in adamic]

    plt.loglog(distances, color='r', label='distances')
    plt.loglog(common_neighbors, color='g', label='common_neighbors')
    plt.loglog(jaccard, color='b', label='jaccard')
    plt.loglog(adamic, color='y', label='adamic')
    plt.legend()
    plt.savefig('node_similarity/stats1.png', format='png')
    plt.close()


def edge_removing(distance_couple, net):
    clustering_coefficients = [nx.average_clustering(net)]
    components = [len(list(nx.connected_components(net)))]

    for i in range(100):
        net.remove_edge(distance_couple[i][0][0], distance_couple[i][0][1])
        clustering_coefficients.append(nx.average_clustering(net))
        components.append(len(list(nx.connected_components(net))))

    plt.plot(clustering_coefficients, color='r')
    plt.savefig('node_similarity/clustering_coeff.png', format='png')
    plt.close()

    plt.plot(components, color='r')
    plt.savefig('node_similarity/components.png', format='png')
    plt.close()

    for i in range(100):
        net.remove_edge(distance_couple[len(distance_couple) - 1 - i][0][0],
                        distance_couple[len(distance_couple) - 1 - i][0][1])
        clustering_coefficients.append(nx.average_clustering(net))
        components.append(len(list(nx.connected_components(net))))

    plt.plot(clustering_coefficients, color='r')
    plt.savefig('node_similarity/clustering_coeff_rev.png', format='png')
    plt.close()

    plt.plot(components, color='r')
    plt.savefig('node_similarity/components_rev.png', format='png')
    plt.close()


def main():
    # reads from file and building the LastFm network
    artists, net = ma.read_data()
    listening = ma.get_node_listening(artists)

    users_vectors = get_vector(listening)
    distance_couple = distance(users_vectors, net)
    # graph_stats(distance_couple, net)
    edge_removing(distance_couple, net)

if __name__ == '__main__':
    main()