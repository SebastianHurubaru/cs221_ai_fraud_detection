import csv

def predict_all_nonfraud(filename, skip_first = 1):
	correct = 0
	wrong = 0
	with open(filename) as csv_file:
	    csv_reader = csv.reader(csv_file, delimiter = ',')

	    if skip_first:
	        next(csv_reader, None)

	    for row in csv_reader:
	        has_committed_fraud = int(row[10])
	        
	        if has_committed_fraud:
	        	wrong += 1
	        else:
	        	correct += 1

	return (correct, wrong)

train_correct, train_wrong = predict_all_nonfraud('train_data.csv')
test_correct, test_wrong = predict_all_nonfraud('test_data.csv')

print (train_correct + test_correct) / float(train_correct + test_correct + test_wrong + train_wrong)