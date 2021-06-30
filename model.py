import numpy
import pandas
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

# convert an array of values into a dataset matrix
def create_dataset(dataset, look_back=1,future = 1):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-future):
		a = dataset[i:(i+look_back), 0]
		dataX.append(a)
		dataY.append(dataset[i + look_back:i+look_back+future, 0])
  
	return numpy.array(dataX),numpy.asarray(dataY).astype('float32')


def predict(df,look_back,future):
	# normalize the dataset
	scaler = MinMaxScaler(feature_range=(0, 1))
	dataset = scaler.fit_transform(df.values.reshape(-1,1))

	# reshape into X=t and Y=t+1
	trainX, trainY = create_dataset( dataset[0:,:], look_back,future)

	# reshape input to be [samples, time steps, features]
	trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))

	# create and fit the LSTM network
	model = Sequential()
	model.add(LSTM(10, input_shape=(1, look_back)))
	model.add(Dense(future))
	model.compile(loss='mean_squared_error', optimizer='adam')
	model.fit(trainX, trainY, epochs=100, batch_size=1, verbose=2)

	test = dataset[-look_back:,:]
	testX = numpy.array([test[:,0]]).reshape((1,1,look_back))
	testPredict = model.predict(testX)
	testPredict = scaler.inverse_transform(testPredict)

	return testPredict[0,:]
