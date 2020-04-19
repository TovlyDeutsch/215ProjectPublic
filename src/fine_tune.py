import torch
import torch.nn as nn
import csv
import pickle
import random
import time
import argparse
import math
from add_cmu_example import get_cmu_examples
from collections import defaultdict
from model import Emb_RNNLM

DEFAULT_FEATURES_FILE = None
DEFAULT_D_EMB = 24
DEFAULT_D_HID = 64
DEFAULT_NUM_LAYERS = 1
DEFAULT_BATCH_SIZE = 16
DEFAULT_LEARNING_RATE = 0.005
DEFAULT_EPOCHS = 10
DEFAULT_TIED = True
DEFAULT_TRAINING_SPLIT = 80
DEFAULT_DEV = True


SPECIAL_LABELS = ['<p>', '<s>', '<e>']


def get_targets(dataset):
  targets = dataset[:, -1]
  targets = targets.float()
  targets = targets / 10e6
  return targets


def naive_baseline(training, dev, criterion_fun=nn.MSELoss):
  criteria = [nn.MSELoss, nn.L1Loss]
  # criterion = criterion_fun(reduction="sum")
  num_examples, seq_len = dev.size()

  mean_train_target = get_targets(training).mean()
  dev_targets = get_targets(dev)
  preds = torch.tensor([mean_train_target] * dev.size()[0])
  print(mean_train_target)
  losses = defaultdict(float)
  for criterion in criteria:
    loss = criterion()(preds, dev_targets).detach().item()
    losses[criterion.__name__] = loss

  return losses


def compute_dev_loss(dataset, net, bsz=64, criterion_fun=nn.MSELoss):
  criteria = [nn.MSELoss, nn.L1Loss]
  losses = defaultdict(float)

  num_examples, seq_len = dataset.size()

  batches = [(start, start + bsz) for start in
             range(0, num_examples, bsz)]

  nll = 0.
  for b_idx, (start, end) in enumerate(batches):
    batch = dataset[start:end][:, :-1].cuda()
    targets = dataset[start:end][:, -1].cuda()
    preds = net(batch).cuda()
    preds = preds.view(-1)
    targets = targets.float()
    targets = targets / 10e6
    for criterion in criteria:
      loss = criterion(reduction="sum")(preds, targets).detach().item()
      losses[criterion.__name__] += loss

  losses = {k: v / num_examples for k, v in losses.items()}
  return losses


def get_plural_data(filename):
  raw_data = []
  f = open(filename, 'r', encoding='utf-8')
  reader = csv.DictReader(f, dialect='excel-tab')
  for line in reader:
    # TODO don't ignore multiple prnounciations
    if ',' in line['IPA']:
      continue
    line['IPA'] = line['IPA'].rstrip()
    line['IPA'] = ['<s>'] + list(line['IPA']) + ['<e>']
    raw_data.append(line)
  return raw_data


def process_data(
        string_training_data,
        inventory,
        phone2ix,
        ix2phone,
        dev=True,
        training_split=60,
        inject=False,
        cross_valid=None,
        test_set='eng',
        stress=False):
  if inject:
    print('injecting additional training data')
    new_examples = get_cmu_examples(stress=stress)
    existing_IPA = set([tuple(ex['IPA']) for ex in string_training_data])
    def process(word): return ['<s>'] + list(word.rstrip()) + ['<e>']
    processed_new = [
        {
            'IPA': process(
                ex['sing_ipa']), 'voice': ex['voicing_rating']} for ex in new_examples if tuple(
            process(
                ex['sing_ipa'])) not in existing_IPA]
    unfiltered_processed_new = [{'IPA': process(
        ex['sing_ipa']), 'voice': ex['voicing_rating']} for ex in new_examples]
    string_training_data += processed_new
    # print(string_training_data)
  prepend = "stress_" if stress else ""
  raw_wugs = get_plural_data(f'corpora/{prepend}wug_voicing_ratings.tsv')
  random.shuffle(raw_wugs)
  random.shuffle(string_training_data)
  # all data points need to be padded to the maximum length
  max_chars = max([len(x['IPA']) for x in string_training_data + raw_wugs])
  # encode vocing rating (target) as last column
  string_training_data = [
      sequence['IPA'] + ['<p>'] * (max_chars - len(sequence['IPA'])) + [sequence['voice']]
      for sequence in string_training_data]
  wug_data = [
      sequence['IPA'] + ['<p>'] * (max_chars - len(sequence['IPA'])) + [sequence['voice']]
      for sequence in raw_wugs]

  def phonify(sample):
    return torch.LongTensor([phone2ix[p]
                             for p in sample[:-1]] + [float(sample[-1]) * 10e6])

  as_ixs = [phonify(sequence) for sequence in string_training_data]
  as_ixs_wug = [phonify(sequence) for sequence in wug_data]

  if test_set == 'wug':
    training_data = torch.stack(as_ixs, 0)
    dev = torch.stack(as_ixs_wug, 0)
  elif test_set == 'wug_half':
    halfway = math.floor(len(as_ixs_wug) / 2)
    training_data = torch.stack(as_ixs, 0)
    dev = torch.stack(as_ixs_wug[:halfway], 0)
  elif test_set == 'wug_half_both':
    halfway = math.floor(len(as_ixs_wug) / 2)
    training_data = torch.stack(
        as_ixs + as_ixs_wug[halfway:], 0)
    dev = torch.stack(as_ixs_wug[:halfway], 0)
  elif not dev:
    raise AssertionError('dev must be true')
  elif cross_valid is None:
    split = math.floor(len(as_ixs) * (training_split / 100))
    training_data = torch.stack(as_ixs[:split], 0)
    dev = torch.stack(as_ixs[split:], 0)
  else:
    packages = []
    for i in range(cross_valid):
      split_start = math.floor(len(as_ixs) * (i / cross_valid))
      split_end = math.floor(len(as_ixs) * ((i + 1) / cross_valid))
      print(split_start, split_end)
      training_data = torch.stack(as_ixs[:split_start] + as_ixs[split_end:], 0)
      dev = torch.stack(as_ixs[split_start:split_end], 0)
      packages.append((training_data, dev, max_chars))
    return packages

  return training_data, dev, max_chars


def train_lm(dataset, dev, params, net, seed=0):
  criterion = nn.SmoothL1Loss()
  optimizer = torch.optim.Adam(
      net.R2o.parameters(),
      lr=params['learning_rate'])
  num_examples, seq_len = dataset.size()
  batches = [
      (start, start + params['batch_size'])
      for start in range(0, num_examples, params['batch_size'])
  ]

  best_epoch_loses = None
  prev_perplexity = 1e10
  for epoch in range(params['epochs']):
    ep_loss = 0.
    start_time = time.time()
    random.shuffle(batches)

    for b_idx, (start, end) in enumerate(batches):
      batch = dataset[start:end][:, :-1].cuda()
      targets = dataset[start:end][:, -1].cuda()
      preds = net(batch).cuda()
      preds = preds.view(-1)
      targets = targets.float()
      targets = targets / 10e6
      loss = criterion(preds, targets)

      loss.backward()
      optimizer.step()
      optimizer.zero_grad()
      ep_loss += loss.detach()

    best_abs_loss = 100
    best_mse_loss = 100

    epoch_dev_losses = compute_dev_loss(dev, net, bsz=params['batch_size'])
    if best_epoch_loses is None or epoch_dev_losses['MSELoss'] < best_epoch_loses['MSELoss']:
      best_epoch_loses = epoch_dev_losses

    # print(
    #     'epoch: %d, loss: %0.2f, time: %0.2f sec, dev mse loss: %0.2f, dev abs loss: %0.2f' %
    #     (epoch, ep_loss, time.time() - start_time, mse_dev_loss, abs_dev_loss))

    # stop early criterion, increasing perplexity on dev
    # if dev_perplexity - prev_perplexity > 0.01:
    #   print('Stop early reached')
    #   break
  return best_epoch_loses


def reshape_output(x): return x.reshape(x.size()[0], -1)


def train_and_eval(rnn_params, inject=False, cross_valid=None):
  prepend = "stress_" if rnn_params["stress"] else ""
  raw_data = get_plural_data(f'corpora/{prepend}english_voicing_ratings.tsv')
  phone2ix = pickle.load(open(f'models/{prepend}phone2ix.bin', mode='rb'))
  ix2phone = pickle.load(open(f'models/{prepend}ix2phone.bin', mode='rb'))
  inventory = pickle.load(open(f'models/{prepend}inventory.bin', mode='rb'))
  inventory_size = len(inventory)
  rnn_params['inv_size'] = inventory_size

  def train_and_eval_with_data(training, dev, max_chars):
    # TODO change to base non-pretrained model if rnn_params['pretrain'] == False
    # look at main.py for how to get untrained model
    if rnn_params['pretrain']:
      # load pretrained model
      print('loading pretrained')
      model = torch.load(
          f"models/rnn_{rnn_params['stress']}_{rnn_params['num_layers']}_{rnn_params['d_emb']}_{rnn_params['d_hid']}.pt")
    else:
      model = Emb_RNNLM(rnn_params).cuda()

    for param in model.parameters():
      param.requires_grad = False

    model.resizer = reshape_output
    # Replace the last fully-connected layer
    # Parameters of newly constructed modules have requires_grad=True by
    # default
    model.R2o = nn.Linear(model.d_hid * max_chars, 1).cuda()

    naive_errors = naive_baseline(training, dev)

    # print(f'naive guess mse dev: {naive_baseline(training, dev)}')
    # print(
    # f'naive guess abs dev: {naive_baseline(training, dev,
    # criterion_fun=nn.L1Loss)}')
    model_errors = train_lm(training, dev, rnn_params, model)
    model_errors.update({('naive_' + k): v for k, v in naive_errors.items()})
    return model_errors

  processed_data = process_data(
      raw_data,
      inventory,
      phone2ix,
      ix2phone,
      inject=inject,
      cross_valid=cross_valid,
      test_set=rnn_params['test_set'],
      stress=rnn_params['stress'])

  results = []
  if isinstance(processed_data, list):
    for training, dev, max_chars in processed_data:
      result = train_and_eval_with_data(training, dev, max_chars)
      results.append(result)
  else:
    training, dev, max_chars = processed_data
    result = train_and_eval_with_data(training, dev, max_chars)
    results.append(result)

  avgs = defaultdict(float)
  for result in results:
    for key, value in result.items():
      avgs[key] += value
  for key in avgs:
    if cross_valid is not None:
      avgs[key] /= cross_valid
  return avgs


# TODO remove this main function, maybe?
# if __name__ == "__main__":
#   parser = argparse.ArgumentParser(
#       description="Generates a vector embedding of sounds in "
#       "a phonological corpus using a RNN."
#   )
#   parser.add_argument(
#       '--d_emb',
#       type=int,
#       help='Number of dimensions for the output embedding.',
#       default=DEFAULT_D_EMB)
#   parser.add_argument(
#       '--d_hid',
#       type=int,
#       help='Number of dimensions for the hidden layer embedding.',
#       default=DEFAULT_D_HID)
#   parser.add_argument(
#       '--num_layers', type=int, help='Number of layers in the RNN',
#       default=DEFAULT_NUM_LAYERS
#   )
#   parser.add_argument(
#       '--batch_size', type=int, help='Batch size.',
#       default=DEFAULT_BATCH_SIZE
#   )
#   parser.add_argument(
#       '--learning_rate', type=float, help='Learning rate.',
#       default=DEFAULT_LEARNING_RATE
#   )
#   parser.add_argument(
#       '--epochs', type=int, help='Number of training epochs.',
#       default=DEFAULT_EPOCHS,
#   )
#   parser.add_argument(
#       '--tied', default=DEFAULT_TIED, help='Whether to use tied embeddings.',
#       action='store_true'
#   )
#   parser.add_argument(
#       '--training_split', type=int, default=DEFAULT_TRAINING_SPLIT,
#       help='Percentage of data to place in training set.'
#   )
#   parser.add_argument(
#       '--dev', default=DEFAULT_DEV,
#       help='Trains on all data and tests on a small subset.'
#   )

#   args = parser.parse_args()

#   raw_data = get_plural_data('corpora/english_voicing_ratings.tsv')
#   phone2ix = pickle.load(open('models/phone2ix.bin', mode='rb'))
#   ix2phone = pickle.load(open('models/ix2phone.bin', mode='rb'))
#   inventory = pickle.load(open('models/inventory.bin', mode='rb'))
#   inventory_size = len(inventory)

#   rnn_params = {}
#   rnn_params['d_emb'] = args.d_emb
#   rnn_params['d_hid'] = args.d_hid
#   rnn_params['num_layers'] = args.num_layers
#   rnn_params['batch_size'] = args.batch_size
#   rnn_params['learning_rate'] = args.learning_rate
#   rnn_params['epochs'] = args.epochs
#   rnn_params['tied'] = args.tied
#   rnn_params['inv_size'] = inventory_size
