__authors__ = 'Lorenzo De Mattei, Andrea Meini, Vincenzo Rizza'
__license__ = "GPL"
__email__ = 'lorenzo.demattei@gmail.com, ndrmeini@gmail.com, vincenzorizza6@gmail.com'
import codecs
import datetime
from datetime import datetime
import sys
import networkx as nx
import matplotlib.pyplot as plt
import artist_listening as local
import graphviz as gv


def build_tree(list, threshold):
    net = nx.DiGraph()

    # Assign the root to a new list
    newlist = [list[0]]

    # From root cycle over list (second cycle)
    # If the time between root listening and the node is < threshold...
    # ... create a net edge and add the node to newList
    # If the root has at least one child -> newList increased...
    # ... and the first cycle continue with a new root

    first = list[0][1]
    c = 0
    for root in newlist:
        j = 0
        for i in range(1, len(list)):
            if (list[i] != root) and (list[i] not in newlist):
                time_diff = (list[i][0] - root[0]).total_seconds()
                if time_diff < threshold:
                    print root[1] + ' - ' + list[i][1]
                    j += 1
                    newlist.append(list[i])
                    net.add_edge(root[1], list[i][1], weight=time_diff)

    return net, first


def max_sublist(list, threshold):
    # Assign the root to a new list
    newlist = [list[0]]
    total_list = []
    i = 1
    max = newlist
    while i < len(list):
        if (list[i][0] - list[i-1][0]).total_seconds() < threshold:
            newlist.append(list[i])
        else:
            if len(newlist) > len(max):
                max = newlist
            total_list.append(newlist)
            newlist = [list[i]]
        i += 1
    # Check last newlist created
    total_list.append(newlist)
    if len(newlist) > len(max):
                max = newlist
    return max


def unicode_to_date(date_posted):
    return datetime.strptime(date_posted, '%Y-%m-%d %H:%M:%S')


def read_list(artist):
    list = []
    with codecs.open('listening_analysis/local_diffusion/listening_' + artist + '.csv', 'r', 'utf-8') as fp:
        for line in fp:
            line = line.strip().split(',')
            list.append([unicode_to_date(line[2]), line[1], (line[0])])
    return list


def main(artist, days):
    one_day = 86400
    days_threshold = one_day * int(days)
    # listeners_list = local.get_listeners(artist)
    listeners_list = read_list(artist)
    max = max_sublist(listeners_list, days_threshold)
    net, root = build_tree(max, days_threshold)

    # Calculate width of first level of graph
    width_first_level = len(net.neighbors(root))
    print width_first_level

    # Calculate number of nodes == length of list
    print net.order()   # len(max)

    # print list(net.edges_iter(data=True))
    # ts = nx.topological_sort(net)
    # print ts
    pos = nx.spring_layout(net)  # positions for all nodes
    '''
    # nodes
    nx.draw_networkx_nodes(net, pos, node_size=700)
    # edges
    nx.draw_networkx_edges(net, pos, width=6)
    # labels
    nx.draw_networkx_labels(net, pos, font_size=20, font_family='sans-serif')
    plt.axis('off')
    '''

    g = gv.Digraph(format='png')
    for node in nx.nodes(net):
        g.node(node)
    for edge in nx.edges(net):
        x = round(net.get_edge_data(*edge)['weight']/3600, 1)
        g.edge(edge[0], edge[1], label=str(x))

    g.render('listening_analysis/local_diffusion/local_diffusion_' + str(days) + '_' + artist.replace(' ', '_'))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
