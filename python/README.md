# Dependencies

python
numpy
pandas
statsmodels

* Ubuntu: Install with

```shell
sudo pip install numpy
sudo pip install pandas
sudo pip install statsmodels
```

or

```shell
sudo apt-get install python-numpy python-pandas python-statsmodels
```

# Contents

| File | Comment
| --------------------------------- | ------------------ |
| README.md                         | This file          |
| Makefile                          | Build dependencies |
| TODO.org                          | |
| baseline_synthetic_population.py  | Generates synthetic_people.csv |
| activity_assignment.py            | Generates synthetic_activities.csv |
| generate_input_data_files.py      | Generates attr_a.csv attr_b.csv attr_c.csv micro_sample.csv |
| common.py                         | Some helpers imported by the other scripts |
| ipfNd.py                          | Alternative algorithm for iterative proportional fitting  |

## Notes

Variable and file naming:
* before:
    * common.py, activity_assignment.py: survey_attributes_csv = 'survey_people.csv'
    * common.py, activity_assignment.py: synthetic_people_csv  = 'synthetic_population.csv'
* after:
    * common.py, activity_assignment.py: survey_attributes_csv = 'survey_attributes.csv'
    * common.py, activity_assignment.py: synthetic_people_csv  = 'synthetic_people.csv'
