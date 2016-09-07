import pandas as pd
import numpy as np
import random
from common import *


MICRO_SAMPLE_SIZE  = 500 # Number of agents to use in the micro sample
N_SURVEY_PERSONS =  10 # Number of persons in survey
N_MAX_ACTIVITIES =   4 # Maximum number of activities for a person in a day
POPULATION_SIZE  = 10000 # Might not be exactly fulfilled due to rounding



# (int, int) -> int[]
# Takes two ints n_combinations and total_size and generates a random
# vector of n_combinations ints that sums to total_size.
# Note that in this implementation the sum might not be exactly total_size
# due to rounding errors.
def counts_from_random(n_combinations, total_size):
  counts_frac = np.random.random(n_combinations);
  scale_factor = total_size/counts_frac.sum();
  counts = np.array([int(round(x*scale_factor)) for x in counts_frac]);
  return counts


#(int[][], int[]) -> string
#Transform a matrix with combinations and a vector with counts to a
#good looking printable string, using the names of the bins.
#TODO: Alignment
def combinations_with_counts_to_string(combinations, counts):
  out_string = 'Full population\n'
  for combination_no in range(0, combinations.shape[0]):
    for attribute_no in range(0, combinations.shape[1]):
      bin_no = combinations[combination_no][attribute_no]
      out_string += bin_number_to_name(attribute_no, bin_no) + ' '
    out_string += '  ' + str(counts[combination_no]) + '\n'
  return out_string


#(int, int, int[][], int[]) -> int[]
#Creates a marginal distribution with n_bins bins for attribute attribute_no
#from the population descriped by combinations and counts
def aggregate_marginal_distribution(attribute_no, n_bins, combinations, counts):
  marginal = np.zeros(n_bins, dtype=np.int)
  for bin_no in range(0, n_bins):
    sum_over_bin = 0
    for combination_no in range(0, combinations.shape[0]):
      if combinations[combination_no][attribute_no] == bin_no:
        sum_over_bin += counts[combination_no]
    marginal[bin_no] = sum_over_bin
  return marginal


#(int, int[][], int[], string[][]) -> string[][]
#Takes the population described by combinations and counts
#and returns a micro_sample with n_rows individuals based on the
#sampled from the distribution given by counts
def create_micro_sample(n_rows, combinations, counts):
  cum_counts = np.cumsum(counts)
  micro_sample = []
  for micro_row in range(0, n_rows):
    ran = random.randrange(0, cum_counts[len(cum_counts)-1])
    macro_row = 0
    while ran > cum_counts[macro_row]:
      macro_row += 1
    sample_row = []
    for attribute_no in range(0, combinations.shape[1]):
      bin_no = combinations[macro_row][attribute_no]
      sample_row.append(bin_number_to_name(attribute_no, bin_no))
    micro_sample.append(sample_row)
  return micro_sample


#(int, int) -> data_frame
#Creates a data_frame with one row, containing person_id, houshold_id and
#values for all attributes. For each attribute in attributes a random value
#is chosen from bin_names randomly.
def create_attribute_row(person_id, household_id):
  row_attr = pd.DataFrame(columns=['person_id', 'household_id'] + attributes)
  row_attr.set_value(0, 'person_id', person_id)
  row_attr.set_value(0, 'household_id', household_id)
  for attribute_no in range(0, len(attributes)):
    row_attr.set_value(0, attributes[attribute_no],
                       bin_number_to_name(attribute_no, random.randrange(0, bin_lengths[attribute_no])))

  return row_attr


#(int, int, string, int, int, int) -> data_frame
#Creates a data_frame with one row, containing person_id, houshold_id and
#information about a certain activity.
def create_activity_row(person_id, household_id, activity_type, start_time, duration, location):
    # TODO: Add correlation between duration and attributes
    row_act = pd.DataFrame(columns=['person_id', 'household_id', 'activity_type',
                                    'start_time', 'duration', 'location'])
    row_act.set_value(0, 'person_id',     person_id)
    row_act.set_value(0, 'household_id',  household_id)
    row_act.set_value(0, 'activity_type', activity_type)
    row_act.set_value(0, 'start_time',    start_time)
    row_act.set_value(0, 'duration',      duration)
    row_act.set_value(0, 'location',      0)
    return row_act


# Create full population (this is the 'truth')
combinations = define_combinations(bin_lengths)
counts = counts_from_random(combinations.shape[0], POPULATION_SIZE)
print combinations_with_counts_to_string(combinations, counts)

#Write the marginal distribution for each attribute to a csv file
for attribute_no in range(0, len(attributes)):
  attribute_df = pd.DataFrame(aggregate_marginal_distribution(attribute_no, bin_lengths[attribute_no], combinations, counts)).transpose()
  attribute_df.columns = bin_names[attribute_no]
  attribute_df.to_csv(marginal_csvs[attribute_no], index=False)

#Sample micro sample and write to a cvs file
pd.DataFrame(create_micro_sample(MICRO_SAMPLE_SIZE, combinations, counts), columns=attributes).to_csv(micro_sample_csv, index=False)


# Create 'true' survey with activities and save in two files, one with
#   attributes and one with activities.
survey_attributes_df = pd.DataFrame(columns=['person_id', 'household_id'] + attributes)
survey_activities_df = pd.DataFrame(columns=['person_id', 'household_id',
                                             'activity_type', 'start_time',
                                             'duration', 'location'])
household_id = 1
for person_id in range(1, N_SURVEY_PERSONS):

  survey_attributes_df = survey_attributes_df.append(create_attribute_row(person_id, household_id))

  start_time = 0
  for activity_no in range(0, random.randrange(1, N_MAX_ACTIVITIES + 1)):
    activity_type = activities[random.randrange(0, len(activities))] #Pick an activity at random.
    duration = random.randrange(10, 1000) #Take a random duration.
    survey_activities_df = survey_activities_df.append(create_activity_row(person_id, household_id, activity_type, start_time, duration, 0))
    start_time += duration #The start time of the next activity is one duration later.
  if random.random() < 0.6: household_id += 1

print
print 'Schedules'
print survey_activities_df.to_string(index=False)

survey_attributes_df.to_csv(survey_attributes_csv, index=False)
survey_activities_df.to_csv(survey_activities_csv, index=False)
