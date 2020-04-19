import csv
buckeye_file = open('buckeye_words.txt')
buckeye_reader = csv.DictReader(buckeye_file, dialect='excel-tab')
buckeye = [row for row in buckeye_reader]
# print(buckeye[:2])
singular_f_theta = {}
for row in buckeye:
  if row['POS'] == 'NN' and (row['Surface'].endswith(
          'f') or row['Surface'].endswith('T')) and not row['Word'].endswith("'ve"):
    singular_f_theta[row['Surface']] = row['Word']

surface_forms = set(singular_f_theta.keys())
sing_mistakes = (
    'love',
    'leave',
    'drive',
    'nerf',
    'left',
    'wife',
    'paragraph',
    'stuff')
print('mVnT' in surface_forms)
pairs = []
for row in buckeye:
  sing_f = row['Surface'][:-2] + 'f'
  sing_T = row['Surface'][:-2] + 'T'
  ends_with_f = row['Surface'].endswith('fs') or row['Surface'].endswith(
      'fz') or row['Surface'].endswith('vs') or row['Surface'].endswith('vz')
  ends_with_t = row['Surface'].endswith('Ts') or row['Surface'].endswith(
      'Tz') or row['Surface'].endswith('Ds') or row['Surface'].endswith('Dz')
  if sing_f in surface_forms and ends_with_f:
    pairs.append({'sing_sur': sing_f,
                  'plur_sur': row['Surface'],
                  'sing_word': singular_f_theta[sing_f],
                  'plur_word': row['Word']})
    surface_forms.remove(sing_f)
  elif sing_T in surface_forms and ends_with_t:
    pairs.append({'sing_sur': sing_T,
                  'plur_sur': row['Surface'],
                  'sing_word': singular_f_theta[sing_T],
                  'plur_word': row['Word']})
    surface_forms.remove(sing_T)
    # print(sing_f, row['Surface'])
    # print(singular_f_theta[sing_f], row['Word'])
  # elif row['surface'][:-2] + 'T' in surface_forms:
for pair in pairs:
  print(pair['sing_word'], pair['plur_word'])

print(len(pairs))
