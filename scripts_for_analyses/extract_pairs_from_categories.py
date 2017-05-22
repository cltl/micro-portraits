import sys
import csv


def create_category_dict(catfile):

    words2cats = {}
    with open(catfile, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in csvreader:
            cat = row.pop(0)
            for lemma in row:
                words2cats[lemma] = cat

    return words2cats


def check_exact_word_match(word, pair):

    if ' ' + word + ' ' in pair or ' ' + word + '+' in pair or '+' + word + ' ' in pair:
        return True

    if pair.startswith(word + ' ') or pair.startswith(word + '+'):
        return True

    if pair.endswith(' ' + word) or pair.endswith('+' + word):
        return True

    return False


def check_categories_mentioned_in_pair(pair, words2cats):

    cats = []
    for word, cat in words2cats.items():
        if word in pair:
            if check_exact_word_match(word, pair):
                cats.append(cat + '+' + word)

    return cats




def extract_pairs_from_categories(catfile, ppmifile, outputfile, threshold=0):

    #1. create category dict
    #2. walk through ppmi file and print (for relevant and for above threshold) n, pair, cat, ...scores...

    catDict = create_category_dict(catfile)
    output = open(outputfile, 'w')
    outcsv = csv.writer(output, delimiter=';', quotechar='"')
    threshold = int(threshold)
    outcsv.writerow(['number','description_pair','category reason','joint freq','freq d1','freq d2','pmi'])
    counter = 0
    with open(ppmifile, 'rb') as csvinput:
        csvreader = csv.DictReader(csvinput, delimiter=';', quotechar='"')
        for row in csvreader:
            counter += 1
            if counter%10000000 == 0:
                print(counter)
            if int(row['joint freq']) > threshold:
                cats = check_categories_mentioned_in_pair(row['description_pair'], catDict)
                if len(cats) > 0:
                    outcsv.writerow([row['number'], row['description_pair'], "+".join(cats), row['joint freq'], row['freq d1'], row['freq d2'], row['ppmi']])






def main(argv=None):

    if argv is None:
        argv = sys.argv

    if len(argv) < 4:
        print('Usage: python extract_pairs_from_categories.py category_file.csv ppmi_file.csv output.csv (threshold)')
    elif len(argv) < 5:
        extract_pairs_from_categories(argv[1], argv[2], argv[3])
    else:
        extract_pairs_from_categories(argv[1], argv[2], argv[3], argv[4])


if __name__ == '__main__':
    main()
