import csv
import re
import sys
import os
from collections import OrderedDict

import xlrd
# https://blogs.harvard.edu/rprasad/2014/06/16/reading-excel-with-python-xlrd/
import modules.cmd_fuse_exception as cmd_fuse_exception

class DataParser:

    def __init__(self, input_str):
        """
        Params
        ------
        path : str
            The filepath of the data
        """
        self._data = []
        if input_str and os.path.isfile(input_str):
            try:
                self._data = self._get_data(input_str)
            except OSError:
                with open(input_str) as input_file:
                    data_str = input_file.read()
                    self._data = self._get_data(data_str)
        elif input_str:
            self._data = self._get_data(input_str)
       
    @property
    def data(self):
        """
        Returns
        -------
        data : []
            Where one element is unknown
        """
        return self._data

    def _get_data(self, input_str):
        pass

class RawDataParser(DataParser):
    """
    Reads the selected file which holds the data for the commands 
    """
    _XLS_PATTERN = '\.xls'
    _TSV_PATTERN = '\.tsv'
    _CSV_PATTERN = '\.csv'

    def __init__(self, input_str):
        """
        Params
        ------
        input_str : str
            The file's path or a string input
        Raises
        ------
        TypeError
            When the file extension is not supported
        """
        self._dialect = None
        self._is_file_excel = False
        self._can_parse_input = os.path.isfile(input_str)

        if re.search(RawDataParser._XLS_PATTERN, input_str):
            self._is_file_excel = True
        elif re.search(RawDataParser._TSV_PATTERN, input_str):
            self._dialect = 'excel-tab'
        elif re.search(RawDataParser._CSV_PATTERN, input_str):
            self._dialect = 'excel'
        else:
            raise TypeError('Not supported file format')
        return super().__init__(input_str)
    
    def _get_data(self, input_str):
        """
        Returns
        -------
        rows : []
            Where one element is an OrderedDict
        """
        rows = []
        if self._can_parse_input:
            if self._is_file_excel:
                    book = xlrd.open_workbook(input_str)
                    rows = self._parse_workbook(book)
            else:
                with open(input_str) as file:
                    reader = csv.DictReader(file,dialect=self._dialect)
                    for _ in reader:
                        rows.append(_)
        return rows
    
    def _parse_workbook(self, book):
        """
        Returns
        -------
        data : []
            Where one element is an OrderedDict
        """
        data = []
        for sh_name in book.sheet_names():
            sheet = book.sheet_by_name(sh_name)
            nrows = sheet.nrows
            ncols = sheet.ncols
            column_names = []
            for row_idx in range(0, nrows):
                if row_idx == 0:
                    column_names = sheet.row_values(row_idx)
                else:
                    row_dict = OrderedDict()
                    for col_idx in range(0, ncols):
                        label = column_names[col_idx]
                        row_dict[label] = sheet.cell(row_idx, col_idx).value
                    data.append(row_dict)
        return data

