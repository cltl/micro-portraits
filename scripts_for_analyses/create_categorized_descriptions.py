import sys
import csv
from collections import defaultdict

def get_a_cat_dict(categoryfile):
    
    catdict = {}
    for line in open(categoryfile, 'rb'):
        catdict['categoryinputfile'] = categoryfile
        parts = line.split(';')
        for lemma in parts[1:]:
            catdict[lemma] = parts[0]
    return catdict


def get_updated_output(catdict, description):
    

    for k in catdict:
        if 'is ' + k == description:
            description = 'is ' + catdict.get(k)

    return description



def create_categorized_freq_dict(inputfile, catdict):

    freq_dict = defaultdict(int)
    with open(inputfile, 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=';')
        for row in csvreader:
            description = get_updated_output(catdict, row['description'])
            freq_dict[description] += int(row['count'])

    return freq_dict







def create_cat_csv(infile, outputfile, catfile):

    catdict = get_a_cat_dict(catfile)
    freq_dict = create_categorized_freq_dict(infile, catdict)
    


    myoutput = open(outputfile, 'w')
    csvwriter = csv.writer(myoutput, delimiter=';')
    csvwriter.writerow(['number','description','count'])

    counter = 0
    for description in sorted(freq_dict, key=freq_dict.get, reverse=True):
        counter += 1
        csvwriter.writerow([str(counter),description,str(freq_dict[description])])










def main(argv=None):
    
    if argv is None:
        argv = sys.argv
    
    if len(argv) < 4:
        print('python create_categorized_counts.py inputcsv outputcsv [categoryfiles]')
    else:
        create_cat_csv(argv[1], argv[2], argv[3])


if __name__ == '__main__':
    main()
