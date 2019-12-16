####################
#This is to be run in python
###################

#in your csv file, the columns must be the same length.
#you must have weeks in the first column and earned_actual in the second column
#to run this on your command line:  python scurve.py data_csv_file_name.csv 45 

import csv
import numpy as np
import matplotlib.pyplot as plt
import sys
import pandas as pd


#setting up my lists
weeks = []
earned_act = []
planned = []
earned_pred = []
array1 = []
array2 = []
arrayI = []
arrayS = []
arrayN = []
lw_list = []
N_weeks = []
files_list = []
num_files = []
predictions = []
N_range = 1

# def find_csv_filenames( path_to_dir, suffix=".csv" ):
#     filenames = listdir(path_to_dir)
#     return [ filename for filename in filenames if filename.endswith( suffix ) ]


# filenames = find_csv_filenames("C:\Users\William.Casey")
# for name in filenames:
#     files_list.append(name)
# for i in range(0, len(files_list)):
#     num_files.append(i)
#     print num_files[i], " : ", files_list[i]
    

#print num_files, name


file = sys.argv[1]
N_guess = int(sys.argv[2])




#getting my data from csv and putting each item into its list

with open (file) as f:
    for row in csv.reader(f):
        weeks.append(float(row[0])) #changed int to float
        earned_act.append(float(row[1]))
        # planned.append(float(row[2]))



        
#print weeks
#print earned_act
#print planned
weeks_a = np.array(weeks)
earned_act_a = np.array(earned_act)

#setting my parameters
def residuals():
    s = .1
    i = .1
    n = N_guess - N_range
    while s < 5:
        s = s + .01
        i = .1    
        while i < 5:
            i = i + .01
            n = N_guess - N_range
            while n < N_guess + N_range:
                #n = n + 1
                if (sum((earned_act_a - scurve(weeks_a, i, s, n))**2)) > 0:
                    #if scurve(.8*n, i, s, n) > .899:
                        arrayI.append(i)
                        arrayS.append(s)
                        arrayN.append(n)
                        array1.append(sum((earned_act - scurve(weeks_a, i, s, n))**2))
                n = n + 1

    min_index = np.argmin(array1)
    SSE = array1[min_index]
    pred_I = arrayI[min_index]
    pred_S = arrayS[min_index]
    pred_N = arrayN[min_index]
    predictions = [pred_I, pred_S, pred_N]
    #print predictions


    for i in range(1, pred_N + 1):
        N_weeks.append(i)
    N_weeks2 = np.array(N_weeks)
    scurve_a(N_weeks2, pred_I, pred_S, pred_N)
    print("Weeks : Predicted % Complete")
    for i in range(0, pred_N):    
        print( N_weeks2[i], " : ",  earned_pred[i])

     
    r2 = 1 - (SSE/SST_F(earned_act_a, np.mean(earned_act_a)))
    adj_r2 = 1 - ((1- r2)*(len(earned_act_a) - 1)/(len(earned_act_a) - 4))

####print the fit parameters and the R2
    # if print_stats == True:
    print("SST: ", SST_F(earned_act_a, np.mean(earned_act_a)))
    print("SSE, iteration #: ", SSE, min_index)
    print("R-squared: ", r2)
    print("Adj. R-squared: ", adj_r2)
    print("Predicted I: ", pred_I)
    print("Predicted S: ", pred_S)
    print("Predicited N: ", pred_N)
    
    
    
    df = pd.DataFrame({'weeks' : range(1, len(earned_pred) +1), 'earned_predicted': earned_pred})
    # print(df)
    df.to_csv('results.csv', index=False)
    # c = csv.writer(open("results.csv", "wb"))
    # c.writerow(earned_pred)
    # print(type(earned_pred))
    # print(earned_pred)

    # for i in range(1, len(array1) + 1):
    #     array2.append(i)
    

    

    # plt.figure(1)
    # plt.title('S Curve: %s ' %(charttitle))
    # plt.grid(True)
    # #plot  planned value
    # plt.plot(weeks_a,planned,'b')
    # #plot earned actuals
    # plt.plot(weeks_a, earned_act_a, 'r')
    # #plot earned forecasted
    # plt.plot(N_weeks, earned_pred,'g--')
    # plt.xlabel('Time (weeks)')
    # plt.ylabel('% Complete');

    # plt.figure(2)
    # plt.plot(array2, array1, 'k')
    # plt.xlabel('Iterations')
    # plt.ylabel('Min');
    
    # plt.show()









#plugging earned actual data and predicted parameters into scurve function to get predicted outcome
def scurve_a(y_array, I, S, N):
    for y in y_array:
        ep = 1-(1-(float(y)*(N)**-1)**I)**S
        earned_pred.append(ep)
    return earned_pred
 
def scurve(y_array, I, S, N):
    return 1-(1-(y_array*(N)**-1)**I)**S

#formula for computing the SST for r-squared
def SST_F(y_i, y_bar):
    SST =  sum((y_i - y_bar)**2)
    return SST


    
            


residuals()   
 



   

        
