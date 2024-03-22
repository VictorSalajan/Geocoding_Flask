from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from stats_and_visuals import clean_df


def get_feature_and_target():
    df = clean_df()
    x = df['latitude'].to_numpy().reshape(-1, 1)
    y = df['gdp_per_capita'].to_numpy().reshape(-1, 1)

    return x, y


def split_data(x, y):
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.35, random_state=555)

    return X_train, X_test, y_train, y_test


def scale_features(X_train, X_test):
    poly_features = PolynomialFeatures(degree=2)
    X_train = poly_features.fit_transform(X_train)
    X_test = poly_features.transform(X_test)

    return X_train, X_test

def train_model(X_train, y_train):
    model = LinearRegression()
    model.fit(X_train, y_train)

    return model


def metrics_pipeline():
    x, y = get_feature_and_target()
    X_train, X_test, y_train, y_test = split_data(x, y)
    X_train, X_test = scale_features(X_train, X_test)
    model = train_model(X_train, y_train)
    y_pred = model.predict(X_test)

    mean_abs_error = mean_absolute_error(y_test, y_pred)
    root_mean_sq_error = root_mean_squared_error(y_test, y_pred)
    coeff_of_determination = r2_score(y_test, y_pred)

    return mean_abs_error, root_mean_sq_error, coeff_of_determination
