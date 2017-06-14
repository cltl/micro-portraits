import sys
import csv



def extract_cats(inputfile):

    my_cats = set()
    with open(inputfile, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        for row in csvreader:
            if row[0] != '':
                my_cats.add(row[0])

    for cat in my_cats:
        print(cat)




def main():

    argv = sys.argv

    if len(argv) < 2:
        print('Usage: python extract_annotated_categories.py inputfile')
    else:
        extract_cats(argv[1])

if __name__ == '__main__':
    main()
