import pandas as pd

class ExceptionReport:
    def __init__(self, path):
        self.path = path

        self.df = pd.read_csv(path)
        print(self.df)


