__author__ = 'Lorenzo De Mattei, Andrea Meini, Vincenzo Rizza'
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

    count = 0
    precedent = ''
    out = codecs.open('data/cleaned_listenings100.csv', 'w+', 'utf-8')
    lines = []
    with codecs.open('data/cleaned_listenings.csv', 'r', 'utf-8') as fp:
        fp.next()
        for line in fp:
            user = line.strip().split(',')[0]
            if (user != precedent) and (count != 0):
                if count >= 100:
                    for i in lines:
                        out.write(i)
                del lines[:]
            count += 1
            precedent = user
            lines.append(line)
    out.close()

if __name__ == '__main__':
    main()