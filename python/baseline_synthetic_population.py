import pandas as pd
import numpy as np
import random
from common import *
import sys

n_attributes = len(attributes)
# Number of unique combinations of bins from the attributes in the micro sample.
n_combinations = np.product(map(lambda e: len(e), bin_names))

marginal_bin_names = map(lambda csv: pd.read_csv(csv).columns.values.squeeze().tolist(), marginal_csvs)
marginals = map(lambda csv: pd.read_csv(csv).values.squeeze().tolist(), marginal_csvs)

#(int[][], data_frame) -> int[]
#Takes a matrix with all combinations of attribute values and a sample of agents
#and returns a vector with the number of agents in the sample that match each combination.
#TODO: Investigate if filtering on attribute values can be implemented better.
def counts_from_sample(combinations, sample):
  counts = np.zeros(n_combinations, dtype=np.int)
  for combination_no in range(0, combinations.shape[0]):
    sample_temp = sample
    #For each attribute, only keep the rows where the value for this attribute 
    #  matches the value of the current combination (given by combination_no)
    for attribute_no in range(0, combinations.shape[1]):
      sample_temp = sample_temp[sample_temp[attributes[attribute_no]] == bin_number_to_name(attribute_no, combinations[combination_no][attribute_no])]
  
    # The rows still remaining in the data frame are the ones where all the attribute
    #   values match the current combination.
    counts[combination_no] = len(sample_temp.index)
  return counts


#(int[][], int[], int[][], epsilon) -> (float[], int)
#Takes the micro sample described by combinations and counts and uses IPF to scale
#it up to a big population matching the marginal distributions given by marginals.
#Convergence is considired to be reached when the sum of errors over all bins is less
#than epsilon. Returns a list with new counts and a number of how many iterations that
#were performed.
def ipf(combinations, counts, marginals, epsilon):
  counts = counts.astype(np.float)
  n_combinations = combinations.shape[0]
  n_attributes = combinations.shape[1]
  steps = 0
  diff_sum = 1.
  while diff_sum >= epsilon:
    diff_sum = 0.
    for attribute_no in range(0, n_attributes):
      for bin_no in range(0, len(bin_names[attribute_no])):
  
        # Sum counts over all combinations that contains the current bin for the
        #   current attribute.
        sum_over_bin = 0.
        for combination_no in range(0, n_combinations):
          if combinations[combination_no][attribute_no] == bin_no:
            sum_over_bin += counts[combination_no]
  
        # Add the difference between actual and desired marginal distribution
        # value for bin to total deviation.
        diff_sum += abs(sum_over_bin - marginals[attribute_no][bin_no])
  
        # Update all combinations for the current bin for the current attribute
        #   so that the sum over the bin is identical to the marginal distribution
        #   value for this bin.
        for combination_no in range(0, n_combinations):
          if combinations[combination_no][attribute_no] == bin_no:
            counts[combination_no] *= marginals[attribute_no][bin_no]/sum_over_bin
  
    steps += 1
  return (counts, steps) 

#(int[][], float[], int[]) -> string
#Transform a matrix with combinations and two vector with counts to a
#good looking printable string, using the names of the bins.
#TODO: Alignment
def combinations_with_counts_to_string(combinations, counts_new, counts_orig):
  out_string = 'Full population\n'
  out_string = 'Results.\n\
First n_attributes columns are the combinations of bins.\n\
The third last column is people in the micro sample for each combination.\n\
The second last column is the value after IPF. The last column is their ratio.\n'

  for combination_no in range(0, combinations.shape[0]):
    for attribute_no in range(0, combinations.shape[1]):
      bin_no = combinations[combination_no][attribute_no]
      out_string += bin_number_to_name(attribute_no, bin_no) + ' '
    out_string += '  ' + str(counts_orig[combination_no]) + '  ' + str(round(counts_new[combination_no], 3)) + '  ' + str(round(counts_new[combination_no]/counts_orig[combination_no], 3)) + '\n'
  return out_string


#(int[][], int[]) -> data_frame
#Takes a synthetic population expressed as a list of combinations of attributes
#and the number of agents with each combination and creates a data frame with 
#one row for every agent. The agents are randomly assigned into households with random
#size.
def create_synthetic_population(combinations, counts):
  n_persons     = np.sum(counts)
  household_ids = sorted([random.randrange(1, n_persons/3) for i in range(0, n_persons)]) #TODO: better
  person_id     = 1
  synt_pop_df   = pd.DataFrame(columns=['person_id', 'household_id'] + attributes)
  for combination_no in range(0, n_combinations):
    for person_no in range(0, counts[combination_no]):
      row = pd.DataFrame(columns=['person_id', 'household_id'] + attributes)
      row.set_value(0, 'person_id', person_id)
      row.set_value(0, 'household_id', household_ids[person_id-1])
      for attribute_no in range(0, len(attributes)):
        bin_no = combinations[combination_no][attribute_no]
        row.set_value(0, attributes[attribute_no], bin_number_to_name(attribute_no, bin_no))
      synt_pop_df = synt_pop_df.append(row)
      person_id += 1

  return synt_pop_df
  

#------------ Create micro sample matrix ------------
# Create matrix 'combinations' where each row is a unique combination of bins,
#   with one bin from each attribute in the micro sample.
# The indices of the bins of attribute n are described in column n.
# Create vector 'counts', the number of agents (persons, households ...) in
#   the micro sample for the combination described in the matrix. The values
#   in the vector will be increased during IPF.
# Example with n_attributes=3 and len(sample_bin_names=[2, 2, 3]:
# Matrix   Vector
# 0 0 0    3.0
# 1 0 0    3.0
# 0 1 0    9.0
# 1 1 0    4.0
# 0 0 1    2.0
# 1 0 1    6.0
# 0 1 1    4.0
# 1 1 1    1.0
# 0 0 2    8.0
# 1 0 2    5.0
# 0 1 2    1.0
# 1 1 2    2.0

combinations = define_combinations(bin_lengths)
counts_orig = counts_from_sample(combinations, pd.read_csv(micro_sample_csv)[attributes])

#ipf
(counts_new, iterations) = ipf(combinations, counts_orig, marginals, 0.01)

#---------- Print results -------------
print "No of iterations: {0}".format(iterations)
print combinations_with_counts_to_string(combinations, counts_new, counts_orig)

counts_int = np.round(counts_new).astype(np.int) #TODO: Round in a way to perserve marginal distriputions.

# Create synthetic population from combinations and write to file.
create_synthetic_population(combinations, counts_int).to_csv(synthetic_people_csv, index=False)
