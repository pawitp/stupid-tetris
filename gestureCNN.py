#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 01:01:43 2017

@author: abhisheksingh
"""

from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D, ZeroPadding2D
from keras.optimizers import SGD,RMSprop,adam
from keras.utils import np_utils

from keras import backend as K
if K.backend() == 'tensorflow':
    import tensorflow
    #K.set_image_dim_ordering('tf')
else:
    import theano
    #K.set_image_dim_ordering('th')

'''Ideally we should have changed image dim ordering based on Theano or Tensorflow, but for some reason I get following error when I switch it to 'tf' for Tensorflow.
	However, the outcome of the prediction doesnt seem to get affected due to this and Tensorflow gives me similar result as Theano.
	I didnt spend much time on this behavior, but if someone has answer to this then please do comment and let me know.
    ValueError: Negative dimension size caused by subtracting 3 from 1 for 'conv2d_1/convolution' (op: 'Conv2D') with input shapes: [?,1,200,200], [3,3,200,32].
'''
K.set_image_dim_ordering('th')
	
	
import numpy as np
#import matplotlib.pyplot as plt
import os

from PIL import Image
# SKLEARN
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
import json

import cv2
import matplotlib
#matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

# input image dimensions
img_rows, img_cols = 40, 40

# number of channels
# For grayscale use 1 value and for color images use 3 (R,G,B channels)
img_channels = 1


# Batch_size to train
batch_size = 16

## Number of output classes (change it accordingly)
## eg: In my case I wanted to predict 4 types of gestures (Ok, Peace, Punch, Stop)
## NOTE: If you change this then dont forget to change Labels accordingly
nb_classes = 4

# Number of epochs to train (change it accordingly)
nb_epoch = 7 #25

# Total number of convolutional filters to use
nb_filters = 32
# Max pooling
nb_pool = 2
# Size of convolution kernel
nb_conv = 3

#%%
#  data
path2 = './images'

WeightFileName = ["weights.hdf5"]

# outputs
output = ["NOTHING", "PAPER", "SCISSOR", "ROCK"]
#output = ["PEACE", "STOP", "THUMBSDOWN", "THUMBSUP"]

jsonarray = {}

#%%
def update(plot):
    global jsonarray
    h = 450
    y = 30
    w = 45
    font = cv2.FONT_HERSHEY_SIMPLEX

    #plot = np.zeros((512,512,3), np.uint8)
    
    #array = {"OK": 65.79261422157288, "NOTHING": 0.7953541353344917, "PEACE": 5.33270463347435, "PUNCH": 0.038031660369597375, "STOP": 28.04129719734192}
    
    for items in jsonarray:
        mul = (jsonarray[items]) / 100
        #mul = random.randint(1,100) / 100
        cv2.line(plot,(0,y),(int(h * mul),y),(255,0,0),w)
        cv2.putText(plot,items,(0,y+5), font , 0.7,(0,255,0),2,1)
        y = y + w + 30

    return plot

#%%
def modlistdir(path):
    listing = os.listdir(path)
    retlist = []
    for name in listing:
        #This check is to ignore any hidden files/folders
        if name.startswith('.'):
            continue
        retlist.append(name)
    return retlist


# Load CNN model
def loadCNN(wf_index):
    global get_output
    model = Sequential()
    
    
    model.add(Conv2D(nb_filters, (nb_conv, nb_conv),
                        padding='valid',
                        input_shape=(img_channels, img_rows, img_cols)))
    convout1 = Activation('relu')
    model.add(convout1)
    model.add(Conv2D(nb_filters, (nb_conv, nb_conv)))
    convout2 = Activation('relu')
    model.add(convout2)
    model.add(MaxPooling2D(pool_size=(nb_pool, nb_pool)))
    model.add(Dropout(0.5))

    model.add(Flatten())
    model.add(Dense(128))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(nb_classes))
    model.add(Activation('softmax'))
    
    model.compile(loss='categorical_crossentropy', optimizer='adadelta', metrics=['accuracy'])
    
    # Model summary
    model.summary()
    # Model conig details
    model.get_config()
    
    if wf_index >= 0:
        #Load pretrained weights
        fname = WeightFileName[int(wf_index)]
        print("loading ", fname)
        model.load_weights(fname)
    
    layer = model.layers[11]
    get_output = K.function([model.layers[0].input, K.learning_phase()], [layer.output,])
    
    return model

# This function does the guessing work based on input images
def guessGesture(model, img):
    global output, get_output, jsonarray
    #Load image and flatten it
    image = np.array(img).flatten()
    
    # reshape it
    image = image.reshape(img_channels, img_rows,img_cols)
    
    # float32
    image = image.astype('float32') 
    
    # normalize it
    image = image / 255
    
    # reshape for NN
    rimage = image.reshape(1, img_channels, img_rows, img_cols)
    
    # Now feed it to the NN, to fetch the predictions
    #index = model.predict_classes(rimage)
    #prob_array = model.predict_proba(rimage)
    
    prob_array = get_output([rimage, 0])[0]
    
    #print prob_array
    
    d = {}
    i = 0
    for items in output:
        d[items] = prob_array[0][i] * 100
        i += 1
    
    # Get the output with maximum probability
    import operator
    
    guess = max(d.items(), key=operator.itemgetter(1))[0]
    prob  = d[guess]

    if prob > 60.0:
        #print(guess + "  Probability: ", prob)

        #Enable this to save the predictions in a json file,
        #Which can be read by plotter app to plot bar graph
        #dump to the JSON contents to the file
        
        #with open('gesturejson.txt', 'w') as outfile:
        #    json.dump(d, outfile)
        jsonarray = d
                
        return guess

    else:
        return output[0]

#%%
def initializers():
    imlist = modlistdir(path2)
    
    image1 = np.array(Image.open(path2 +'/' + imlist[0])) # open one image to get size
    #plt.imshow(im1)
    
    m,n = image1.shape[0:2] # get the size of the images
    total_images = len(imlist) # get the 'total' number of images
    
    # create matrix to store all flattened images
    immatrix = np.array([np.array(Image.open(path2+ '/' + images).resize((img_rows, img_cols)).convert('L')).flatten()
                         for images in imlist], dtype = 'f')
    
    print(immatrix.shape)
    
    #########################################################
    ## Label the set of images per respective gesture type.
    ##
    label=np.ones((total_images,),dtype = int)
    
    for idx, filename in enumerate(imlist):
        if "nothing" in filename:
            label[idx] = 0
        elif "paper" in filename:
            label[idx] = 1
        elif "scissor" in filename:
            label[idx] = 2
        elif "rock" in filename:
            label[idx] = 3
        else:
            print("Unknown input: " + filename)
    
    data,Label = shuffle(immatrix,label, random_state=2)
    train_data = [data,Label]
     
    (X, y) = (train_data[0],train_data[1])
     
     
    # Split X and y into training and testing sets
     
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=4)
     
    X_train = X_train.reshape(X_train.shape[0], img_channels, img_rows, img_cols)
    X_test = X_test.reshape(X_test.shape[0], img_channels, img_rows, img_cols)
     
    X_train = X_train.astype('float32')
    X_test = X_test.astype('float32')
     
    # normalize
    X_train /= 255
    X_test /= 255
     
    # convert class vectors to binary class matrices
    Y_train = np_utils.to_categorical(y_train, nb_classes)
    Y_test = np_utils.to_categorical(y_test, nb_classes)
    return X_train, X_test, Y_train, Y_test

def trainModel(model):
    # Split X and y into training and testing sets
    X_train, X_test, Y_train, Y_test = initializers()

    # Now start the training of the loaded model
    hist = model.fit(X_train, Y_train, batch_size=batch_size, epochs=nb_epoch,
                 verbose=1, validation_split=0.2)

    model.save_weights("weights.hdf5", overwrite=True)

    visualizeHis(hist)

def visualizeHis(hist):
    # visualizing losses and accuracy
    train_loss=hist.history['loss']
    val_loss=hist.history['val_loss']
    train_acc=hist.history['acc']
    val_acc=hist.history['val_acc']
    xc=range(nb_epoch)

    plt.figure(1,figsize=(7,5))
    plt.plot(xc,train_loss)
    plt.plot(xc,val_loss)
    plt.xlabel('num of Epochs')
    plt.ylabel('loss')
    plt.title('train_loss vs val_loss')
    plt.grid(True)
    plt.legend(['train','val'])
    #print plt.style.available # use bmh, classic,ggplot for big pictures
    #plt.style.use(['classic'])

    plt.figure(2,figsize=(7,5))
    plt.plot(xc,train_acc)
    plt.plot(xc,val_acc)
    plt.xlabel('num of Epochs')
    plt.ylabel('accuracy')
    plt.title('train_acc vs val_acc')
    plt.grid(True)
    plt.legend(['train','val'],loc=4)

    plt.show()
