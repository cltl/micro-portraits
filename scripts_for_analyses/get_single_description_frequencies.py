import sys
import os
import csv
from collections import defaultdict


relation_translator = {'undergoer':'ondergaat','agent':'doet','label':'is','property':'is','recepient':'krijgt'}
other_roles = set()

def translate_relation(relation, f):

    global relation_translator, other_roles
    
    if relation in relation_translator:
        relation = relation_translator.get(relation)
    elif not 'rol' in relation:
        print(f, relation)
    else:
        other_roles.add(relation)

    return relation

def create_descrfreq_dict(inputdir):

    descrFreq = defaultdict(int)
    
    for f in os.listdir(inputdir):
        with open(inputdir + f) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                if not row['pos'] == 'punct':
                    relation = row['relation']
                    relation = translate_relation(relation, f)
                    description = relation + ' ' + row['description']
                    descrFreq[description] += 1

    return descrFreq


def get_description_freqs(inputdir, outputfile):

    descFreq = create_descrfreq_dict(inputdir)
    output = open(outputfile, 'wb')
    csvwriter = csv.writer(output, delimiter=';')
    csvwriter.writerow(['number','description','count'])
    counter = 0
    for description in sorted(descFreq, key=descFreq.get, reverse=True):
        counter += 1
        row = [str(counter),description,str(descFreq[description])]
        csvwriter.writerow(row)
    output.close()

    global other_roles
    print(other_roles)


def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 3:
        print('Usage: python get_single_description_frequencies.py microportraitdir/ outfile.csv')
    else:
        get_description_freqs(argv[1], argv[2])

if __name__ == '__main__':
    main()
