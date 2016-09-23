synthetic_people.csv: attr_a.csv attr_b.csv attr_c.csv micro_sample.csv
	python baseline_synthetic_population.py
# Generates synthetic_people.csv

synthetic_activities.csv: survey_attributes.csv survey_activities.csv synthetic_people.csv
	python activity_assignment.py
# Generates synthetic_activities.csv

attr_a.csv attr_b.csv attr_c.csv micro_sample.csv: generate_input_data_files.py
	python generate_input_data_files.py
# Generates attr_a.csv attr_b.csv attr_c.csv micro_sample.csv

clean:
	-rm attr_a.csv attr_b.csv attr_c.csv micro_sample.csv
