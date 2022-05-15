import xlsxwriter

import pandas as pd
import gen_algo
workbook = xlsxwriter.Workbook('ga.xlsx')
worksheet = workbook.add_worksheet()

DATA = pd.read_csv('51.csv')
columns = list(DATA.columns)

for i in range(len(columns)):
    worksheet.write(i+1, 0, columns[i])
for i in range(50):
    names = list(gen_algo.start(i+1))
    worksheet.write(0, i+1, i+1)
    for j in range(len(names)):
        worksheet.write(columns.index(names[j]), i+1, 1)

workbook.close()