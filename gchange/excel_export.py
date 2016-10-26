class ExcelExport(object):

    def __init__(self, out_filepath, sheet_name = None):
        self._out_filepath = out_filepath
        self._sheet_name = sheet_name

        self._workbook = Workbook(encoding='UTF-8')
        self._worksheet = workbook.add_sheet(self._sheet_name)

    def export(self):
        raise NotImplementedError
    
    def save(self):
        self.export()
        self.save(self._out_filepath)



    