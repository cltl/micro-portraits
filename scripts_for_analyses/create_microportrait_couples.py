import sys
import os
import csv
from collections import defaultdict


relation_translator = {'undergoer':'ondergaat','agent':'doet','label':'is','property':'is','recepient':'krijgt'}
other_roles = set()

def create_classification_dict(classification_file):

    class_dict = {}

    with open(classification_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            class_dict[row['lemma']] = class_dict[row['label']]

    return class_dict

def translate_relation(relation):
    
    global relation_translator, other_roles
    
    if relation in relation_translator:
        relation = relation_translator.get(relation)
    else:
        other_roles.add(relation)
    
    return relation



def create_microportrait_dict(inputfile, classification_dict):

    portrait_dict = defaultdict(list)
    with open(inputfile) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            relation = row['relation']
            relation = translate_relation(relation)
            description = row['description']
            if description in classification_dict:
                description = classification_dict.get(description)
            full_description = relation + ' ' + description
            portrait_dict[row['identifier']].append(full_description)

    return portrait_dict

def get_pairs(description_list):

    description_pairs = set()
    for description in description_list:
        for desc2 in description_list:
            if not desc2 == description:
                mycouple = [description, desc2]
                pair = '+++'.join(sorted(mycouple))
                description_pairs.add(pair)
    return description_pairs


def create_microportrait_set(inputdir, outputfile, classification_file = None):

    classification_dict = {}
    if not classification_file is None:
        classification_dict = create_classification_dict(classification_file)

    myout = open(outputfile, 'w')
    for f in os.listdir(inputdir):
        microportrait_dict = create_microportrait_dict(inputdir + f, classification_dict)
        for v in microportrait_dict.values():
            description_pairs = get_pairs(v)
            for pair in description_pairs:
                myout.write(pair + '\n')
    myout.close()





def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 3:
        print('Usage: python create_microportrait_set.py inputdir/ outputfile/ (classification)')
    elif len(argv) < 4:
        create_microportrait_set(argv[1], argv[2])
    else:
        create_microportrait_set(argv[1], argv[2], argv[3])




if __name__ == '__main__':
    main()






