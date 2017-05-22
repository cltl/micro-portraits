import sys
import csv
import math
from collections import defaultdict



def create_single_freq_dir(inputfile):

    descr_freq = {}
    with open(inputfile, 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        for row in csvreader:
            descr_freq[row['description']] = float(row['count'])
    return descr_freq


def calculate_ppmi(total, freq1, freq2, joint_freq):

    prob1 = freq1/total
    prob2 = freq2/total
    joint_prob = joint_freq/total

    ppmi = math.log(joint_prob/(prob1*prob2))

    return ppmi


def add_single_freqs_and_ppmi(singlefreqs, pairfreqs, outpufile):

    descr_freq = create_single_freq_dir(singlefreqs)
    total_corpus_size = sum(descr_freq.values())
    myoutput = open(outpufile, 'w')
    outcsv = csv.writer(myoutput, delimiter=';', quotechar='"')
    outcsv.writerow(['number','description_pair','joint freq','freq d1','freq d2','ppmi'])
    counter = 0
    with open(pairfreqs, 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        for row in csvreader:
            counter += 1
            if counter%10000000 == 0:
                print(counter)
            pair = row['description_pair'].split('+++')
            freq1 = descr_freq.get(pair[0])
            freq2 = descr_freq.get(pair[1])
            joint_freq = float(row['frequency'])
            if not (freq1 is None or freq2 is None):
                ppmi = calculate_ppmi(total_corpus_size, freq1, freq2, joint_freq)
                outcsv.writerow([row['number'],row['description_pair'],row['frequency'],str(freq1),str(freq2),str(ppmi)])





def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 4:
        print('Usage: python add_singular_frequencies_and_pmi.py description_freq.csv pair_freq.csv output.csv')
    else:
        add_single_freqs_and_ppmi(argv[1], argv[2], argv[3])

if __name__ == '__main__':
    main()
