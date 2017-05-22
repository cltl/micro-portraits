import sys
import csv
from collections import defaultdict
from string import ascii_lowercase



def create_freq_dict(inputfile, beginletter):

    freqDict = defaultdict(int)
    myinput = open(inputfile)
    for line in myinput:
        if line.startswith(beginletter):
            freqDict[line.rstrip()] += 1
    myinput.close()
    return freqDict


def create_frequency_file_from_list(inputfile, outputfile):

    counter = 0
    myoutput = open(outputfile, 'wb')
    csvwriter = csv.writer(myoutput, delimiter=';', quotechar='"')
    csvwriter.writerow(['number','description_pair','frequency'])
    
    for letter in ascii_lowercase:
        print(letter)
        freqDict = create_freq_dict(inputfile, letter)
        for pair in sorted(freqDict, key=freqDict.get, reverse=True):
            counter += 1
            csvwriter.writerow([str(counter),pair,str(freqDict[pair])])
    myoutput.close()

def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 3:
        print('Usage: python get_pair_frequencies.py inputfile outputfile')
    else:
        create_frequency_file_from_list(argv[1], argv[2])

if __name__ == '__main__':
    main()
