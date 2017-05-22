import sys
import csv




def get_a_cat_dict(categoryfile):

    catdict = {}
    for line in open(categoryfile, 'rb'):
        catdict['categoryinputfile'] = categoryfile
        parts = line.split(';')
        for lemma in parts[1:]:
            catdict[lemma] = parts[0]
    return catdict


def create_outcsv_dict(catdicts, outputprefix):
    
    outdict = {}

    for cdict in catdicts:
        catfile = cdict.get('categoryinputfile')
        outfile = open(outputprefix + catfile.split('/')[-1], 'w')
        outdict[catfile] = outfile
    return outdict


def get_updated_output(catdict, descriptions):

    d1 = descriptions[0]
    d2 = descriptions[1]
    for k in catdict:
        if 'is ' + k == descriptions[0]:
            d1 = 'is ' + catdict.get(k)
        if 'is ' + k == descriptions[1]:
            d2 = 'is ' + catdict.get(k)

    return d1, d2


def create_cat_csv(inputfile, outputfile, categoryfile):

    catdict = get_a_cat_dict(categoryfile)
    myoutput = open(outputfile, 'w')
    csvwriter = csv.writer(myoutput, delimiter=';')
    csvwriter.writerow(['number','description_pair','joint freq','freq d1','freq d2'])
    repl_dict = {}
   
    counter = 0
    with open(inputfile, 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=';')
        for row in csvreader:
            counter += 1
            if counter%10000000 == 0:
                print(counter)
            descriptions = row['description_pair'].split('+++')
            d1, d2 = get_updated_output(catdict, descriptions)
            if not d1 in descriptions:
                repl_dict[descriptions[0]] = [d1, row['freq d1']]
            if not d2 in descriptions:
                repl_dict[descriptions[1]] = [d2, row['freq d2']]
            updated_description = d1 + '+++' + d2
            csvwriter.writerow([row['number'], updated_description, row['joint freq'], row['freq d1'], row['freq d2']])


    replaced = open('replaced_pairs.csv', 'w')
    repwriter = csv.writer(replaced, delimiter=';')
    repwriter.writerow(['original','replacement','freq'])
    for k, v in repl_dict.items():
        v.insert(0, k)
        repwriter.writerow(v)



def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 4:
        print('python create_categorized_counts.py inputcsv outputcsv [categoryfiles]')
    else:
        create_cat_csv(argv[1], argv[2], argv[3])


if __name__ == '__main__':
    main()
