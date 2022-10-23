#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 15:57:08 2022

@author: edgarsicat
"""

from entry import makeEntry
import IPython
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import LSTM, Input, Dropout
from keras.layers import Dense
from keras.layers import RepeatVector
from keras.layers import TimeDistributed
from keras.models import load_model
from keras.constraints import MaxNorm
from keras.optimizers import SGD
from keras.callbacks import EarlyStopping, ReduceLROnPlateau, LearningRateScheduler
from sklearn.metrics import mean_squared_error

data = pd.read_excel("FitDataV4.xlsx", index_col="time")
RMSE = {} 

def step_decay_schedule(initial_lr=0.01, decay_factor=0.75, step_size=10):
    '''
    Wrapper function to create a LearningRateScheduler with step decay schedule.
    '''
    def schedule(epoch):
        return initial_lr * (decay_factor ** np.floor(epoch/step_size))
    
    return LearningRateScheduler(schedule)


model = Sequential()
model.add(LSTM(128, input_shape=(1, 1), return_sequences=True))

model.add(LSTM(64))

model.add(RepeatVector(1))

model.add(LSTM(64, return_sequences=True))

model.add(LSTM(128, return_sequences=True))

model.add(Dense(1))

model.compile(optimizer='adam', loss='mse')
model.summary()

lr_sched = step_decay_schedule(initial_lr=0.01, decay_factor=0.75, step_size=2)

earlyStopping = EarlyStopping(monitor='loss', patience=3)

earlyStopping2 = EarlyStopping(monitor='val_loss', patience=3)

callback = [earlyStopping, lr_sched, earlyStopping2]


for i in range(171, len(data.columns)):
    x_train = data[data.columns[i]].values
    x_train = x_train.reshape(8724, 1, 1)
    history = model.fit(
    x_train,
    x_train,
    epochs=50,
    batch_size=32,
    validation_split=0.1,
    callbacks=callback
    )
    trainPredict = model.predict(x_train)
    x_train_RMSE = x_train.reshape(8724)
    trainPredict_RMSE = trainPredict.reshape(8724)
    RMSE[str(data.columns[i])] = mean_squared_error(x_train_RMSE, trainPredict_RMSE)
    #makeEntry('log.csv', RMSE[str(data.columns[i])])
    df_mae = pd.DataFrame.from_dict([RMSE])
    df_mae.to_csv('df_maeV11.csv')