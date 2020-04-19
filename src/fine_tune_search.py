from fine_tune import train_and_eval
import itertools
import os
import sys
from main import pretrain
import json
import numpy as np
from scipy import stats
import random
import math
from collections import defaultdict
from statsmodels.stats.multicomp import (pairwise_tukeyhsd,
                                         MultiComparison)


def avg_runs(rnn_params, num_runs):
  total_loss = 0
# TODO consider signifance testing between models if num_runs = 2
  results = []
  for i in range(num_runs):
    random.seed(i)
    result = train_and_eval(
        rnn_params,
        inject=rnn_params['inject'],
        cross_valid=None)

    results.append(result)
  return results


def pretrain_if_needed(finetune_params):
  pretrain_rnn_params = {}
  pretrain_rnn_params['d_emb'] = finetune_params['d_emb']
  # these must be the same
  pretrain_rnn_params['d_hid'] = finetune_params['d_hid']
  pretrain_rnn_params['stress'] = finetune_params['stress']
  pretrain_rnn_params['num_layers'] = finetune_params['num_layers']
  pretrain_rnn_params['batch_size'] = 64
  pretrain_rnn_params['learning_rate'] = 0.005
  pretrain_rnn_params['epochs'] = 10
  pretrain_rnn_params['tied'] = False
  model_path = f"models/rnn_{finetune_params['stress']}_{finetune_params['num_layers']}_{pretrain_rnn_params['d_emb']}_{pretrain_rnn_params['d_hid']}.pt"
  print('trying to load:', model_path)
  if not os.path.exists(model_path):
    print('pretraining')

    pretrain_data = 'corpora/cmudict_processed.tsv' if not finetune_params[
        'stress'] else 'corpora/stress_cmudict_processed.tsv'
    test_data = 'corpora/unused/Daland_et_al_IPA.txt'

    pretrain(
        pretrain_rnn_params,
        pretrain_data,
        80,
        None,
        test_data,
        "results/p.txt")


def print_stat_tests(results):
  tuples = []
  for group_id_tuple, result_values_list in results.items():
    tuples += [(str(group_id_tuple), math.sqrt(v['MSELoss']))
               for v in result_values_list]
  tuples += [('naive', v['naive_MSELoss']) for v in list(results.values())[0]]
  # print(tuples)
  dta2 = np.array(tuples, dtype=[
      ('group', '|S2000'),
      ('rmse', '<f8')])
  # print(dta2)
  # print(len(set(dta2['group'])))
  res2 = pairwise_tukeyhsd(dta2['rmse'], dta2['group'])
  print(res2, file=open('sigs.json', 'w'))
  # TODO for each group, one sample t test against naive rmse


def dict_mean(dict_list):
  mean_dict = {}
  for key in dict_list[0].keys():
    mean_dict[key] = sum(d[key] for d in dict_list) / len(dict_list)
  return mean_dict


def search_hyperparams(rnn_param_lists):
  keys, values = zip(*rnn_param_lists.items())
  experiments = [dict(zip(keys, v)) for v in itertools.product(*values)]
  print(f'{len(experiments)} experiments')
  print(experiments[:3])
  results = {}
  unaveraged_results = {}
  for rnn_params in experiments:
    print(f'running exp {len(results)}')
    pretrain_if_needed(rnn_params)
    raw_results = avg_runs(rnn_params, 1000)
    # print(raw_results)
    unaveraged_results[tuple(rnn_params.items())] = raw_results
    results[tuple(rnn_params.items())] = dict_mean(raw_results)
    print(results)
    sorted_results = {
        str(k): v for k,
        v in sorted(
            results.items(),
            key=lambda item: item[1]['MSELoss'] -
            item[1]['naive_MSELoss'])}
  json.dump(sorted_results, open('results/runs.json', 'w'))
  print_stat_tests(unaveraged_results)
  # print(sorted_results)

# best result: ('d_emb', 48), ('d_hid', 128), ('num_layers', 1),
# ('batch_size', 64), ('learning_rate', 0.0005), ('epochs', 100)


if __name__ == "__main__":
  rnn_params = {}
  # exhaustive search
  # these two are pretrain params
  # rnn_params['d_emb'] = [12, 24, 48]
  # rnn_params['d_hid'] = [8, 16, 32, 64, 128]
  # rnn_params['num_layers'] = [1, 2, 4, 8, 16]
  # # these are fine-tuning params
  # rnn_params['batch_size'] = [64]
  # rnn_params['learning_rate'] = [0.00005, 0.0005, 0.005]
  # rnn_params['epochs'] = [100]
  # rnn_params['tied'] = [False]
  # rnn_params['inject'] = [True, False]
  # rnn_params['pretrain'] = [True, False]

  # simple runs search
  # these two are pretrain params
  rnn_params['d_emb'] = [24]
  rnn_params['d_hid'] = [64]
  rnn_params['num_layers'] = [4]
  # rnn_params['num_layers'] = [1, 2, 4]
  # these are fine-tuning params
  rnn_params['batch_size'] = [64]
  rnn_params['learning_rate'] = [0.005]
  rnn_params['epochs'] = [100]
  rnn_params['tied'] = [False]
  rnn_params['inject'] = [True]  # extra eng from cmu
  rnn_params['pretrain'] = [False]
  # rnn_params['test_set'] = ['eng', 'wug', 'wug_half', 'wug_half_both'] # test set should
  # really be renamed experiments
  rnn_params['test_set'] = ['wug_half', 'wug_half_both']
  rnn_params['stress'] = [False]

  search_hyperparams(rnn_params)
