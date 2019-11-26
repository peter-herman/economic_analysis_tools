__Author__ = "Peter Herman"
__Project__ = "used_vehicles"
__Created__ = "November 12, 2019"
__Description__ = ''' '''

import pandas as pd
from pandas import DataFrame
from typing import List

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
        if not isinstance(code_columns_a, list):
            code_columns_a = [code_columns_a]
        if not isinstance(code_columns_b, list):
            code_columns_b = [code_columns_b]

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

    def __repr__(self):
        strg = self._summary_text
        return "{} \n"\
               "{} \n"\
               "{} \n"\
               "{} \n"\
               "{} ".format(strg[0],strg[1],strg[2],strg[3],strg[4])



class DataDistribution(object):
    def __init__(self,
                 data:DataFrame = None,
                 exclude_columns:List[str] = None,
                 include_columns:List[str] = None,
                 percentiles:List[float] = None):
        '''
        A class to provide distribution information about each code in each column. For each column, a table of counts
        and string length is generated for each value in the column. It can also output to an excel workbook.
        Args:
            data: (pd.DataFrame)
                A dataframe to analyze the distributions of.
            exclude_columns: (List[str])
                (optional) A list of columns to exclude from the distribution analysis. E.g. continuous, non-repeating
                values with uninformative distributions.
            include_columns: (List[str])
                (optional) A list of columns to include in the distribution analysis. The default is to include all
                columns.
        Attributes:
            columns: (list)
                A list of columns with distributional info.
            distributions: (Dict[DataFrame])
                A dictionary keyed by the column names that contains each columns' distribution info as a DataFrame.
            values: (Dict[list])
                A dictionary keyed by column names containing lists of the unique values in each respective column.
        Methods:
            to_excel(self, path)
                Args:
                    path: (str)
                        A location and filename at which to create a excel workbook in which each distrobution is stored
                        on a sheet. The path should terminate in an ".xlsx" extension.
        Exmaples:
        >>> test_data = pd.DataFrame({'Name':['Ted', 'Ted', 'Nancy'], 'Age':[35, 32, 12]})
        >>> test_dd = DataDistribution(data=test_data)
        >>> print(test_dd.distributions['Name'])
        >>> test_dd.to_excel('P:\Desktop\\test_distrobution.xlsx')
        '''

        self._data = data.copy()

        if include_columns:
            using_columns = include_columns
        else:
            if not exclude_columns:
                using_columns = data.columns.tolist()
            else:
                using_columns = [col for col in data.columns.tolist() if col not in exclude_columns]

        self.columns = using_columns
        self.distributions = dict()
        self.values = dict()

        if percentiles is not None:
            self._percentiles = percentiles
        else:
            self._percentiles = [round(x*0.1,1) for x in range(0,11)]

        self.description = self._data.describe(percentiles = self._percentiles)

        for col in self.columns:
            self._data[col] = self._data[col].astype(str)
            self.distributions[col], self.values[col] = self._get_distribution(col)

    def _get_distribution(self,
                          column):
        temp_data = self._data[[column]].copy()
        temp_data['count'] = 1
        temp_data = temp_data.groupby([column]).agg('sum').reset_index()
        temp_data['string_length'] = temp_data[column].str.len()
        temp_data.sort_values(by = [column], ascending=False)
        codes = temp_data[column].to_list()


        return temp_data, codes

    def to_excel(self, path:str):
        writer = pd.ExcelWriter(path, engine='xlsxwriter')
        self.description.to_excel(writer, sheet_name = 'Distibutions', index = True)
        for column in self.distributions.keys():
            self.distributions[column].to_excel(writer, sheet_name = column, index = False)

        writer.save()
