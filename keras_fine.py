# Standard labels for Cifar100 using Keras
# Matching the network structure of the Caffe network for Cifar100
# Only using the fine labels, so accuracy can be reported
from __future__ import print_function

optimizer = 'sgd'#'rmsprop'
model_style = 'original'#'original'#'wider'#'nodrop_wider'#'original'#'wider'
nb_epoch = 5#1500
learning_rate = 0.01#0.01
data_augmentation = True
more_augmentation = False#True
model_name = '%s_%s_e%s_a%s' % (model_style, optimizer, nb_epoch, data_augmentation)
if more_augmentation:
    model_name += '_moreaug'
if optimizer == 'sgd':
    model_name += '_lr%s' % learning_rate
gpu = 'gpu1'

import os
os.environ["THEANO_FLAGS"] = "mode=FAST_RUN,device=%s,floatX=float32" % gpu
from keras.datasets import cifar100
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential, Graph
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD
from keras.utils import np_utils
import cPickle as pickle
from network_utils import accuracy, load_custom_weights

# Open an IPython session if an exception is found
import sys
from IPython.core import ultratb
sys.excepthook = ultratb.FormattedTB(mode='Verbose', color_scheme='Linux', call_pdb=1)

batch_size = 32
nb_classes_fine = 100
nb_classes_coarse = 20

# input image dimensions
img_rows, img_cols = 32, 32
# the CIFAR10 images are RGB
img_channels = 3

# the data, shuffled and split between train and test sets
(X_train, y_train_fine), (X_test, y_test_fine) = cifar100.load_data(label_mode='fine')
(_, y_train_coarse), (_, y_test_coarse) = cifar100.load_data(label_mode='coarse')
print('X_train shape:', X_train.shape)
print(X_train.shape[0], 'train samples')
print(X_test.shape[0], 'test samples')
print('y_train_fine shape:', y_train_fine.shape)
print('y_train_coarse shape:', y_train_coarse.shape)

# convert class vectors to binary class matrices
Y_train_fine = np_utils.to_categorical(y_train_fine, nb_classes_fine)
Y_train_coarse = np_utils.to_categorical(y_train_coarse, nb_classes_coarse)
Y_test_fine = np_utils.to_categorical(y_test_fine, nb_classes_fine)
Y_test_coarse = np_utils.to_categorical(y_test_coarse, nb_classes_coarse)
print('Y_train_fine shape:', Y_train_fine.shape)
print('Y_train_coarse shape:', Y_train_coarse.shape)

X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_train /= 255
X_test /= 255

######################
# Beginning of Model #
######################
model = Sequential()
"""
model.add(Convolution2D(64, 4, 4, border_mode='same',
                        input_shape=(img_channels, img_rows, img_cols)))
model.add(Convolution2D(42, 1, 1))
model.add(Activation('relu'))
model.add(Convolution2D(32, 1, 1))
model.add(MaxPooling2D(pool_size=(3, 3),strides=(2,2)))
model.add(Dropout(0.25))
model.add(Activation('relu'))
model.add(Convolution2D(42, 4, 4))
model.add(MaxPooling2D(pool_size=(3, 3),strides=(2,2)))
model.add(Dropout(0.25)) #FIXME: figure out correct dropout amount
model.add(Activation('relu'))
model.add(Convolution2D(64, 2, 2))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2,2)))
model.add(Activation('relu'))
model.add(Flatten())
#inner product layer
model.add(Dense(768))
#sigmoid layer
model.add(Activation('sigmoid'))

#ip_f
model.add(Dense(100))
#accuracy_f
#loss_f
model.add(Activation('softmax'))
"""

model.add(Convolution2D(32, 3, 3, border_mode='same',
			input_shape=(img_channels, img_rows, img_cols)))
model.add(Activation('relu'))
model.add(Convolution2D(32, 3, 3))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
#model.add(Dropout(0.25))

model.add(Convolution2D(64, 3, 3, border_mode='same'))
model.add(Activation('relu'))
model.add(Convolution2D(64, 3, 3))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
#model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
#model.add(Dropout(0.5))
model.add(Dense(100))
model.add(Activation('softmax'))

training = True # if the network should train, or just load the weights from elsewhere
load_matching = False # if the network should load the weights from the model trained on both labels

if optimizer == 'sgd':
    # let's train the model using SGD + momentum (how original).
    sgd = SGD(lr=learning_rate, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', metrics=['accuracy'], optimizer=sgd)
else:
    model.compile(loss='categorical_crossentropy', metrics=['accuracy'], optimizer=optimizer)

if training:
    if not data_augmentation:
        print('Not using data augmentation.')
        history = model.fit(X_train, Y_train_fine, batch_size=batch_size,
                  nb_epoch=nb_epoch, show_accuracy=True,
                  validation_data=(X_test, Y_test_fine), shuffle=True)
    else:
        print('Using real-time data augmentation.')

        # this will do preprocessing and realtime data augmentation
        datagen = ImageDataGenerator(
            featurewise_center=False,  # set input mean to 0 over the dataset
            samplewise_center=False,  # set each sample mean to 0
            featurewise_std_normalization=False,  # divide inputs by std of the dataset
            samplewise_std_normalization=False,  # divide each input by its std
            zca_whitening=False,  # apply ZCA whitening
            rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
            width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
            height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
            horizontal_flip=True,  # randomly flip images
            vertical_flip=False)  # randomly flip images

        # compute quantities required for featurewise normalization
        # (std, mean, and principal components if ZCA whitening is applied)
        datagen.fit(X_train)

        # fit the model on the batches generated by datagen.flow()
        history = model.fit_generator(datagen.flow(X_train, Y_train_fine, batch_size=batch_size),
                            samples_per_epoch=X_train.shape[0],
                            nb_epoch=nb_epoch, show_accuracy=True,
                            validation_data=(X_test, Y_test_fine),
                            nb_worker=1)

    model.save_weights('net_output/cifar100_fine_%s_weights.h5' % model_name)
    json_string = model.to_json()
    open('net_output/cifar100_fine_%s_architecture.json' % model_name, 'w').write(json_string)
    pickle.dump(history.history, open('net_output/cifar100_fine_%s_history.p' % model_name,'w'))
    print("saving to: cifar100_fine_%s" % model_name)
elif load_matching:
    load_custom_weights(model, 'net_output/keras_cifar100_matching_weights.h5')
    Y_predict_test = model.predict(X_test, batch_size=batch_size, verbose=1)
    Y_predict_train = model.predict(X_train, batch_size=batch_size, verbose=1)
    
    test_accuracy_fine = accuracy(Y_predict_test, Y_test_fine)
    print("Fine test accuracy: %f" % test_accuracy_fine)
    
    train_accuracy_fine = accuracy(Y_predict_train, Y_train_fine)
    print("Fine train accuracy: %f" % train_accuracy_fine)
else:
    model.load_weights('cifar100_fine_%s_weights.h5' % model_name)
    Y_predict_test = model.predict(X_test, batch_size=batch_size, verbose=1)
    Y_predict_train = model.predict(X_train, batch_size=batch_size, verbose=1)
    
    Y_predict_test_fine = Y_predict_test['output_fine']
    test_accuracy_fine = accuracy(Y_predict_test_fine, Y_test_fine)
    print("Fine test accuracy: %f" % test_accuracy_fine)
    
    Y_predict_train_fine = Y_predict_train['output_fine']
    train_accuracy_fine = accuracy(Y_predict_train_fine, Y_train_fine)
    print("Fine train accuracy: %f" % train_accuracy_fine)
