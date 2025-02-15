
import pandas as pd
from constants import SAMPLE_CASES

class Database:
    def __init__(self):
        pass

    def generate_samples(self):
        cases_df = pd.DataFrame(SAMPLE_CASES)

        return cases_df


