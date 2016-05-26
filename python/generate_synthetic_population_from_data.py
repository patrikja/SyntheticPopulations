import pandas as pd
import numpy as np


micro_csv = 'micro_sample.csv'
sample_attributes = ['attr_a', 'attr_b', 'attr_c']
sample_bin_names = [['a1', 'a2'], ['b1', 'b2', 'b3'], ['c1', 'c2', 'c3']] 

marginal_csvs = ['attr_a.csv', 'attr_b.csv', 'attr_c.csv']

#micro_csv = 'pop_pums_500.csv'
#sample_attributes = ['sex', 'age', 'race']
#sample_bin_names = [[1, 2], [1, 2, 3], [1, 2, 3]] 
#
#marginal_csvs = ['sex_marginal.csv', 'age_marginal.csv', 'race_marginal.csv']


micro_df = pd.read_csv(micro_csv)[sample_attributes]
n_attributes = len(sample_attributes)
n_combinations = np.product(map(lambda e: len(e), sample_bin_names)) #Number of unique combinations of bins from the attributes in the micro sample

marginal_bin_names = map(lambda csv: pd.read_csv(csv).columns.values.squeeze().tolist(), marginal_csvs)
marginals = map(lambda csv: pd.read_csv(csv).values.squeeze().tolist(), marginal_csvs)

def inc_bin_indices(bi_list, ind, bin_names):
  bi_list[ind] += 1
  if bi_list[ind] == len(bin_names[ind]):
    bi_list[ind] = 0
    if ind < n_attributes - 1: 
      return inc_bin_indices(bi_list, ind+1, bin_names)
  return bi_list

#A list of indices for sample_bin_names. This list is updated for every combination of bins below, and used so that 
#each combination is expressed by a unique combination of bin indices. 
bin_indices = np.zeros(n_attributes, dtype=np.int)

#------------ Create micro sample matrix ------------
#Create matrix 'combinations' where each row is a unique combination of bins, with one bin from each attribute in the micro sample.
#The indices of the bins of attribute n are described in column n.
#Create vector 'counts', the number of agents (persons, households ...) in the micro 
#sample for the combination described in the matrix. The values in the vector will be increased during IPF
#Example with n_attributes=3 and len(sample_bin_names=[2, 2, 3]:
#Matrix   Vector
#0 0 0    3.0
#1 0 0    3.0
#0 1 0    9.0
#1 1 0    4.0
#0 0 1    2.0
#1 0 1    6.0
#0 1 1    4.0
#1 1 1    1.0
#0 0 2    8.0
#1 0 2    5.0
#0 1 2    1.0
#1 1 2    2.0

combinations = np.zeros((n_combinations, n_attributes), dtype=np.int)
counts = np.zeros(n_combinations, dtype=np.float)
for combination_no in range(0, n_combinations):
  micro_df_sub = micro_df
  for attribute_no in range(0, n_attributes): 
    combinations[combination_no][attribute_no] = bin_indices[attribute_no] #The current attribute for the current combination is given its value 
    micro_df_sub = micro_df_sub.loc[micro_df_sub[sample_attributes[attribute_no]] == sample_bin_names[attribute_no][bin_indices[attribute_no]]] #The df is filtered to remove all rows where the attribute differs from the value given on the row above

  counts[combination_no] = len(micro_df_sub.index) #The rows still remaining in the df are the ones where all the attribute values match the signatuere given in bin_indices.
  bin_indices = inc_bin_indices(bin_indices, 0, sample_bin_names)

#------------ IPF -------------
counts_orig = np.copy(counts)
counter = 0
diff_sum = 1.
while True:
  diff_sum = 0.
  for attribute_no in range(0, n_attributes):
    for bin_no in range(0, len(sample_bin_names[attribute_no])):

      #Sum counts over all combinations that contains the current bin for the current attribute
      sum_over_bin = 0.
      for combination_no in range(0, n_combinations):
        if combinations[combination_no][attribute_no] == bin_no:
          sum_over_bin += counts[combination_no]
      
      #Add the difference between actual and desired marginal distribution value for bin 
      #To total deviation
      diff_sum += abs(sum_over_bin - marginals[attribute_no][bin_no])

      #Update all combinations for the current bin for the current attribute so that the sum over 
      #the bin is identical to the marginal distribution value for this bin
      for combination_no in range(0, n_combinations):
        if combinations[combination_no][attribute_no] == bin_no:
          counts[combination_no] *= marginals[attribute_no][bin_no]/sum_over_bin

  counter +=1
  if diff_sum < 0.01: 
    break

#---------- Print results -------------
print "No of iterations: {0}".format(counter)
print
#print 'Matching of constraints'
#for attribute_no in range(0, n_attributes):
#  for bin_no in range(0, len(sample_bin_names[attribute_no])):
#    sum_over_bin = 0.
#    for combination_no in range(0, n_combinations):
#      if combinations[combination_no][attribute_no] == bin_no:
#        sum_over_bin += counts[combination_no]
#    print "{0}. Calculated: {1}. Constraint: {2}".format(marginal_bin_names[attribute_no][bin_no], sum_over_bin, marginals[attribute_no][bin_no])

ratio = np.zeros(n_combinations)
for ii in range(0, n_combinations):
  ratio[ii] = counts[ii]/counts_orig[ii]

np.set_printoptions(precision=3)
np.set_printoptions(suppress=True)
print 'Results.'
print 'First n_attributes columns are the combinations of bins.'
print 'The third last column is people in the micro sample for each combination.'
print 'The second last column is the value after IPF. The last column is their ratio.'
print np.column_stack((combinations, counts_orig, counts, ratio)) 



#for i0 in range(0, lengths[0]):
#  for i1 in range(0, lengths[1]):
#    for i2 in range(0, lengths[2]):
#      micro[i0][i1][i2] = len(micro_df.loc[(micro_df[attributes[0]] == sexes_s[i0]) & (micro_df[attributes[1]] == ages_s[i1]) & (micro_df[attributes[2]] == races_s[i2])].index)
#
#sexes=sex_df.as_matrix()[0,:]
#ages=age_df.as_matrix()[0,:]
#races=race_df.as_matrix()[0,:]
#
#for i1 in range(0, lengths[0]):
#  micro[i0][i1][i2] 
