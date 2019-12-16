import pandas as pd 
import numpy as np
import sys

#in your csv file, the columns must be the same length.
#you must have weeks in the first column and earned_actual in the second column
#to run this on your command line:  python scurve.py data_csv_file_name.csv 45 True


def residuals(df, N_guess, N_range, print_stats):
	array1 = []
	array2 = []
	arrayI = []
	arrayS = []
	arrayN = []
	weeks_a = df[df.columns[0]]
	earned_act_a = df[df.columns[1]]
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
					arrayI.append(i)
					arrayS.append(s)
					arrayN.append(n)
					array1.append(sum((earned_act_a - scurve(weeks_a, i, s, n))**2))
				n = n + 1

	min_index = np.argmin(array1)
	SSE = array1[min_index]
	pred_I = arrayI[min_index]
	pred_S = arrayS[min_index]
	pred_N = arrayN[min_index]
	predictions = [pred_I, pred_S, pred_N]
    #print predictions


	earned_pred_array = scurve_a(np.array(range(1, pred_N + 1)), pred_I, pred_S, pred_N)
	pred_df = pd.DataFrame({'Weeks': range(1, pred_N + 1), 'predicted_earned_value': earned_pred_array})
	pred_df.to_csv('results.csv')


    # r-squared formula, p = 3 (number of parameters)
	r2 = 1 - (SSE/SST_F(earned_act_a, np.mean(earned_act_a)))
	adj_r2 = 1 - ((1- r2)*(len(earned_act_a) - 1)/(len(earned_act_a) - 4))

####print the fit parameters and the R2
	if print_stats == True:
		print("SST: ", SST_F(earned_act_a, np.mean(earned_act_a)))
		print("SSE, iteration #: ", SSE, min_index)
		print("R-squared: ", r2)
		print("Adj. R-squared: ", adj_r2)
		print("Predicted I: ", pred_I)
		print("Predicted S: ", pred_S)
		print("Predicited N: ", pred_N)




def scurve(y_array, I, S, N):
	return 1-(1-(y_array*(N)**-1)**I)**S

#plugging earned actual data and predicted parameters into scurve function to get predicted outcome
def scurve_a(y_array, I, S, N):
	for y in y_array:
		ep = 1-(1-(float(y)*(N)**-1)**I)**S
		earned_pred.append(ep)
	return earned_pred


def main():
	N_range = 1
	df = pd.read_csv(sys.argv[1])
	N_guess = int(sys.argv[2])
	print_stats = sys.argv[3]
	residuals(df, N_guess, N_range, print_stats)
	print("Done")
	# print(df)





if __name__ == '__main__':
	main()