import numpy as np
import pandas as pd
import statsmodels.formula.api as sm
import copy

BIG_FLOAT = float(Infinity)

# The following must be identical to the corresponding values in the genertion
# script (if the files produced there are to be used).
survey_attributes_csv    = 'survey_people.csv'
survey_activities_csv    = 'survey_activities.csv'
synthetic_people_csv     = 'synthetic_population.csv' # TODO avoid different file name and variable name pattern (pick people or population)
synthetic_activities_csv = 'synthetic_activities.csv'
attribute_names = ['attr_a', 'attr_b', 'attr_c']
activity_names  = ['act0', 'act1', 'act2']
bin_names       = [['a0','a1', 'a2'], ['b0', 'b1', 'b2'], ['c0', 'c1', 'c2']]

bin_names_flat =[val for sublist in bin_names for val in sublist[1:]]

n_attribute_names = len(attribute_names)
n_activity_names  = len(activity_names)
n_bins = map(lambda e: len(e), bin_names)
n_bin_names_flat = len(bin_names_flat)


class Activity:
  def __init__(self, name, starttime, duration, location_id):
    self.name = name
    self.starttime = starttime
    self.duration = duration
    self.location_id = location_id

  def __repr__(self):
    return self.name
    #return 'Activity name: {0}. Start time: {1}. Duration: {2}.'.format(self.name, self.starttime, self.duration)

class Person:
  def __init__(self, person_id, household_id, attributes, activities):
    self.person_id = person_id
    self.household_id = household_id #household this person belongs to
    self.attributes = attributes #list with the bin value for each attribute

    # Array with ones ond zeros where all bin values, exept the first, for
    # all attributes are represented. One means that that bin value is the
    # matching one for this person. If there are only zeros for an attribute
    # it means that the first bin value is used.
    # Example: [a0, b1, c2] transforms to [0, 0, 1, 0, 0, 1]:
    #  a1  a2  b1  b2  c1  c2
    # [0,  0,  1,  0,  0,  1]
    self.bins = np.zeros(n_bin_names_flat, dtype=np.int)
    for attribute in attributes:
      if attribute in bin_names_flat:
        self.bins[bin_names_flat.index(attribute)] = 1

    self.activities = activities
    #Sum total time for each activity
    self.survey_activity_times = np.zeros(n_activity_names, dtype=np.int)
    for activity in activities:
      self.survey_activity_times[activity_names.index(activity.name)] += activity.duration

  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self.person_id == other.person_id
    else:
      return False

  def __ne__(self, other):
    return not self.__eq__(other)

  def __repr__(self):
    return 'Person id: {0}. Household id: {1}. Attributes: {2}. Activities: {3}'\
.format(self.person_id, self.household_id, self.attributes, self.activities)

  # Fitted activity time is y = x*b, where y is a vector of times for different
  # categories, x is a vector of ones and zeros, representing the presence of
  # attributes (a 1 is added for the interception) and b is a matrix with the
  # linear coefficients.
  def assign_fitted_time(self, beta):
    self.fitted_activity_times = np.matmul(beta, np.hstack((1, self.bins)))

  # Calculate the distance between two persons as the (Euclidian) distance
  # between their fitted activity time vectors.
  # TODO: Replace with Mahalanobis distance instead of Euclidian
  def distance(self, other_person):
    return np.linalg.norm(        self.fitted_activity_times -
                          other_person.fitted_activity_times)

class Household:
  def __init__(self, household_id):
    self.household_id = household_id
    self.persons = []

  def __eq__(self, other):
    if isinstance(other, self.__class__):
      return self.household_id == other.household_id
    else:
      return False

  def __ne__(self, other):
    return not self.__eq__(other)

  def addPerson(self, person):
    self.persons.append(person)

  # The houshold-houshold distance is defined as follows:
  # For every person in one of the households, take the smallest distance
  #   between it and any person in the other household.
  # The household distance is the biggest of the person-person distances
  #   for all persons in the household.
  def distance(self, other_household):
    max_person_dist = 0
    for my_person in self.persons:
      min_person_dist = BIG_FLOAT
      for other_person in other_household.persons:
        min_person_dist = min(min_person_dist, my_person.distance(other_person))
      max_person_dist = max(max_person_dist, min_person_dist)
    return max_person_dist



#print pd.merge(pd.read_csv(survey_attributes_csv), pd.read_csv(survey_activities_csv), left_on='person_id', right_on='person_id')

# Read survey files and construct list of survey persons
survey_attributes_df = pd.read_csv(survey_attributes_csv)
survey_activities_df = pd.read_csv(survey_activities_csv)

# Add dummy row to be able to use while construction below
empty_row = pd.DataFrame(columns=survey_activities_df.columns.values.squeeze().tolist())
empty_row.set_value(len(survey_activities_df), 'person_id', -1)
empty_row.set_value(len(survey_activities_df), 'household_id', -1)
empty_row.set_value(len(survey_activities_df), 'activity_type', '')
empty_row.set_value(len(survey_activities_df), 'start_time', 0)
empty_row.set_value(len(survey_activities_df), 'duration', 0)
empty_row.set_value(len(survey_activities_df), 'location', 0)
survey_activities_df = survey_activities_df.append(empty_row)


survey_persons = []
activities = []
activity_row_no = 0
for index, attribute_row in survey_attributes_df.iterrows():
  while survey_activities_df['person_id'].iloc[activity_row_no] < attribute_row['person_id']:  activity_row_no += 1
  activities = []
  while survey_activities_df['person_id'].iloc[activity_row_no] == attribute_row['person_id']:
    activities.append(Activity(survey_activities_df['activity_type'].iloc[activity_row_no],
                               survey_activities_df['start_time'].iloc[activity_row_no],
                               survey_activities_df['duration'].iloc[activity_row_no],
                               survey_activities_df['location'].iloc[activity_row_no]))
    activity_row_no += 1

  attributes = map(lambda a: attribute_row[a], attribute_names)
  survey_persons.append(Person(attribute_row['person_id'],
                               attribute_row['household_id'],
                               attributes,
                               activities))

# Create list of survey households and associate survey persons with them
survey_households = []
for person in survey_persons:
  hh_temp = Household(person.household_id)
  if not hh_temp in survey_households:
    survey_households.append(hh_temp)
for person in survey_persons:
  survey_households[survey_households.index(Household(person.household_id))].addPerson(person)


# Read synthetic people file and construct list of synthetic persons. They have no activities.
synthetic_people_df = pd.read_csv(synthetic_people_csv)
synthetic_persons = []
for index, row in synthetic_people_df.iterrows():
  attributes = map(lambda a: row[a], attribute_names)
  synthetic_persons.append(Person(row['person_id'], row['household_id'], map(lambda a: row[a], attribute_names), []))

# Create list of synthetic households and associate synthetic persons with them
synthetic_households = []
for person in synthetic_persons:
  hh_temp = Household(person.household_id)
  if not hh_temp in synthetic_households:
    synthetic_households.append(hh_temp)
for person in synthetic_persons:
  synthetic_households[synthetic_households.index(Household(person.household_id))].addPerson(person)

# Create a dataframe with activity times and attributes. The attributes are
# represented as dummy variables by the vector of zeros and ones created above.
act_df = pd.DataFrame(columns=activity_names+bin_names_flat)
for person in survey_persons:
  row = pd.DataFrame(columns=activity_names+bin_names_flat)
  for activity_id in range(0, n_activity_names):
    row.set_value(person.person_id, activity_names[activity_id], person.survey_activity_times[activity_id])
  for bin_no in range(0, n_bin_names_flat):
    row.set_value(person.person_id, bin_names_flat[bin_no], person.bins[bin_no])
  act_df = act_df.append(row)
# TODO: This is needed to make the output of the fitting nice. WHY???
act_df=act_df.fillna(0)

# For each activity time, fit it as a function of the attributes.
beta = np.zeros((n_activity_names, n_bin_names_flat+1), dtype=float)
beta_row = 0
for activity in activity_names:
  formula_str = activity + ' ~ '
  for bin_name in bin_names_flat:
    formula_str += bin_name + ' + '
  formula_str = formula_str[0:-3]
  # TODO: What is ols and is it good enough?
  result = sm.ols(formula=formula_str, data=act_df).fit()
  beta[beta_row][:] = result.params
  beta_row += 1


# Assign fitted times to survey persons and synthetic persons
for person in survey_persons:
  person.assign_fitted_time(beta)
for person in synthetic_persons:
  person.assign_fitted_time(beta)

# For each synthetic household, find the survey household that it is closest to.
# Then, for each synthetic person in the synthetic household, find the survey
# person in the selected survey household that it is closest to and copy the
# survey person's schedule to the synthetic person
for synthetic_household in synthetic_households:
  min_household_dist = BIG_FLOAT
  closest_survey_household = Household(0)
  for survey_household in survey_households:
    if synthetic_household.distance(survey_household) < min_household_dist:
      min_household_dist = synthetic_household.distance(survey_household)
      closest_survey_household = survey_household
  for synthetic_person in synthetic_household.persons:
    min_person_dist =  BIG_FLOAT
    closest_survey_person = Person(0, 0, [], [])
    for survey_person in closest_survey_household.persons:
      if synthetic_person.distance(survey_person) < min_person_dist:
        min_person_dist = synthetic_person.distance(survey_person)
        closest_survey_person = survey_person
    synthetic_person.activities = copy.deepcopy(closest_survey_person.activities)

#for person in survey_persons:
#  print person
#for person in synthetic_persons:
#  print person

# Create dataframe with schedules for synthetic persons and write to file.
synthetic_activities_df = pd.DataFrame(columns=['person_id',
                                                'household_id',
                                                'activity_type',
                                                'start_time',
                                                'duration',
                                                'location'])
for person in synthetic_persons:
  for activity in person.activities:
    row = pd.DataFrame(columns=['person_id', 'household_id', 'activity_type',
                                'start_time', 'duration', 'location'])
    row.set_value(0, 'person_id', person.person_id)
    row.set_value(0, 'household_id', person.household_id)
    row.set_value(0, 'activity_type', activity.name)
    row.set_value(0, 'start_time', activity.starttime)
    row.set_value(0, 'duration', activity.duration)
    row.set_value(0, 'location', activity.location_id)
    synthetic_activities_df = synthetic_activities_df.append(row)
synthetic_activities_df.to_csv(synthetic_activities_csv, index=False)
