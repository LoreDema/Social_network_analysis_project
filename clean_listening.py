__authors__ = 'Lorenzo De Mattei, Andrea Meini, Vincenzo Rizza'
__license__ = "GPL"
__email__ = 'lorenzo.demattei@gmail.com, ndrmeini@gmail.com, vincenzorizza6@gmail.com'

import codecs


def main():
    precedent = ''
    out = codecs.open('data/cleaned_listenings.csv', 'w+', 'utf-8')
    with codecs.open('data/listenings.csv', 'r', 'utf-8') as fp:
        for line in fp:
            if line != precedent:
                out.write(line)
            precedent = line
    out.close()

if __name__ == '__main__':
    main()