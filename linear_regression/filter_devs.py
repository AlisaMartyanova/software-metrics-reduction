import pandas as pd
from sklearn.preprocessing import normalize


data = pd.read_csv('dev_issues (copy).csv')
data = data.drop('Link', axis=1)
normalize = normalize(data)
data_scaled = pd.DataFrame(normalize)

correlation = data_scaled.corr(method='spearman')

# print(correlation)

THRESHOLD = 0.65
variables = []
columns = data.columns

variance = data_scaled.var()
#
# print(correlation)
for i in range(len(variance)):
    if correlation[len(variance)-1][i] > THRESHOLD:
        print(correlation[len(variance) - 1][i])
        variables.append(columns[i])
for i in range(len(variables)):
    print(variables[i])

print(len(variables))
# print(variables)

# variance = data_scaled.var()
# columns = data.columns
# variable = []
# THRESHOLD = 0.2

# for i in range(0,len(variance)):
#     for j in range(0,len(variance)):
#         if columns[i]!= columns[j] and (columns[i] not in variable) and (correlation[i][j]>THRESHOLD or correlation[i][j] is not None):
#             variable.append(columns[i])
# print(variable)