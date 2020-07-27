import numpy as np
import pandas as pd
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.stattools import adfuller, acf, pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from fbprophet import Prophet


def test_stationarity(time_series):
    # Determing rolling statistics
    rolling_mean = time_series.rolling(30).mean()
    rolling_std = time_series.rolling(30).std()

    # Plot rolling statistics:
    orig = plt.plot(time_series, color='blue', label='Original')
    mean = plt.plot(rolling_mean, color='red', label='Rolling Mean')
    std = plt.plot(rolling_std, color='black', label='Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean & Standard Deviation')
    plt.show(block=False)

    # Perform Dickey-Fuller test:
    print('Results of Dickey-Fuller Test:')
    dickey_fuller_test = adfuller(time_series, autolag='AIC')
    dickey_fuller_output = pd.Series(dickey_fuller_test[0:4],
                                     index=['Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used'])
    for key, value in dickey_fuller_test[4].items():
        dickey_fuller_output['Critical Value (%s)' % key] = value
    print(dickey_fuller_output)


def log_shift(data, shift):
    ts_log = np.log(data)
    ts_log_diff = ts_log - ts_log.shift(shift)
    ts_log_diff = ts_log_diff.dropna()
    ts_log_diff = pd.Series(ts_log_diff.values, index=ts_log_diff.index)
    return ts_log, ts_log_diff


def decompose(data, col):
    ts_log, ts_log_diff = log_shift(data[col], 1)
    decomposition = seasonal_decompose(ts_log)

    trend = decomposition.trend
    seasonal = decomposition.seasonal
    residual = decomposition.resid

    figure(num=None, figsize=(10, 7), dpi=300, facecolor='w', edgecolor='k')
    plt.subplot(411)
    plt.plot(ts_log, label='Original')
    plt.legend(loc='best')
    plt.subplot(412)
    plt.plot(trend, label='Trend')
    plt.legend(loc='best')
    plt.subplot(413)
    plt.plot(seasonal, label='Seasonality')
    plt.legend(loc='best')
    plt.subplot(414)
    plt.plot(residual, label='Residuals')
    plt.legend(loc='best')
    plt.tight_layout()
    return trend, seasonal, residual


def transform(data, window):
    ts_log = np.log(data)
    avg_log = ts_log.rolling(window=window).mean()
    diff_ts_avg = (ts_log - avg_log).dropna()
    return diff_ts_avg


def ACF_PACF(time_series):
    figure(num=None, figsize=(5, 3), dpi=300, facecolor='w', edgecolor='k')
    # Use the transform function data 
    ts_log_diff = transform(time_series, window=30)
    lag_acf = acf(ts_log_diff, nlags=10)
    lag_pacf = pacf(ts_log_diff, nlags=10, method='ols')
    # Plot ACF:
    plt.subplot(121)
    plt.plot(lag_acf)
    plt.axhline(y=0, linestyle='--', color='green')
    plt.axhline(y=-1.96 / np.sqrt(len(ts_log_diff)), linestyle='--', color='red')
    plt.axhline(y=1.96 / np.sqrt(len(ts_log_diff)), linestyle='--', color='red')
    plt.title('Autocorrelation Function')

    # Plot PACF:
    plt.subplot(122)
    plt.plot(lag_pacf)
    plt.axhline(y=0, linestyle='--', color='green')
    plt.axhline(y=-1.96 / np.sqrt(len(ts_log_diff)), linestyle='--', color='red')
    plt.axhline(y=1.96 / np.sqrt(len(ts_log_diff)), linestyle='--', color='red')
    plt.title('Partial Autocorrelation Function')
    plt.tight_layout()


def ARIMA_funtion(ts_log, ts_log_diff, order):
    model = ARIMA(ts_log, order=order)
    results = model.fit(disp=-1)
    rss = np.sum((results.fittedvalues - ts_log_diff) ** 2)
    figure(num=None, figsize=(10, 7), dpi=300, facecolor='w', edgecolor='k')
    plt.plot(ts_log_diff)
    plt.plot(results.fittedvalues, color='red')
    plt.title('RSS: %.4f' % rss)
    fitted = results.fittedvalues()
    print("RSS of the model is = " + str(rss))
    return fitted


def fit_ARIMA(ts, order):
    ts_log, ts_log_diff = log_shift(ts, 1)
    model = ARIMA(ts_log, order=(1, 1, 1))
    results_ARIMA = model.fit(disp=-1)
    plt.plot()
    plt.plot(results_ARIMA.fittedvalues, color='red')
    plt.title('RSS: %.4f' % sum((results_ARIMA.fittedvalues - ts_log_diff) ** 2))
    return results_ARIMA


def predict_ARIMA(ts, order):
    results_ARIMA = fit_ARIMA(ts, order)
    predictions_ARIMA = pd.Series(results_ARIMA.fittedvalues, copy=True)
    return predictions_ARIMA


def create_date_col(df):
    df['Date'] = pd.to_datetime(df[['year', 'month', 'day']])
    return df


def make_continuous(df):
    df = df[['price', 'Date']].set_index('Date')  # Set Date as index
    df = df.asfreq(freq='1D')  # Set the frequency as 1 Day
    ## fill missing values by interpolating
    df['price'].interpolate(inplace=True)
    return df


def prophet_forecast(data, period, changepoint_prior_scale=0.5):
    data = make_continuous(data)
    df = pd.DataFrame()
    df['ds'] = data.index
    df['y'] = data.price.values
    m = Prophet(changepoint_prior_scale=changepoint_prior_scale)
    m_fit = m.fit(df)
    future = m.make_future_dataframe(periods=period)
    forecast = m.predict(future)
    forecast = forecast.round(0)
    fig1 = m.plot(forecast)
    fig2 = m.plot_components(forecast)
    return forecast
