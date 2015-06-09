__authors__ = 'Lorenzo De Mattei, Andrea Meini, Vincenzo Rizza'
__license__ = "GPL"
__email__ = 'lorenzo.demattei@gmail.com, ndrmeini@gmail.com, vincenzorizza6@gmail.com'
import local_diffusion as local
import codecs
import csv
import datetime
from datetime import datetime
import io
import operator


# Take in input the list of listening of one single user
# Return a new list containing only the first listening for each artist
def select_first_listenings(list):
    sorted_list = sorted(list, key=operator.itemgetter(1, 2))
    new_list = [sorted_list[0]]
    for i in range(1, len(sorted_list)):
        if sorted_list[i][1] != sorted_list[i-1][1]:
            new_list.append(sorted_list[i])
    return new_list


def main():
    artists = local.read_data()
    i = 0
    artist = ""
    user_listening = []
    final_listening = []
    with codecs.open('data/cleaned_listenings.csv', 'r', 'utf-8') as fp:
        next(fp)
        for line in fp:
            line = line.strip().split(',')
            try:
                if i == 0:
                    artist = line[0]
                    user_listening.append([line[0], line[2], local.unicode_to_date(line[4])])
                else:
                    if line[0] != artist:
                        final_listening.append(select_first_listenings(user_listening))
                        user_listening = [[line[0], line[2], local.unicode_to_date(line[4])]]
                        artist = line[0]
                    else:
                        user_listening.append([line[0], line[2], local.unicode_to_date(line[4])])
            # handles Index Error caused by non utf-8 characters
            except IndexError:
                continue
            i += 1

    out_file = open('listening_analysis/firsts_listening.csv', 'w+')
    for user_list in final_listening:
        for listening in user_list:
            out_file.write(listening[0].encode('utf-8') + "," + listening[1].encode('utf-8') + "," + str(listening[2]).encode('utf-8') + '\n')
    out_file.close()

if __name__ == '__main__':
    main()