import pandas as pd
import math
    from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import normalize
import numpy as np

DATA = pd.read_csv('dev_issues.csv')

X = DATA[['# Closed issues', '# Devs opened issues', '# contributors', "# Open issues", "Number of issue comments", "# Devs opened pulls", "# reactions in closed issues"]]
normalize = normalize(X)
X = pd.DataFrame(normalize)
X = X.to_numpy()


X_links = DATA['Link'].to_numpy()
y = DATA['# Devs closed issues'].to_numpy()

X_train1 = []
y_train1 = []

X_final = []
y_final = []
x_links_final = []
for i in range(len(y)):
    if math.isnan(y[i]):
        X_final.append(X[i])
        x_links_final.append(X_links[i])
    else:
        X_train1.append(X[i])
        y_train1.append(y[i])

X_train, X_test, y_train, y_test = train_test_split(X_train1, y_train1, test_size=0.1, random_state=8)
regr = LinearRegression()
regr.fit(X_train, y_train)
y_pred = regr.predict(X_test)

# The mean squared error
print("Mean squared error: %.2f" % mean_squared_error(y_test, y_pred))
# The coefficient of determination: 1 is perfect prediction
print("Coefficient of determination: %.2f" % r2_score(y_test, y_pred))

y_final = regr.predict(X_final)

for i in range(len(y_final)):
    print("Link", x_links_final[i], " Dev", y_pred[i])
