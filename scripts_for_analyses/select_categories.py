import sys
import csv




def select_categories(inputfile, outputprefix):

    mosout = open(outputprefix + '-moslim.csv', 'w')
    moscsvwriter = csv.writer(mosout, delimiter=';')
    moscsvwriter.writerow(['number','description_pair','category reason','joint freq','freq d1','freq d2','pmi'])
    nmosout = open(outputprefix + '-nietmoslim.csv', 'w')
    nietmoswriter = csv.writer(nmosout, delimiter=';')
    nietmoswriter.writerow(['number','description_pair','category reason','joint freq','freq d1','freq d2','pmi'])

    with open(inputfile, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        for row in csvreader:
            category = row[2]
            if 'nietmosl' in category:
                nietmoswriter.writerow(row)
            if 'moslim' in category:
                moscsvwriter.writerow(row)



def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 3:
        print('Usage: python select_categories.py input.csv outputprefix')

    else:
        select_categories(argv[1], argv[2])

if __name__ == '__main__':
    main()
