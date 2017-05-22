import sys
import csv
from collections import defaultdict


def create_word2lemma_dict(word2lemmas):

    w2l_dict = {}
    for line in open(word2lemmas, 'r'):
        parts = line.rstrip().split(';')
        w2l_dict[parts[0]] = parts[1:]

    return w2l_dict




def convert_surface_to_lemmas(word2lemmas, classificationfile, outputfile):

    w2l_dict = create_word2lemma_dict(word2lemmas)

    with open(classificationfile, 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=';')
        new_vals_dict = defaultdict(list)
        for row in csvreader:
            for fn in csvreader.fieldnames:
                if row[fn] in w2l_dict:
                    new_vals_dict[fn] += w2l_dict.get(row[fn])
                elif len(row[fn]) > 0:
                    new_vals_dict[fn].append(row[fn])


    myout = open(outputfile, 'w')
    csvout = csv.writer(myout, delimiter=';')
    for k, v in new_vals_dict.items():
        v.insert(0, k)
        csvout.writerow(v)



def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 4:
        print('Usage: python get_lemma_variant_of_classification.py word2lemmas.csv class.csv output.csv')
    else:
        convert_surface_to_lemmas(argv[1], argv[2], argv[3])

if __name__ == '__main__':
    main()
