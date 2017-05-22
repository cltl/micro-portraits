import sys
import csv
import math


def create_freq_dict(individualfreqs):

    freq_dict = {}
    with open(individualfreqs, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=';')
        for row in csvreader:
            freq_dict[row['description']] = float(row['count'])
                      
    return freq_dict

                      
def calculate_pmi(total, freq1, freq2, joint_freq):
                      
    prob1 = freq1/total
    prob2 = freq2/total
    joint_prob = joint_freq/total
                      
    pmi = math.log(joint_prob/(prob1*prob2))
                      
    return pmi


def add_ifreq_pmi(inputfile, individualfreqs, outputfile):

    freq_dict = create_freq_dict(individualfreqs)
    myoutput = open(outputfile, 'w')
    csvwriter = csv.writer(myoutput, delimiter=';')
    csvwriter.writerow(['description_pair','joint freq', 'freq d1', 'freq d2', 'pmi'])
                      
    total_freq = sum(freq_dict.values())
    with open(inputfile, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=';')
        for row in csvreader:
            descriptions = row['description_pair'].split('+++')
            jointfreq = float(row['joint freq'])
            freqd1 = freq_dict.get(descriptions[0])
            freqd2 = freq_dict.get(descriptions[1])
            pmi = calculate_pmi(total_freq, freqd1, freqd2, jointfreq)
            csvwriter.writerow([row['description_pair'],str(jointfreq),str(freqd1),str(freqd2),str(pmi)])



def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 4:
        print('Usage: python add_individual_freq_pmi_to_joint_freq_file.py inputfile individualfreqs outputfile')
    else:
        add_ifreq_pmi(argv[1], argv[2], argv[3])


if __name__ == '__main__':
    main()
