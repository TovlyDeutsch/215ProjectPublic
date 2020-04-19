import csv
import re


def mayer_format(word, stress=False):
  if stress:
    result = re.sub("[ˌː]", "", word)
  else:
    result = re.sub("[ˌˈː]", "", word)
  result = re.sub(r"r", "ɹ", result)
  return result


if __name__ == "__main__":
  f = open('corpora/cmudict-0.7b-ipa.tsv', encoding='utf-8')
  out_f = open(
      'corpora/stress_cmudict_processed.tsv',
      mode='w',
      newline='',
      encoding='utf-8')
  reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
  writer = csv.writer(out_f, delimiter='\t')
  for line in reader:
    formatted = mayer_format(line[1], stress=True)
    forms = formatted.split(', ')
    for form in forms:
      writer.writerow([" ".join(form)])

  f.close()
  out_f.close()
