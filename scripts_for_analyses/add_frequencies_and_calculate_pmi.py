import sys
import csv
import math
from collections import defaultdict
from string import ascii_lowercase
from operator import add



def create_freq_dict(inputfile):

    freqDict = defaultdict(float)
    single_fd = defaultdict(float)
    counter = 0
    with open(inputfile, 'rb') as csvin:
        csvreader = csv.DictReader(csvin, delimiter=';')
        for row in csvreader:
            counter += 1
            if counter%10000000 == 0:
                print(counter)
        
            description_pair = row['description_pair'].split('+++')
            single_fd[description_pair[0]] += float(row['freq d1'])
            single_fd[description_pair[1]] += float(row['freq d2'])
            new_pair = (description_pair[0], description_pair[1])
            freqDict[new_pair] += float(row['joint freq'])


    return freqDict, single_fd

def calculate_pmi(total, freq1, freq2, joint_freq):
    
    prob1 = freq1/total
    prob2 = freq2/total
    joint_prob = joint_freq/total
    
    pmi = math.log(joint_prob/(prob1*prob2))
    
    return pmi


def create_updated_frequencies(inputfile, outputfile):

    myoutput = open(outputfile, 'wb')
    csvwriter = csv.writer(myoutput, delimiter=';', quotechar='"')
    csvwriter.writerow(['number','description_pair','joint freq','freq d1','freq d2','pmi'])
    
    freq_dict, single_fd = create_freq_dict(inputfile)

    pmi_dict = {}
    total_score = float(sum(single_fd.values()))
    counter = 0
    print('writing out outcome')
    for pair, joint_freq in freq_dict.items():
        counter += 1
        d1f = single_fd.get(pair[0])
        d2f = single_fd.get(pair[1])
        descriptions = pair[0] + '+++' + pair[1]
        pmi = calculate_pmi(total_score, float(d1f), float(d2f), float(joint_freq))
        csvwriter.writerow([str(counter),descriptions,str(joint_freq), str(d1f), str(d2f), str(pmi)])

def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 3:
        print('Usage: python add_frequencies_and_calculate_pmi.py inputfile outputfile')
    else:
        create_updated_frequencies(argv[1], argv[2])

if __name__ == '__main__':
    main()
