import os
import sys
import csv
from collections import defaultdict

def create_cooc_dict(inputdir):

    cooc_dict = defaultdict(dict)
    freq_dict = defaultdict(int)
    
    for f in os.listdir(inputdir):
        descriptions = open(inputdir + f).readlines()
        for description in descriptions:
            freq_dict[description] += 1
            foundSelf = False
            mycounts = cooc_dict.get(description)
            if mycounts is None:
                mycounts = defaultdict(int)
                cooc_dict[description] = mycounts
            for desc2 in descriptions:
                if desc2 == description and not foundSelf:
                    foundSelf = True
                else:
                    mycounts[desc2] += 1
    return cooc_dict, freq_dict

def get_rel_cooc_freqs(inputdir, outpufile):

    cooc_dict, freq_dict = create_cooc_dict(inputdir)
    
    #total descriptions is sum of count values; needed to calculate prob; hence float
    total_size = float(sum(freq_dict.values()))

    myout = open(outpufile, 'wb')
    csvwriter = csv.writer(myout, delimiter=';')
    csvwriter.writerow(['word pair', 'cooccurrence count', 'cooc. prob', 'prob w1', 'prob w2', 'pmi'])
    covered = []
    for description, coocs in cooc_dict.items():
        p_desc = float(freq_dict.get(description))/total_size
        for label, count in coocs.items():
            setname = description + '-' + label
            if not setname in covered:
                p_label = float(freq_dict.get(label))/total_size
                p_descAndLabel = float(count)/total_size
                pmi = p_descAndLabel/(p_desc * p_label)
                csvwriter.writerow([setname, count, p_descAndLabel, p_desc, p_label, pmi])
                covered.append(label + '-' + description)
    myout.close()
    

def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(sys.argv) < 3:
        print('Usage: python get_relative_cooccurrence_frequencies.py indir/ outputfile.csv')
    else:
        get_rel_cooc_freqs(argv[1], argv[2])

if __name__ == '__main__':
    main()
