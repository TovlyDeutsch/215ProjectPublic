import epitran
import re
import csv
becker_file = open('beeker_singular_and_plural.tsv')
becker_processed = open('beeker_singular_and_plural_processed.tsv', 'w')
reader = csv.DictReader(becker_file, dialect='excel-tab')

epi = epitran.Epitran('eng-Latn')


def subs(string, sub_pairs):
  for pattern, replace in sub_pairs:
    string = re.sub(pattern, replace, string)
  return string


def transiliterate(word):
  transliterated = epi.transliterate(word)
  subbed = subs(transliterated, [('ow', 'oʊ'), ('aw', 'aʊ'),
                                 ('ej', 'eɪ'), ('aj', 'aɪ'), ('oj', 'ɔɪ')])
  return subbed


rows = []
for row in reader:
  row['singular_phonetic'] = transiliterate(row['Word'])
  row['plural_phonetic_1'] = transiliterate(row['plural_word'])
  rows.append(row)

writer = csv.DictWriter(becker_processed, rows[0].keys(), dialect='excel-tab')
writer.writeheader()
writer.writerows(rows)
