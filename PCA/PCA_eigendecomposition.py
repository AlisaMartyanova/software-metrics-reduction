from openpyxl import load_workbook
from sklearn import preprocessing
import pandas as pd
import numpy as np


# normalize the entire dataset using min-max scaler
def normalize(dataset):
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(dataset)

    return x_scaled


def pca(data, initial_feature_names):
    # calculate covariance matrix
    cov_mat = np.cov(data, rowvar=False)

    # from this covariance matrix, calculate the eigenvalues and the eigenvectors
    eigen_vals, eigen_vecs = np.linalg.eig(cov_mat)

    # sort eigenvalues and eigenvectors
    sorted_index = np.argsort(eigen_vals)[::-1]
    sorted_eigenvalue = eigen_vals[sorted_index]
    sorted_eigenvectors = eigen_vecs[:, sorted_index]

    # get number of components that explain 95% of variance
    variance_explained = []
    count = 0
    for i in sorted_eigenvalue:
        if sum(variance_explained) >= 95:
            break
        variance_explained.append((i / sum(sorted_eigenvalue)) * 100)
        count += 1

    # get most important feature from each component
    most_important = [np.abs(sorted_eigenvectors[i]).argmax() for i in range(count)]
    most_important_names = [initial_feature_names[i] for i in most_important[:count]]
    return most_important_names


# save results as a table
def interpret_results(initial_names, xlsx_filename, result_names):
    wb = load_workbook(xlsx_filename)
    sheet = wb.active
    sheet.cell(1, 1, 'Number of metrics')

    for i in range(len(initial_names)):
        sheet.cell(1, i + 2, initial_names[i])
    for i in range(len(result_names)):
        sheet.cell(i+2, 1, i+1)
        for c in range(len(initial_names)):
            if initial_names[c] == result_names[i]:
                for j in range(i, len(result_names)):
                    sheet.cell(j+2, c+2, 1)

    wb.save(xlsx_filename)


def main():

    # data with 49 metrics
    data_filename = '49.csv'

    # read the data, fill missing values with median and convert all to float
    data = pd.read_csv(data_filename)
    for i in data:
        data[i] = data[i].astype(float)
    initial_feature_names = [d for d in data]
    data = normalize(data)

    names = pca(data, initial_feature_names)
    names = list(dict.fromkeys(names))
    print(len(names), names)

    # interpret_results(initial_feature_names, 'results/PCA_results_49.xlsx', names)


main()
