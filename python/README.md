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
| baseline_synthetic_population.py  | Generates synthetic_population.csv |
| activity_assignment.py            | Generates synthetic_activities.csv |
| generate_input_data_files.py      | Generates attr_a.csv attr_b.csv attr_c.csv micro_sample.csv |
| common.py                         | Some helpers imported by the other scripts |
| ipfNd.py                          | Alternative algorithm for iterative proportional fitting  |
