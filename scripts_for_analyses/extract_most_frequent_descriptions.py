import sys
import csv
from collections import defaultdict


def create_class_dict(my_classifications):

    class_dict = defaultdict(list)
    i = 0
    while i < len(my_classifications):
        if i%2 == 0:
            myclass = my_classifications[i]
            term = my_classifications[i+1]
            class_dict[myclass].append(term)
        i += 1
    return class_dict

def create_frequency_dicts(inputfile, maxlength):

    maxlength = int(maxlength)
    frequency_dict = defaultdict(dict)
    with open(inputfile, 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=';')
        for row in csvreader:
            mydescriptions = row['description_pair'].split('+++')
            my_classifications = row['category reason'].split('+')
            class_dict = create_class_dict(my_classifications)
            for k, v in class_dict.items():
                cfreq_dict_all = frequency_dict.get(k + '-all')
                cfreq_dict_neut = frequency_dict.get(k + '-neut')
                if cfreq_dict_all is None:
                    cfreq_dict_all = defaultdict(int)
                    cfreq_dict_neut = defaultdict(int)
                    frequency_dict[k + '-all'] = cfreq_dict_all
                    frequency_dict[k + '-neut'] = cfreq_dict_neut
                words1 = mydescriptions[0].split()
                words2 = mydescriptions[1].split()
                if len(words1) < maxlength:
                    cfreq_dict_all[mydescriptions[0]] += int(row['joint freq'])
                    if len(set(v) & set(words1)) == 0:
                        cfreq_dict_neut[mydescriptions[0]] += int(row['joint freq'])
                if len(words2) < maxlength:
                    cfreq_dict_all[mydescriptions[1]] += int(row['joint freq'])
                    if len(set(v) & set(words2)) == 0:
                        cfreq_dict_neut[mydescriptions[1]] += int(row['joint freq'])
    return frequency_dict






def select_most_frequent(inputfile, output, maxlength=100):

    frequency_dict = create_frequency_dicts(inputfile, maxlength)
    allout = open(output + '-all.csv', 'w')
    allwriter = csv.writer(allout, delimiter=';')
    allwriter.writerow(['description','class','freq'])
    neutout = open(output + '-nclass.csv', 'w')
    neutwriter = csv.writer(neutout, delimiter=';')
    neutwriter.writerow(['description','class','freq'])

    for k, mydict in frequency_dict.items():
        classname = k.split('-')[0]
        for description in sorted(mydict, key=mydict.get, reverse=True):
            if k.endswith('-all'):
                allwriter.writerow([description,classname,str(mydict.get(description))])
            elif k.endswith('-neut'):
                neutwriter.writerow([description,classname,str(mydict.get(description))])






def main(argv=None):

    if argv is None:
        argv = sys.argv


    if len(argv) < 3:
        print('Usage: python extract_most_frequent_descriptions.py inputfile outputfile (maxlength)')
    elif len(argv) < 4:
        select_most_frequent(argv[1], argv[2])
    else:
        select_most_frequent(argv[1], argv[2], argv[3])



if __name__ == '__main__':
    main()
