import csv
import pandas

english_words_file = open('exp1.csv')
# wug_file = open('exp2.csv')

eng_df = pandas.read_csv('exp1.csv')
# eng_df = pandas.unique(eng_df)
eng_df = eng_df[['item', 'IPA', 'place']].drop_duplicates()
# pandas unique
eng_df = eng_df[eng_df.place != 'x']
eng_df.sort_values('item')
print(eng_df.tail(40))
# why is this 378 instead of the 126 described in paper?
# check num in appendix
print(eng_df.size)
