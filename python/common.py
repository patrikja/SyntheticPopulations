import numpy as np
import random

# The names of the different attributes. Can be arbitrarily many. 
attributes = ['attr_a', 'attr_b', 'attr_c']

# The names of the differint bins within an attribute. Can be arbitrarily many
#   for each attribute.
bin_names = [['a0', 'a1'], ['b0', 'b1', 'b2'], ['c0', 'c1', 'c2']]
bin_lengths    = map(lambda e: len(e), bin_names)

# The names of the different activitiy types. Can be arbitrarily many.
activities = ['act0', 'act1', 'act2']

# File names
micro_sample_csv = 'micro_sample.csv'
marginal_csvs = map(lambda e: e + '.csv', attributes)

survey_attributes_csv = 'survey_people.csv'
survey_activities_csv = 'survey_activities.csv'
synthetic_people_csv  = 'synthetic_population.csv'

#int[] -> int[][]
#Takes a list describing the number of bins for each attribute and
#Returns a matrix with all possible combinations of the bins.
#Each bin is represented by an index starting at zero.
def define_combinations(bin_lengths):
  n_attributes = len(bin_lengths)
  n_combinations = np.product(bin_lengths)
  bin_lengths_cum_prod = np.hstack((1, np.cumprod(bin_lengths)))
  combinations = np.zeros((n_combinations, n_attributes), dtype=np.int)
  for attribute_no in range(0, n_attributes):
    combination_no = 0
    for range_repeat in range(0, bin_lengths_cum_prod[n_attributes]/bin_lengths_cum_prod[attribute_no+1]):
      for bin_no in range(0, bin_lengths[attribute_no]):
        for bin_repeat in range(0, bin_lengths_cum_prod[attribute_no]):
          combinations[combination_no][attribute_no] = bin_no
          combination_no += 1
  return combinations


#(int, int) -> string
#Takes attribute index and bin index, looks up the bin name in bin_names and return it.
def bin_number_to_name(attribute_no, bin_no):
  return bin_names[attribute_no][bin_no]
