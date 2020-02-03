
import pandas as pd
from typing import List
from pandas import DataFrame


class ZeroDiagnosis(object):
    def __init__(self,
                 gravity_data:DataFrame,
                 trade_var_name:str = 'trade_value',
                 imp_var_name:str = 'importer',
                 exp_var_name:str = 'exporter',
                 year_var_name:str = 'year',
                 sector_var_name:str = None):
        '''
        Identify countries that do not have any non-zero trade flows.
        Args:
            gravity_data: (pd.DataFrame) A gravity dataset to analyze.
            trade_var_name: (str) The name of the column containing trade flows.
            imp_var_name: (str) The name of the column containing importer IDs.
            exp_var_name: (str) The name of the column containing exporter IDs.
            year_var_name: (str) The name of the column containing year IDs.
            sector_var_name: (str) The name of the column containing sector IDs.

        Attributes:
            modified_data: (pd.DataFrame) A dataframe in which rows of zeros have been dropped by the methods (if
                specified).

        '''
        self.gravity_data = gravity_data
        self.modified_data = gravity_data
        self.trade_var_name = trade_var_name
        self.imp_var_name = imp_var_name
        self.exp_var_name = exp_var_name
        self.year_var_name = year_var_name
        self.sector_var_name = sector_var_name

    def find_zeros(self, dimensions:List[str], drop_obs:bool = False):
        '''
        Find zeros given the specified dimensions.
        Args:
            dimensions: (List[str]) A list of columns specifying the level at which to check for zero trade. For
                example, ['importer','exporter'] would look for bilateral pairs that never trade and ['importer','year']
                would look for importers that never import in a given year.
            drop_obs: (bool) if true, the identified rows are dropped from the dataframe in self.modified_data.

        Returns: A dataframe reporting cases in which all trade flows are zero.

        '''
        agg_data = self.gravity_data.groupby(dimensions).agg({self.trade_var_name:['min', 'max', 'sum']}).reset_index()
        agg_data.columns = ["_".join(x) for x in agg_data.columns.ravel()]
        [agg_data.rename(columns = {(name+'_'):name}, inplace=True) for name in dimensions]
        non_trading = (agg_data[self.trade_var_name+'_min'] == 0) & (agg_data[self.trade_var_name+'_max'] == 0) & (agg_data[self.trade_var_name+'_sum'] == 0)
        if non_trading.any():
            id_rows = agg_data.loc[non_trading,:]
        else:
            id_rows = 'No zero trade cases for this set of dimensions.'

        if drop_obs:
            if self.modified_data is None:
                modified_data = self.gravity_data.copy()
            if self.modified_data is not None:
                modified_data = self.modified_data.copy()

            drop_df = id_rows[dimensions].copy()
            drop_df['drop'] = 1
            modified_data = modified_data.merge(right = drop_df, how = 'outer', on = dimensions)
            modified_data = modified_data.loc[modified_data['drop']!= 1,:]
            modified_data.drop(['drop'],axis = 1, inplace = True)
            self.modified_data = modified_data.copy()

        return id_rows

    def no_intra_trade(self, drop_obs:bool = False):
        '''
        Find cases in which intra-national trade is always zero.
        Args:
            drop_obs: (bool) if true, the identified rows are dropped from the dataframe in self.modified_data.

        Returns: (pd.DataFrame) A dataframe reporting cases in which all trade flows are zero.

        '''
        non_trading = self.find_zeros([self.imp_var_name, self.exp_var_name])
        no_intra = non_trading.loc[non_trading['importer'] == non_trading['exporter'], :]
        if drop_obs:
            self._drop_obs(no_intra, [self.imp_var_name, self.exp_var_name])
        return no_intra


    def _drop_obs(self, found_zeros, dimensions):
        if self.modified_data is None:
            modified_data = self.gravity_data.copy()
        if self.modified_data is not None:
            modified_data = self.modified_data.copy()

        drop_df = found_zeros[dimensions].copy()
        drop_df['drop'] = 1
        modified_data = modified_data.merge(right=drop_df, how='outer', on=dimensions)
        modified_data = modified_data.loc[modified_data['drop'] != 1, :]
        modified_data.drop(['drop'], axis=1, inplace=True)
        self.modified_data = modified_data.copy()