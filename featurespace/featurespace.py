import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import warnings
import argparse
from FS import *

warnings.filterwarnings("ignore")

#get command line arguements
parser = argparse.ArgumentParser(description='FeatureSpace Fraud Model')
parser.add_argument(
    '--transactions_file'
    , type=str
    , help="""provide the file path for the transactions data
            i.e. ~/Desktop/transactions_obf.csv"""
)
parser.add_argument(
    '--label_file'
    , type=str
    , help="""provide the file path for the label data
            i.e. ~/Desktop/labels_obf.csv"""
)
file_paths = parser.parse_args()

###########global variables#########################
transactions_file_path, labels_file_path = file_paths.transactions_file, file_paths.label_file
cat_cols = ['accountNumber', 'merchantId', 'mcc','merchantCountry', 'posEntryMode']
train_percent = 2/3
valid_percent = (1/3)*(1/3)

#columns to be used in the model
model_columns = [
# 'availableCash',
#  'cash_delta',
 'percent_of_total_account_amount',
#  'transactionAmount',
#  'accountNumber_fraud_rate',
#  'accountNumber_nr_trans',
 'accountNumber__amount_percentile',
#  'merchantId_fraud_rate',
#  'merchantId_nr_trans',
 'merchantId__amount_percentile',
#  'mcc_fraud_rate',
#  'mcc_nr_trans',
 'mcc__amount_percentile',
#  'merchantCountry_fraud_rate',
#  'merchantCountry_nr_trans',
 'merchantCountry__amount_percentile',
#  'posEntryMode_fraud_rate',
#  'posEntryMode_nr_trans'
]

#model hyperparameters
Params = {     'bootstrap': True
	     , 'max_depth': 2
	     , 'max_features': 4
	     , 'min_samples_leaf': 3
	     , 'min_samples_split': 2
	     , 'n_estimators': 1000
	}


############################################

def read_data(*csvs):
   transactions, lables = [csv for csv in csvs]
   trans_df = pd.read_csv(transactions)
   labels_df = pd.read_csv(lables)
   return trans_df, labels_df

def clean_data(trans, labels):
    labels['label'] = 1
    df = trans.merge(labels, how='left', on='eventId')
    df['label'] = df.label.fillna(0).astype('int')
    df[cat_cols] = df[cat_cols].astype('str')
    df['reported_delta_days'] = (pd.to_datetime(df['reportedTime']) - pd.to_datetime(df['transactionTime'])).dt.days
    df['reportedTime'] = pd.to_datetime(df['reportedTime']).dt.date
    df['transactionTime'] = pd.to_datetime(df['transactionTime'])
    df['transactionDate'] = df['transactionTime'].dt.date
    df['cash_delta'] = df.availableCash - df.transactionAmount
    df['percent_of_total_account_amount'] = df.transactionAmount/df.availableCash
    return df

def train_test_model(Params, traindata, testdata, y_train):
    rf = RandomForestClassifier(n_estimators=1000
                                , n_jobs=-1
                                , max_depth=Params['max_depth']
                                , max_features=Params['max_features']
                                , min_samples_leaf = Params['min_samples_leaf']
                                , min_samples_split = Params['min_samples_split']
                                , random_state=300
                               )
    model = rf.fit(traindata, y_train)
    predictions_prob_train = model.predict_proba(traindata)
    predictions_prob_test = model.predict_proba(testdata)

    prob1__train = [a[1] for a in predictions_prob_train]
    prob1__test = [a[1] for a in predictions_prob_test]
    return model, prob1__train, prob1__test


def valid_model(model, validdata, validdata_transactionAmount, y_valid):
    predictions_prob_valid = model.predict_proba(validdata)
    prob1__valid = [a[1] for a in predictions_prob_valid]
    validdata['predictions_prob'] =prob1__valid
    validdata['actual_label'] = y_valid
    if 'transactionAmount' not in validdata.columns:
        validdata['transactionAmount'] = validdata_transactionAmount

    #they can review about 400 per month or about 13 per day. in the test/validation sets there
    #are about 140 days. So 140*13 = 1820 but I'm only looking at half of the traffic in the
    #validation set so take the top ~900
    saved = validdata.sort_values('predictions_prob', ascending=False).head(900)
    total_money_saved = saved[saved['actual_label'] == 1].transactionAmount.sum()
    total_fraud_money = validdata[validdata['actual_label'] == 1].transactionAmount.sum()
    precision_money = (total_money_saved/saved.transactionAmount.sum())
    recall_money = (total_money_saved/total_fraud_money)
    return total_money_saved, total_fraud_money, precision_money, recall_money


def main():
    print("Reading data from CSV")
    transactions, labels = read_data(transactions_file_path, labels_file_path)
    print("Cleaning data")
    df = clean_data(transactions, labels)
    pop_fraud_rate = df.label.sum()/len(df)
    print("Fraud rate of the whole population: {}".format(pop_fraud_rate))
    train_split_idx = round((len(df)*train_percent))

    # split data into time train and test
    print("Splitting data into train and test")
    X_train, X_test, y_train, y_test = timeseries_train_test(df, 'label', train_split_idx)
    # Reassign the label column with only the usable labels
    X_train['label'] = X_train['usable_label']
    y_train = X_train.label
    #drop some time columns and usuable label column
    X_train = X_train.drop(columns=['usable_label', 'reported_delta_days'])
    X_test = X_test.drop(columns='reported_delta_days')

    #add nulls to train
    print("Adding Nulls to train")
    X_train = add_nulls_to_train(X_train, cat_cols, fraud_rate=pop_fraud_rate, nr_rows=1000)
    print("Processing categorical columns")
    X_train, X_test = preprocessing_cat_cols(X_train, X_test, cat_cols)

    #fill nulls in test set with -1 to match the nulls added in train
    X_test = X_test.fillna(-1)

    # drop aggregated columns
    print("dropping amount aggregate columns")
    agg_cols = ['trans_amount_mean', 'trans_amount_std', 'trans_amount_median',
                'percentile_75', 'percentile_90', 'percentile_99']

    drop_columns = []
    for col in cat_cols:
        for c in agg_cols:
            drop_columns.append(col + '_' + c)

    X_train = X_train.drop(columns=drop_columns)
    X_test = X_test.drop(columns=drop_columns)


    #split the test set into a valid set as well
    y_train = X_train.label
    y_test = X_test.label
    print("Splitting the test data into test and valid")
    X_valid, X_test, y_valid, y_test = (train_test_split(X_test
                                                    , X_test.label
                                                    , test_size=.50, random_state=100))


    print("train fraud_percent: {}".format((X_train[['label']].sum()/len(X_train)).values[0]))
    print("test fraud_percent: {}".format((X_test[['label']].sum()/len(X_test)).values[0]))
    print("valid fraud_percent: {}".format((X_valid[['label']].sum()/len(X_valid)).values[0]))

    traindata, testdata, validdata = X_train[model_columns], X_test[model_columns], X_valid[model_columns]
    validdata_transactionAmount = X_valid.transactionAmount

    #train and test model
    print("Modeling data with RandomForest")
    model, prob1__train, prob1__test = train_test_model(Params, traindata, testdata, y_train)

    train_average_precision_score = metrics.average_precision_score(y_train, prob1__train)
    train_auc = metrics.roc_auc_score(y_train, prob1__train)

    test_average_precision_score = metrics.average_precision_score(y_test, prob1__test)
    test_auc = metrics.roc_auc_score(y_test, prob1__test)
    total_money_saved, total_fraud_money, precision_money, recall_money = valid_model(model, validdata, validdata_transactionAmount, y_valid)

    print("""
            Model Metrics:
            Training Average Precision Score: {0}
            Testing Average Precision Score:  {1}
            Train AUC:                        {2}
            Test AUC:                         {3}

            Validation
            Money Saved                       {4}
            Total Fraud Amout:                {5}
            Precision (Money):                {6}
            Recall (Money):                   {7}
            """.format(train_average_precision_score
                      ,test_average_precision_score
                      , train_auc
                      , test_auc
                      , total_money_saved
                      , total_fraud_money
                      , precision_money
                      , recall_money

                      ))



if __name__ == '__main__':
    main()
