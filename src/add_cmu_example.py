from cmu_preprocessor import mayer_format
import csv


def get_cmu_examples(stress=False):
  f = open('corpora/cmudict-0.7b-ipa.tsv', encoding='utf-8')
  reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)

  ipa_to_ortho = {line[1]: line[0] for line in reader}
  # ipas = set(ipa_to_ortho.keys())
  new_examples = []
  # cmu_tuples = set([(line[0], line[1]) for line in reader])
  for ipa, item in ipa_to_ortho.items():
    if ',' not in ipa:
      formatted_ipa = mayer_format(ipa, stress=stress)
      if ipa.endswith('f') and ipa + \
              's' in ipa_to_ortho and "'" not in ipa_to_ortho[ipa + 's']:
        new_examples.append({'sing_item': item,
                             'plur_item': mayer_format(ipa_to_ortho[ipa + 's']),
                             'sing_ipa': formatted_ipa,
                             'plur_ipa': formatted_ipa + 's',
                             'voicing_rating': 1.0})
      elif ipa.endswith('f') and ipa[:-1] + \
              'vs' in ipa_to_ortho and "'" not in ipa_to_ortho[ipa[:-1] + 'vs']:
        new_examples.append({'sing_item': item,
                             'plur_item': ipa_to_ortho[ipa[:-1] + 'vs'],
                             'sing_ipa': formatted_ipa,
                             'plur_ipa': formatted_ipa[:-1] + 'vs',
                             'voicing_rating': 7.0})
      elif ipa.endswith('θ') and ipa + \
              's' in ipa_to_ortho and "'" not in ipa_to_ortho[ipa + 's']:
        new_examples.append({'sing_item': item,
                             'plur_item': mayer_format(ipa_to_ortho[ipa + 's']),
                             'sing_ipa': formatted_ipa,
                             'plur_ipa': formatted_ipa + 's',
                             'voicing_rating': 1.0})
      elif ipa.endswith('θ') and ipa[:-1] + \
              'ðs' in ipa_to_ortho and "'" not in ipa_to_ortho[ipa[:-1] + 'ðs']:
        new_examples.append({'sing_item': item,
                             'plur_item': ipa_to_ortho[ipa[:-1] + 'ðs'],
                             'sing_ipa': formatted_ipa,
                             'plur_ipa': formatted_ipa[:-1] + 'ðs',
                             'voicing_rating': 7.0})

  return new_examples
  # print(new_examples)
  # print(len(new_examples))


if __name__ == "__main__":
  get_cmu_examples()
