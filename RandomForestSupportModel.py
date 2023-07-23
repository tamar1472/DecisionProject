import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import pickle

class RandomForestSupportModel:
    def __init__(self, train_file, test_file):
        train = pd.read_csv(train_file)
        test = pd.read_csv(test_file)
        self.data = pd.concat([train, test])
        self.line = None  # input to predict
        self.clf = None

    def train_model(self):
        # over fitting
        X, y = self.data.iloc[:, :-1], self.data.iloc[:, -1]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
        clf = RandomForestClassifier(n_estimators=100)
        clf.fit(X_train, y_train)

        # feature_importance
        feature_imp = pd.Series(
            clf.feature_importances_, index=list(self.data.columns[:-1])
        ).sort_values(ascending=False).head(50).index.tolist()

        # fit model
        X_reduced, y = self.data[feature_imp], self.data.iloc[:, -1]
        X_train, X_test, y_train, y_test = train_test_split(X_reduced, y, test_size=0.3)
        self.clf = RandomForestClassifier(n_estimators=100)
        self.clf.fit(X_train, y_train)

        # update line input to predict
        self.line = pd.DataFrame(X_reduced.iloc[0].to_dict(), index=[0])
        self.line.replace(1, 0, inplace=True)

        # return accuracy
        y_pred = self.clf.predict(X_test)
        accuracy = metrics.accuracy_score(y_test, y_pred)
        return accuracy

    def make_prediction(self, df):
        # df.columns = df.columns.astype(str)

        prediction = self.clf.predict(df)[0]
        probability = self.clf.predict_proba(df).max(axis=1)[0]
        return prediction, probability

    def save(self, filename):
        with open(filename, "wb") as file:
            pickle.dump(self, file)

    @staticmethod
    def load(filename):
        with open(filename, "rb") as file:
            return pickle.load(file)


if __name__ == '__main__':
    train_file = 'Datasets/Training.csv'
    test_file = 'Datasets/Testing.csv'

    model = RandomForestSupportModel(train_file, test_file)

    print("Accuracy:", model.train_model())

    # model.save("model.pkl")
