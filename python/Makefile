synpop: attr_a.csv attr_b.csv attr_c.csv micro_sample.csv
	python baseline_synthetic_population.py
#Generates synthetic_population.csv

activity: survey_people.csv survey_activities.csv synthetic_population.csv
	python activity_assignment.py 
#Generates synthetic_activities.csv

data:
	python generate_input_data_files.py
# generates attr_a.csv attr_b.csv attr_c.csv micro_sample.csv
