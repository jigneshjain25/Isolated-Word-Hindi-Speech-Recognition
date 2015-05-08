import numpy as np
import scipy.io.wavfile as wav
from features import get_features
import pylab as pl
from hmmlearn.hmm import GaussianHMM
import os
import sys
import math
import pickle

test_folder = sys.argv[1]

fpaths = []
labels = []
spoken = []
for f in os.listdir('dictionary'):
    temp = []
    for w in os.listdir('dictionary/' + f):
        temp.append('dictionary/' + f + '/' + w)
        labels.append(f)
        if f not in spoken:
            spoken.append(f)
    fpaths.append(temp)
print 'Words spoken:',spoken

serialized = open('Models/serialized.txt', 'r')
isSerial = False
if (serialized.read() == '1'):
	isSerial = True

if isSerial == False:
	print "Generating models..."
	n_samples = 20
	###############################################################################
	# Run Gaussian HMM
	models = []
	means = []
	std_devs = []

	for i in range(len(spoken)):
		#print "fitting to HMM and decoding ..."

		n_components = 3
		arr = []

		# make an HMM instance and execute fit
		model = GaussianHMM(n_components, covariance_type="diag", n_iter=1000)

		for j in range(n_samples):
			#print fpaths[i][j]
			(rate,sig) = wav.read(fpaths[i][j])
			features = get_features(sig)
			arr.append(len(features))
			model.fit([features])

		models.append(model)
		means.append(np.mean(arr))
		std_devs.append(np.std(arr))
	
	with open('Models/models.pkl', 'wb') as output:
		pickle.dump(models, output, pickle.HIGHEST_PROTOCOL)
		
	with open('Models/means.pkl', 'wb') as output:
		pickle.dump(means, output, pickle.HIGHEST_PROTOCOL)
		
	with open('Models/std_devs.pkl', 'wb') as output:
		pickle.dump(std_devs, output, pickle.HIGHEST_PROTOCOL)

	serialized = open('Models/serialized.txt', 'w')
	serialized.write("1")
	print "Done\n"
else:
	print "Loading models..."
	with open('Models/models.pkl', 'rb') as input:
		models = pickle.load(input)
		
	with open('Models/means.pkl', 'rb') as input:
		means = pickle.load(input)
		
	with open('Models/std_devs.pkl', 'rb') as input:
		std_devs = pickle.load(input)
	print "Done\n"

correct_answers = []
with open('Test/'+test_folder+'/answer.txt') as answers:
    for entry in answers:
        correct_answers.append(entry.split())

tot_words = len(correct_answers)
right = 0.0
threshold = 1

for i in xrange(tot_words):
	(rate,sig) = wav.read('Test/'+test_folder+"/word" + str(i) + ".wav")
	features = get_features(sig)
	word_len = len(features)
	ans = -1
	j = -1
	max_ans = -1e9
	for model in models:
	    j = j+1
	    if math.fabs(word_len - means[j]) <= threshold * std_devs[j]:
		    temp = model.score(features)
		    if temp>max_ans:
			    max_ans = temp
			    ans = j
	
	#print max_ans
	print str(i+1)+". Detected word: "+spoken[ans]
	if spoken[ans] == correct_answers[i][0]:
	    right = right + 1
	    
print "Accuracy = "+str((right/tot_words)*100)+"%"

'''
###############################################################################
# print trained parameters and plot
print("Transition matrix")
print(model.transmat_)
print()

print("means and vars of each hidden state")
for i in range(n_components):
    print("%dth hidden state" % i)
    print("mean = ", model.means_[i])
    print("var = ", np.diag(model.covars_[i]))
    print()

years = YearLocator()   # every year
months = MonthLocator()  # every month
yearsFmt = DateFormatter('%Y')
fig = pl.figure()
ax = fig.add_subplot(111)

for i in range(n_components):
    # use fancy indexing to plot data in each state
    idx = (hidden_states == i)
    ax.plot_date(dates[idx], close_v[idx], 'o', label="%dth hidden state" % i)
ax.legend()

# format the ticks
ax.xaxis.set_major_locator(years)
ax.xaxis.set_major_formatter(yearsFmt)
ax.xaxis.set_minor_locator(months)
ax.autoscale_view()

# format the coords message box
ax.fmt_xdata = DateFormatter('%Y-%m-%d')
ax.fmt_ydata = lambda x: '$%1.2f' % x
ax.grid(True)

fig.autofmt_xdate()
pl.show()
'''
