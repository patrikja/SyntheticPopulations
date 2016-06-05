import pandas as pd
import numpy as np
import random
import sys

#The names of the different attributes. Can be arbitrarily many. Will be used as names for marginal
#distribution files and as headers in micro sample.
attributes = ['attr_a', 'attr_b', 'attr_c']

#The names of the differint bins within an attribute. Can be arbitrarily many for each attribute.
#Will be used in micro sample.
bin_names = [['a0', 'a1'], ['b0', 'b1', 'b2'], ['c0', 'c1', 'c2']]

#The names of the different activitiy types. Can be arbitrarily many. Will be used when generating schedules
activities = ['act0', 'act1', 'act2']

#File names to use when saving
micro_sample_csv = 'micro_sample.csv'
marginal_csvs = map(lambda e: e + '.csv', attributes)

survey_attributes_csv = 'survey_people.csv'
survey_activities_csv = 'survey_activities.csv'
synthetic_people_csv = 'synthetic_population.csv'

n_micro_samples = 500 #Number of agents to use in the micro sample
n_survey_persons = 10 #Number of persons in survey
N_MAX_ACTIVITIES = 4 #Maximum number of activities for a person in a day
POPULATION_SIZE = 100 #Might not be exactly fulfilled due to rounding

n_attributes = len(attributes)
n_activities = len(activities)
bin_lengths = map(lambda e: len(e), bin_names)
n_combinations = np.product(bin_lengths)

def inc_bin_indices(bi_list, ind, bin_names):
  bi_list[ind] += 1
  if bi_list[ind] == len(bin_names[ind]):
    bi_list[ind] = 0
    if ind < n_attributes - 1:
      return inc_bin_indices(bi_list, ind+1, bin_names)
  return bi_list

bin_indices = np.zeros(n_attributes, dtype=np.int)

#Create full population (this is the 'truth')
combinations = np.zeros((n_combinations, n_attributes), dtype=np.int)
counts_frac = np.zeros(n_combinations, dtype=np.float)
for combination_no in range(0, n_combinations):
  for attribute_no in range(0, n_attributes):
    combinations[combination_no][attribute_no] = bin_indices[attribute_no]
  counts_frac[combination_no] = random.random()
  bin_indices = inc_bin_indices(bin_indices, 0, bin_names)

counts = np.zeros(n_combinations, dtype=np.int)
scale_factor = POPULATION_SIZE/np.sum(counts_frac)
for combination_no in range(0, n_combinations):
  counts[combination_no] = int(round(counts_frac[combination_no]*scale_factor))

print 'Full population'
# TODO: bin_indices is [0, 0, 0] at this point => "a0 b0 c0" is printed on each line before the count! Lack of combinations[combination_no]?
for combination_no in range(0, n_combinations):
  for attribute_no in range(0, n_attributes):
    sys.stdout.write(bin_names[attribute_no][bin_indices[attribute_no]] + ' ')
  print '  ' + str(counts[combination_no])

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
  pd.DataFrame([attribute_marginal], columns=bin_names[attribute_no]).to_csv(marginal_csvs[attribute_no], index=False)

#Create micro sample and save as csv
micro_sample = []
for micro_row in range(0, n_micro_samples):
  ran = random.randrange(0, cum_counts[len(cum_counts)-1])
  macro_row = 0
  while ran > cum_counts[macro_row]:
    macro_row += 1
  sample_row = []
  for attribute_no in range(0, n_attributes):
    sample_row.append(bin_names[attribute_no][combinations[macro_row][attribute_no]])
  micro_sample.append(sample_row)
pd.DataFrame(micro_sample, columns=attributes).to_csv(micro_sample_csv, index=False)

#Create 'true' survey with activities and save in two files, one with attributes and one with activities
survey_attributes_df = pd.DataFrame(columns=['person_id', 'household_id']+attributes)
survey_activities_df = pd.DataFrame(columns=['person_id', 'household_id', 'activity_type', 'start_time', 'duration', 'location'])
household_id = 1
for person_id in range(1, n_survey_persons):
  row_attr = pd.DataFrame(columns=['person_id', 'household_id']+attributes)
  row_attr.set_value(0, 'person_id', person_id)
  row_attr.set_value(0, 'household_id', household_id)
  for attribute_no in range(0, n_attributes):
    row_attr.set_value(0, attributes[attribute_no], bin_names[attribute_no][random.randrange(0, bin_lengths[attribute_no])])
  survey_attributes_df = survey_attributes_df.append(row_attr)

  row_act = pd.DataFrame(columns=['person_id', 'household_id', 'activity_type', 'start_time', 'duration', 'location'])
  start_time = 0
  for activity_no in range(0, random.randrange(1, N_MAX_ACTIVITIES + 1)):
    activity_type = activities[random.randrange(0, n_activities)]
    duration = random.randrange(10, 1000) #TODO: Add coorelation between duration and attributes
    row_act.set_value(0, 'person_id', person_id)
    row_act.set_value(0, 'household_id', household_id)
    row_act.set_value(0, 'activity_type', activity_type)
    row_act.set_value(0, 'start_time', start_time)
    row_act.set_value(0, 'duration', duration)
    row_act.set_value(0, 'location', 0)
    start_time += duration
    survey_activities_df = survey_activities_df.append(row_act)
  if random.random() < 0.6: household_id += 1

print
print 'Schedules'
print survey_activities_df.to_string(index=False)

survey_attributes_df.to_csv(survey_attributes_csv, index=False)
survey_activities_df.to_csv(survey_activities_csv, index=False)
