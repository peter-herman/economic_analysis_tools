__Author__ = "Peter Herman"
__Project__ = "misc_tools"
__Created__ = "August 06, 2019"

import pandas as pd

def TeXTable(dataframe: pd.DataFrame = None,
             csv_input: str = None,
             save_path: str = None,
             round_value: int = None):
    '''
    Convert table to latex format.
    :param dataframe: pd.DataFrame (optional) a Pandas DataFrame to convert to TeX formatting
    :param csv_input: str (optional) a path to a csv containing a table to be converted to TeX formatting
    :param save_path: str (optional) A path and filename to save the TeX table to.
    :param round_value: int (optional) Number of decimal places to round results to.
    :return: pd.DataFrame of TeX formatted strings.

    Example:
    > TeXTable(csv_input = "other/test_table.csv", round_value = 2)
    '''

    # Check for table input type
    if dataframe is None:
        if csv_input is None:
            raise ValueError("Must supply a dataframe or a csv_input.")
        dataframe = pd.read_csv(csv_input, dtype = str)

    # Replace stars with latex syntax (e.g. *** -> ^{***})
    latex = dataframe.copy()
    col_list = dataframe.columns
    for col in range(dataframe.shape[1]):
        latex.iloc[:,col] = dataframe.iloc[:,col].str.replace('\*\*\*$', '^{***}', regex=True)
    dataframe_2 = latex.copy()
    for col in range(dataframe.shape[1]):
        latex.iloc[:,col] = dataframe_2.iloc[:,col].str.replace('\*\*$', '^{**}', regex=True)
    dataframe_3 = latex.copy()
    for col in range(dataframe.shape[1]):
        latex.iloc[:,col] = dataframe_3.iloc[:,col].str.replace('\*$', '^{*}', regex=True)
    dataframe = latex

    # round values
    if round_value is not None:
        st_format = '{:.' + str(round_value) + 'f}'
        for row in range(dataframe.shape[0]):
            for column in range(dataframe.shape[1]):
                cell = dataframe.iloc[row,column]
                try:
                    rfmt = float(cell)
                    dataframe.iloc[row, column] = st_format.format(rfmt)
                except:
                    # Round values ending in specific characters
                    for end_str in ['^{***}', '^{**}', '^{*}']:
                        if cell.endswith(end_str):
                            rfmt = float(cell.rstrip(end_str))
                            rfmt = st_format.format(rfmt)
                            dataframe.iloc[row, column] = rfmt + end_str
                    # Round values beginning and ending in specific characters
                    for beg_end in [('(', ')')]:
                        if cell.startswith(beg_end[0]) and cell.endswith(beg_end[1]):
                            print(cell)
                            rfmt = float(cell.lstrip(beg_end[0]).rstrip(beg_end[1]))
                            rfmt = st_format.format(rfmt)
                            dataframe.iloc[row, column] = beg_end[0] + rfmt + beg_end[1]

    # Write out if specified
    if save_path is not None:
        dataframe.to_csv(save_path, index = False, sep='&', line_terminator='\\\\\n')

    return dataframe





