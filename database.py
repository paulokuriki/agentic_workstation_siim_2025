import pandas as pd

class Database:
    def __init__(self):
        pass

    def generate_samples(self, num_samples = 3):
        cases_data = {
            'Patient ID': [f'**Patient ID:** {1000 + i}' for i in range(1, num_samples + 1)],
            'Action': ['Select' for _ in range(num_samples)]
        }
        cases_df = pd.DataFrame(cases_data)

        return cases_df
