__authors__ = 'Lorenzo De Mattei, Andrea Meini, Vincenzo Rizza'
__license__ = "GPL"
__email__ = 'lorenzo.demattei@gmail.com, ndrmeini@gmail.com, vincenzorizza6@gmail.com'

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import music_analysis as ma


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


def main():
    # reads from file and building the LastFm network
    artists, net = ma.read_data()
    listening = ma.get_node_listening(artists)
    communities = list(nx.k_clique_communities(net, 5))
    community_statistics(communities, 'k-clique')


if __name__ == '__main__':
    main()
