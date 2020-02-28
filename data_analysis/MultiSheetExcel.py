__Author__ = "Peter Herman"
__Project__ = "Economic Analysis Tools"
__Created__ = "February 28, 2020"
__Description__ = '''A class for creating and writing multi-sheet excel files.'''

# ToDo: Add LaTeX support for output.

from pandas import DataFrame, ExcelWriter


class MultiSheetExcel():
	def __init__(self):
		'''
		A class for creating multi sheet excel files. Add sheets using obj.add_sheet() and write to disk
		with obj.write()
		'''
		self.sheet_list = list()
		self.contents = None

	def add_sheet(self, dataframe, sheet_name: str = None, description: str = '', note: str = None):
		'''
		Add a sheet to the excel file.
		:param dataframe: (pandas.DataFrame) The dataframe to be written on the new sheet.
		:param sheet_name: (str) Name for the sheet.
		:param description: (str) An optional descritption for the sheet to be included on a table of contents.
		:param note: (str) An optional note to add to the bottom of the table (first column, last row)
		:return: None
		'''
		if sheet_name:
			dataframe = self._add_note(dataframe, 'Sheet', sheet_name)
		if description:
			dataframe = self._add_note(dataframe,'Description',description)
		if note:
			dataframe = self._add_note(dataframe, 'Note', note)
		if not sheet_name:
			sheet_name = 'unnamed_{}'.format(len(self.sheet_list) + 1)
		self.sheet_list.append({'table': dataframe, 'sheet_name': sheet_name, 'description': description})

	def _add_note(self, df, type, note):
		note_row = DataFrame(df.iloc[0, :].copy()).transpose()
		note_row.index = ['{}:'.format(type)]
		note_row.loc[:, :] = ''
		note_row.iloc[0, 0] = note
		return df.append(note_row)

	def write(self, path, table_of_contents: bool = True):
		'''
		Write the multisheet excel
		:param path: (str) file path to write excel 'xlsx' file.
		:param table_of_contents: (bool) If true, the file will include a table of contents on the first sheet of that
		lists the different sheets and any descriptions that were provided.
		:return: None
		'''
		if not path.endswith('xlsx'):
			path = path + '.xlsx'
		if table_of_contents:
			sheet_names = list()
			descriptions = list()
			for number, item in enumerate(self.sheet_list):
				sheet_names.append(item['sheet_name'])
				descriptions.append(item['description'])
			title_sheet = DataFrame({'Sheet #': list(range(1, len(sheet_names) + 1)),
									 'Contents': sheet_names,
									 'Description': descriptions})

			with ExcelWriter(path) as writer:
				number = 0
				if table_of_contents:
					title_sheet.to_excel(writer, sheet_name='Contents', index=False)
				for item in self.sheet_list:
					number = number + 1
					item['table'].to_excel(writer, sheet_name=('{}. {}'.format(number, item['sheet_name'][0:26])))
