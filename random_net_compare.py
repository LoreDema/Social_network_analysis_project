__authors__ = 'Lorenzo De Mattei, Andrea Meini, Vincenzo Rizza'
__license__ = "GPL"
__email__ = 'lorenzo.demattei@gmail.com, ndrmeini@gmail.com, vincenzorizza6@gmail.com'

import networkx as nx
import codecs
import matplotlib.pyplot as plt
import operator


def degree_distribution(net):
    distribution = nx.degree_histogram(net)
    for i, value in enumerate(distribution):
        distribution[i] = (float(value)/float(len(net.nodes())))

    return distribution[1:]


def main():
    # reads from file and building the LastFm network
    net = nx.Graph()
    with codecs.open('data/network_cleaned.csv', 'r', 'utf-8') as fp:
        for line in fp:
            line = line.strip().split(',')
            net.add_edge(line[0], line[1])

    # generating a random network
    random_net = nx.gnm_random_graph(len(net.nodes()), len(net.edges()))

    # calculates the degree distributions for the LastFM network
    # and for the random network, then plots the results
    distribution_net = degree_distribution(net)
    distribution_random_net = degree_distribution(random_net)
    plt.loglog(distribution_net, label='LastFM net', color='b')
    plt.loglog(distribution_random_net, label='Random net', color='r')
    plt.legend()
    plt.ylabel('frequency')
    plt.xlabel('degree')
    plt.savefig('degree_distribution.png', format='png')
    plt.close()

    # calculates the average shortest paths for the LastFM network
    # and for the random network
    net_asp = nx.average_shortest_path_length(net)
    out_file = open('average_shortest_path_length.txt', 'w+')
    out_file.write('LastFM network average shortest path: ' + str(net_asp) + '\n')
    try:
        random_net_asp = nx.average_shortest_path_length(random_net)
        out_file.write('Random network average shortest path: ' + str(random_net_asp) + '\n')
    except nx.networkx.exception.NetworkXError:
        for i, g in enumerate(nx.connected_component_subgraphs(random_net)):
            random_net_asp = nx.average_shortest_path_length(g)
            out_file.write('Random network subgraph ' + str(i + 1) + ' average shortest path: '
                           + str(random_net_asp) + '\n')
    out_file.close()

    # calculates the average clustering coefficient for the LastFM network
    # and for the random network
    out_file = open('average_cluster_coefficient.txt ', 'w+')
    net_cc = nx.average_clustering(net)
    out_file.write('LastFM network average cluster coefficient: ' + str(net_cc) + '\n')
    random_net_cc = nx.average_clustering(random_net)
    out_file.write('Random network average cluster coefficient: ' + str(random_net_cc) + '\n')
    out_file.close()

    # calculates the closeness centrality for each node of the LastFM network
    # and of the random network
    net_clc = nx.closeness_centrality(net)
    random_net_clc = nx.closeness_centrality(random_net)

    # plots the closeness centralities ordered descending for both the network
    net_clc = sorted(net_clc.items(), key=operator.itemgetter(1))
    net_clc = [i[1] for i in net_clc]

    random_net_clc = sorted(random_net_clc.items(), key=operator.itemgetter(1))
    random_net_clc = [i[1] for i in random_net_clc]

    plt.plot(net_clc, label='LastFM net', color='b')
    plt.plot(random_net_clc, label='Random net', color='r')
    plt.legend()
    plt.ylabel('centrality')
    plt.xlabel('rank')
    plt.savefig('closeness_centrality.png', format='png')
    plt.close()

    # calculates the betweenness centrality for each node of the LastFM network
    # and of the random network
    net_bc = nx.closeness_centrality(net)
    random_net_bc = nx.closeness_centrality(random_net)

    # plots the betweenness centralities ordered descending for both the network
    net_bc = sorted(net_bc.items(), key=operator.itemgetter(1))
    net_bc = [i[1] for i in net_bc]

    random_net_bc = sorted(random_net_bc.items(), key=operator.itemgetter(1))
    random_net_bc = [i[1] for i in random_net_bc]

    plt.plot(net_bc, label='LastFM net', color='b')
    plt.plot(random_net_bc, label='Random net', color='r')
    plt.legend()
    plt.ylabel('centrality')
    plt.xlabel('rank')
    plt.savefig('betweenness_centrality.png', format='png')
    plt.close()

    # calculates the page rank for each node of the LastFM network
    # and of the random network
    net_pr = nx.pagerank(net)
    if nx.is_connected(random_net):
        random_net_pr = nx.pagerank(random_net)
    else:
        random_net_pr = {}
        for g in nx.connected_component_subgraphs(random_net):
            sub_pr = nx.pagerank(g)
            random_net_pr.update(sub_pr)
    # plots the page rank ordered descending for both the network
    net_pr = sorted(net_pr.items(), key=operator.itemgetter(1))
    net_pr = [i[1] for i in net_pr]

    random_net_pr = sorted(random_net_pr.items(), key=operator.itemgetter(1))
    random_net_pr = [i[1] for i in random_net_pr]

    plt.plot(net_pr, label='LastFM net', color='b')
    plt.plot(random_net_pr, label='Random net', color='r')
    plt.legend()
    plt.ylabel('centrality')
    plt.xlabel('rank')
    plt.savefig('page_rank.png', format='png')
    plt.close()

if __name__ == '__main__':
    main()