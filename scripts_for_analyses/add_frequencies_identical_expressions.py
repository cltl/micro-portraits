import sys
import csv


def add_freqs(infile, outfile):

    myoutput = open(outfile, 'w')
    csvwriter = csv.writer(myoutput, delimiter=';')

    current_string = 'description_pair'
    current_freq = 'joint freq'
    with open(infile, 'r') as csvinput:
        csvreader = csv.reader(csvinput, delimiter=';')
        for row in csvreader:
            if not row[0] == 'description_pair':
                if row[0] == current_string:
                    current_freq += float(row[1])
                else:
                    csvwriter.writerow([current_string, current_freq])
                    current_freq = float(row[1])
                    current_string = row[0]

        csvwriter.writerow([current_string, current_freq])






def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 3:
        print('Usage: python add_frequencies_identical_expressions.py inputfile outputfile')
    else:
        add_freqs(argv[1], argv[2])

if __name__ == '__main__':
    main()
