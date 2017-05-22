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


def create_microportrait_set(inputdir, outputdir, classification_file = None):

    classification_dict = {}
    if not classification_file is None:
        classification_dict = create_classification_dict(classification_file)


    for f in os.listdir(inputdir):
        microportrait_dict = create_microportrait_dict(inputdir + f, classification_dict)
        for k, v in microportrait_dict.items():
            myoutfile = open(outputdir + k.split('/')[-1], 'w')
            for description in v:
                myoutfile.write(description + '\n')
            myoutfile.close()





def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 3:
        print('Usage: python create_microportrait_set.py inputdir/ outputdir/ (classification)')
    elif len(argv) < 4:
        create_microportrait_set(argv[1], argv[2])
    else:
        create_microportrait_set(argv[1], argv[2], argv[3])




if __name__ == '__main__':
    main()






