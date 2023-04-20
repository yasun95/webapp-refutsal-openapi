import pandas as pd

class DropDuplicateGoalTag:
    def __init__(self):
        self.df = pd.DataFrame()
        self.df1 = pd.DataFrame()
        self.df2 = pd.DataFrame()
        self.df3 = pd.DataFrame()
        self.df4 = pd.DataFrame()
        self.merged_df = pd.DataFrame()
        self.drop_duplicates_df = pd.DataFrame()

    def readCsv(self, file1, file2, file3, file4):
        self.df1 = pd.read_csv(file1)
        self.df2 = pd.read_csv(file2)
        self.df3 = pd.read_csv(file3)
        self.df4 = pd.read_csv(file4)

    def MergeCsv(self):
        self.merged_df = pd.merge(self.df1, self.df2, how='outer')
        self.merged_df = pd.merge(self.merged_df, self.df3, how='outer')
        self.merged_df = pd.merge(self.merged_df, self.df4, how='outer')

        self.drop_duplicates_df = self.merged_df.drop_duplicates(subset=['min', 'sec'])

        return self.drop_duplicates_df

    def SaveCsv(self):
        self.df = self.MergeCsv()
        self.df.to_csv('goal_tag.csv', index=False)
