import pandas as pd
import numpy as np
import random

#The names of the different attributes. Can be arbitrarily many. Will be used as names for marginal 
#distribution files and as headers in micro sample.
attributes = ['attr_a', 'attr_b', 'attr_c']

#The names of the differint bins within an attribute. Can be arbitrarily many for each attribute.
#Will be used in micro sample.
bin_names = [['a1', 'a2'], ['b1', 'b2', 'b3'], ['c1', 'c2', 'c3']]

#Number of agents to use in the micro sample
n_micro_samples = 500

n_attributes = len(attributes)

n_combinations = np.product(map(lambda e: len(e), bin_names))

def inc_bin_indices(bi_list, ind, bin_names):
  bi_list[ind] += 1
  if bi_list[ind] == len(bin_names[ind]):
    bi_list[ind] = 0
    if ind < n_attributes - 1:
      return inc_bin_indices(bi_list, ind+1, bin_names)
  return bi_list

bin_indices = np.zeros(n_attributes, dtype=np.int)

#Create macro sample (this is the 'truth')
combinations = np.zeros((n_combinations, n_attributes), dtype=np.int)
counts = np.zeros(n_combinations, dtype=np.int)
for combination_no in range(0, n_combinations):
  for attribute_no in range(0, n_attributes):
    combinations[combination_no][attribute_no] = bin_indices[attribute_no]
  counts[combination_no] = random.randint(0,100)
  bin_indices = inc_bin_indices(bin_indices, 0, bin_names)

print np.column_stack((combinations, counts))

cum_counts = np.cumsum(counts)
#Create marginal distributions and save as csv
for attribute_no in range(0, n_attributes):
  attribute_marginal = []
  for bin_no in range(0, len(bin_names[attribute_no])):
    sum_over_bin = 0
    for combination_no in range(0, n_combinations):
      if combinations[combination_no][attribute_no] == bin_no:
        sum_over_bin += counts[combination_no]
    attribute_marginal.append(sum_over_bin)
  pd.DataFrame([attribute_marginal], columns=bin_names[attribute_no]).to_csv(attributes[attribute_no] + '.csv', index=False)

#Create micro sample and save as csv
micro_sample = []
for micro_row in range(0, n_micro_samples):
  ran = random.randint(0, cum_counts[len(cum_counts)-1])
  macro_row = 0
  while ran > cum_counts[macro_row]:
    macro_row += 1
  sample_row = []
  for attribute_no in range(0, n_attributes):
    sample_row.append(bin_names[attribute_no][combinations[macro_row][attribute_no]])
  micro_sample.append(sample_row)
pd.DataFrame(micro_sample, columns=attributes).to_csv('micro_sample.csv', index=False)
