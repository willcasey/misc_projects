#!/usr/bin/python
#from sklearn import metrics
import numpy as np
import pandas as pd
from math import isnan

def non_usable_lable(report_time, label, split_date):
    if report_time > split_date:
        return 0
    else:
        return label


def timeseries_train_test(df, label, train_split_idx):
    df = df.sort_values('transactionTime').reset_index(drop=True)
    X_train = df[:train_split_idx]
    split_date = df.loc[train_split_idx, 'transactionDate']
    X_train['usable_label'] = X_train[['reportedTime', label]].apply(lambda x: non_usable_lable(x['reportedTime']
                                                                        , x[label], split_date), axis=1)
    y_train = X_train['usable_label']
    X_test = df[train_split_idx:]
    y_test = X_test[label]
    return X_train, X_test, y_train, y_test

def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'percentile_%s' % n
    return percentile_

def which_percentile(col, amt, *args):
    percentile_50, percentile_75, percentile_90, percentile_99 = [i for i in args]
    if amt >= percentile_99:
        return 99
    elif amt < percentile_99 and amt >= percentile_90:
        return 90
    elif amt < percentile_90 and amt >= percentile_75:
        return 75
    elif amt < percentile_75 and amt >= percentile_50:
        return 50
    elif col == 'dummy' or isnan(percentile_50):
        return -1
    else:
        return 0

def add_nulls_to_train(X_train,cat_cols, fraud_rate, nr_rows=1000):
    """
    This is to add some random nulls to the training set
    So that the test set will know how to handles cases where the category is unknown

    """
    add_to_train = pd.DataFrame(columns=['transactionTime', 'eventId', 'accountNumber', 'merchantId', 'mcc',
           'merchantCountry', 'posEntryMode', 'transactionAmount', 'availableCash',
           'reportedTime', 'label', 'transactionDate', 'cash_delta'])
    for col in cat_cols:
        add_to_train_1 = X_train[X_train['label'] == 1].sample(n=int(fraud_rate*nr_rows))
        add_to_train_0 = X_train[X_train['label'] == 0].sample(n=(nr_rows-int(fraud_rate*nr_rows)))
        add_to_train_1[col] = ['dummy']*len(add_to_train_1)
        add_to_train_0[col] = ['dummy']*len(add_to_train_0)
        add_to_train = pd.concat([add_to_train, add_to_train_1, add_to_train_0])
    add_to_train['label']  = add_to_train['label'].astype('int')
    X_train = pd.concat([X_train, add_to_train])
    return X_train


def get_fraud_percent(df, col):
    """
    Returns the fraud percent and total
    number of transactions for the given column
    as a dataframe
    """
    agg = df[[col, 'label']].groupby(col).agg({'label': [np.size, np.sum]})
    agg.columns = [col + '_' +'nr_trans', col + '_' + 'nr_fraud_trans']
    total = agg[col + '_' + 'nr_fraud_trans'].sum()
    agg = agg.reset_index()
    agg[col + '_' + 'fraud_rate'] = agg[col + '_' + 'nr_fraud_trans']/total
    agg[col + '_' +'nr_trans'] = agg.apply(lambda x: replace_dummies(x[col], x[col + '_' +'nr_trans']), axis=1)
    agg[col + '_' + 'fraud_rate'] = agg.apply(lambda x: replace_dummies(x[col], x[col + '_' + 'fraud_rate']), axis=1)
    return agg[[col, col + '_' + 'fraud_rate', col + '_' +'nr_trans']]

def get_transaction_amount(df, col):
    agg = df.groupby(col).agg({'transactionAmount': [np.mean, np.std, np.median
                                                     , percentile(75), percentile(90), percentile(99)]})
    agg_columns = ['trans_amount_mean', 'trans_amount_std', 'trans_amount_median',
                'percentile_75', 'percentile_90', 'percentile_99']
    agg.columns = [col + '_' + w for w in agg_columns]
    agg = agg.reset_index()
    for c in agg:
        agg[c] = agg.apply(lambda x: replace_dummies(x[col], x[c]), axis=1)
    return agg


def replace_dummies(col, item):
    if col == 'dummy':
        return -1
    else:
        return item

def preprocessing_cat_cols(X_train, X_test, cat_cols):
    dataframe_list = []
    for dataframe in [X_train, X_test]:
        dataframe = dataframe.drop(columns=['reportedTime', 'eventId'])
        for col in cat_cols:
            dataframe = dataframe.merge(get_fraud_percent(X_train[[col, 'label']], col=col), on=col, how='left')
            dataframe = (dataframe.merge(get_transaction_amount(X_train[[col, 'transactionAmount']], col=col)
                                                                , on=col
                                                                , how='left'))
            dataframe[col + '__amount_percentile'] = (dataframe
                                                     .apply(lambda x: which_percentile(x[col], x['transactionAmount']
                                                                      ,x[col + '_' + 'trans_amount_median']
                                                                      , x[col + '_' + 'percentile_75']
                                                                      , x[col + '_' + 'percentile_90']
                                                                      , x[col + '_' + 'percentile_99'])
                                                                        ,axis=1)
                                                        )

        dataframe_list.append(dataframe)
    return dataframe_list
