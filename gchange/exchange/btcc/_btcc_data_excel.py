from xlutils.copy import copy # http://pypi.python.org/pypi/xlutils
from xlrd import open_workbook # http://pypi.python.org/pypi/xlrd
from xlwt import easyxf, Workbook, Worksheet # http://pypi.python.org/pypi/xlwt

    
    history_datas = btcc.get_history_data_by_time(time = time, limit = 5000)

    workbook = Workbook(encoding='UTF-8')
    worksheet = workbook.add_sheet('history_data')

    '''
    if len(history_datas):
        for row_index in range(0, len(history_datas)):
            data = history_datas[row_index]
            worksheet.write(row_index, 0, data.tid)
            worksheet.write(row_index, 1, data.timestamp)
            worksheet.write(row_index, 2, data.price)
            worksheet.write(row_index, 3, data.amount)
            worksheet.write(row_index, 4, data.type)
        workbook.save('/Users/guanyayang/Documents/history_data_out.xls')
    '''