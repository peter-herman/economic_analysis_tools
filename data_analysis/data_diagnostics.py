__All__ = ['check_merge', 'missing_data_subset', 'importer_exporter_year_subset', 'CompareIdentifiers']
__Author__ = "Peter Herman"
__Project__ = "gravity data comparisons"
__Created__ = ["01/30/2018" \
               "11/28/2018 -  CompareCountryCodes() added"]

import pandas as pd
import numpy as np

'''
dataset = estimation_data_dynamic
year_var_name = 'year'
year_list = [1989, 1990]
'''


def check_merge(dataset_a,
                dataset_b,
                merge_dimensions_a: list = [],
                merge_dimensions_b: list = []):
    '''
    A function to check the quality of a merge and return a dataset of unmatched observations (similar to stata _merge = 1 or 2). Also prints a summary of the missing, unmerged values.
    :param dataset_a: (Pandas DataFrame) Fist of the merging datasets
    :param dataset_b: (Pandas DataFrame) Second of the merging datasets.
    :param merge_dimensions_a: (list of str's) A list containing the column names (str) upon which to merge in dataset_a
    :param merge_dimensions_b: (list of str's) A list containing the column names (str) upon which to merge in dataset_b
    :return: A dataset of unmatched rows in either or both datasets.
    '''
    merged_data = dataset_a.merge(right=dataset_b, how='outer', left_on=merge_dimensions_a, right_on=merge_dimensions_b)
    missing_observations = merged_data.isnull().sum()
    print(missing_observations)
    unmerged = merged_data[merged_data.isnull().any(axis=1)]
    return unmerged




def missing_data_subset(dataset):
    '''
    Creates a dataset consisting of the rows exhibiting at least one missing value
    :param dataset: (Pandas DataFrame) A dataset to locate missing values in.
    :return: A dataset containing only rows featuring a missing value.
    '''
    return dataset[dataset.isnull().any(axis=1)]


def importer_exporter_year_subset(dataset,
                                  importer_var_name: str = 'importer',
                                  exporter_var_name: str = 'exporter',
                                  year_var_name: str = 'year',
                                  importer_list: list = [],
                                  exporter_list: list = [],
                                  year_list: list = []):
    # add checks for typing with year as it could be str or int
    data_subset = dataset
    if len(importer_list) > 0:
        data_subset = data_subset.loc[data_subset[importer_var_name].isin(importer_list)]
    if len(exporter_list) > 0:
        data_subset = data_subset.loc[data_subset[exporter_var_name].isin(exporter_list)]
    if len(year_list) > 0:
        data_subset = data_subset.loc[data_subset[year_var_name].isin(year_list)]
    return data_subset



'''
dataframe_a = itpd_pare
dataframe_b = pta_unique
code_columns_a = ['exporter','importer']
code_columns_b = ['iso1', 'iso2']
'''

class CompareIdentifiers(object):
    def __init__(self,
                 dataframe_a = None,
                 dataframe_b = None,
                 code_columns_a = [],
                 code_columns_b = []):
        '''
        A class that compares the identifiers in two datasets to help diagnose merge quality

        Args:
            dataframe_a: (Pandas DataFrame)
                A dataframe containing one set of identifiers
            dataframe_b: (Pandas DataFrame)
                A dataframe containing another set of identifiers
            code_columns_a: (List[str])
                A list of a column name or names containing identifiers (identifiers in multiple columns are combined)
            code_columns_b: (List[str])
                A list of a column name or names containing identifiers (identifiers in multiple columns are combined)

        Attributes:
            codes_a: (List[str])
                A list of identifier codes in dataframe_a
            codes_b: (List[str])
                A list of identifier codes in dataframe_b
            a_not_in_: (List[str])
                A list of identifier codes in dataframe_a but not in dataframe_b
            b_not_in_: (List[str])
                A list of identifier codes in dataframe_b but not in dataframe_a
            in_both: (List[str])
                A list of identifier codes in both dataframe_a and dataframe_b (i.e. the intersection)
            in_either: (List[str])
                A list of identifier codes in either dataframe_a and dataframe_b (i.e. the union)
            code_merge: (Pandas DataFrame)
                A DataFrame with the codes from both matched together
            unmatched_a: (Pandas DataFrame)
                Codes in a that are not matched with b (i.e. codes_b is nan)
            unmatched_b: (Pandas DataFrame)
                Codes in b that are not matched with a (i.e. codes_a is nan)
            unmatched: (Pandas DataFrame)
                All codes in both dataframes that are unmatched

        Methods:
            summary(self):
                Prints basic summary information
        '''
        codes_a = set()
        for col in code_columns_a:
            temp = dataframe_a[col].unique().tolist()
            codes_a = codes_a.union(set(temp))

        self.codes_a = list(codes_a)

        codes_b = set()
        for col in code_columns_b:
            temp = dataframe_b[col].unique().tolist()
            codes_b = codes_b.union(set(temp))

        self.codes_b = list(codes_b)

        self.a_not_in_b = list(codes_a - codes_b)
        self.b_not_in_a = list(codes_b - codes_a)
        self.in_both = list(codes_a.intersection(codes_b))
        self.in_either = list(codes_a.union(codes_b))

        merge_a = pd.DataFrame(list(codes_a), columns = ['code_a'])

        merge_b = pd.DataFrame(list(codes_b), columns = ['code_b'])


        self.code_merge = merge_a.merge(merge_b, how = 'outer', left_on = ['code_a'], right_on=['code_b'])
        self.unmatched_a = self.code_merge.loc[self.code_merge['code_b'].isnull(),:]
        self.unmatched_b = self.code_merge.loc[self.code_merge['code_a'].isnull(), :]
        self.unmatched = pd.concat([self.unmatched_a, self.unmatched_b])

        self._summary_text = [("Number of 'a' codes: " + str(len(self.codes_a))),
                             ("Number of 'b' codes: " + str(len(self.codes_b))),
                             ("Number of codes in both: " + str(len(self.in_both))),
                             ("Number of codes in 'a' but not 'b': " + str(len(self.a_not_in_b))),
                             ("Number of codes in 'b' but not 'a': " + str(len(self.b_not_in_a)))]
        for text in self._summary_text:
            print(text)

    def summary(self):
        for text in self._summary_text:
            print(text)
        return None

