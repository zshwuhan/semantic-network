'''Train a simple deep CNN on the CIFAR10 small images dataset.

GPU run command:
    THEANO_FLAGS=mode=FAST_RUN,device=gpu,floatX=float32 python cifar10_cnn.py

It gets down to 0.65 test logloss in 25 epochs, and down to 0.55 after 50 epochs.
(it's still underfitting at that point, though).

Note: the data was pickled with Python 2, and some encoding issues might prevent you
from loading it in Python 3. You might have to load it in Python 2,
save it in a different format, load it in Python 3 and repickle it.
'''


from __future__ import print_function

# if the model is not trained on all classes and must generalize
generalization = True

pretrain = False#True # if the model should load pretrained weights
#pretrain_name = 'w2v_original_rmsprop_mse_d50_e100_aTrue'
#pretrain_name = 'w2v_original_sgd_mse_d50_e501_aTrue_lr0.1_pre' # this one has 0.3021 test and .40358 train accuracy
#pretrain_name = 'w2v_original_sgd_mse_d50_e502_aTrue_lr0.1_pre' # this one has 0.3112 test and .4197 train accuracy
#pretrain_name = 'w2v_original_sgd_mse_d50_e503_aTrue_lr0.025_pre' # this one has 0.3127 test and .42788 train accuracy
#pretrain_name = 'w2v_original_sgd_mse_d50_e504_aTrue_lr0.05_pre' # this one has 0.3143 test and .43166 train accuracy
#pretrain_name = 'w2v_original_sgd_mse_d50_e1005_aTrue_lr0.05_pre' # this one has 0.3177 test and .44104 train accuracy
#pretrain_name = 'w2v_original_sgd_mse_d50_e1006_b32_aTrue_lr0.05_pre' # this one has 0.3249 test and .45256 train accuracy
pretrain_name = 'w2v_original_sgd_mse_d50_e2007_b64_aTrue_lr0.05_pre' # this one has 0.3261 test and .45982 train accuracy


batch_size = 64#128#32
training = True # if the network should train, or just load the weights from elsewhere
optimizer = 'adam'#rmsprop'#'sgd'#'rmsprop'
model_style = 'original'#'original'#'wider'#'nodrop_wider'#'original'#'wider'
nb_dim = 50#200 #TODO: try lower numbers
nb_epoch = 300#3008#200#1500
learning_rate = .3#0.05#0.5#0.01
objective='mse'#'cosine_proximity'#'mse'#'mse'
data_augmentation = True
more_augmentation = False#True
model_name = '%s_%s_%s_d%s_e%s_b%s_a%s' % (model_style, optimizer, objective, nb_dim, nb_epoch, batch_size, data_augmentation)
if more_augmentation:
    model_name += '_moreaug'
if optimizer == 'sgd':
    model_name += '_lr%s' % learning_rate
if pretrain:
    model_name += '_pre'
if generalization:
    model_name += '_gen'
gpu = 'gpu1'

import os
os.environ["THEANO_FLAGS"] = "mode=FAST_RUN,device=%s,floatX=float32" % gpu
from keras.datasets import cifar10, cifar100
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD
from keras.utils import np_utils
import cPickle as pickle
from network_utils import get_w2v_labels, accuracy_w2v
import numpy as np

# Open an IPython session if an exception is found
import sys
from IPython.core import ultratb
sys.excepthook = ultratb.FormattedTB(mode='Verbose', color_scheme='Linux', call_pdb=1)

nb_classes = 100

# input image dimensions
img_rows, img_cols = 32, 32
# the CIFAR10 images are RGB
img_channels = 3

# the data, shuffled and split between train and test sets
(X_train, y_train), (X_test, y_test) = cifar100.load_data(label_mode='fine')

# remove 1/5 of the categories from training
if generalization:
    indices = np.where(y_train % 5 != 0)[0]
    y_train = y_train[indices]
    X_train = X_train[indices]
    
    indices_test = np.where(y_test % 5 != 0)[0]
    y_test = y_test[indices_test]
    X_test = X_test[indices_test]

print('X_train shape:', X_train.shape)
print(X_train.shape[0], 'train samples')
print(X_test.shape[0], 'test samples')

# convert class vectors to w2v class matrices
Y_train = get_w2v_labels(y_train, dim=nb_dim)
Y_test = get_w2v_labels(y_test, dim=nb_dim)
print('y_train shape:', y_train.shape)
print('y_train shape:', y_train.shape)

X_train = X_train.astype('float32')
X_test = X_test.astype('float32')
X_train /= 255
X_test /= 255

print(model_name)

model = Sequential()

if model_style == 'original':

    model.add(Convolution2D(32, 3, 3, border_mode='same',
                            input_shape=(img_channels, img_rows, img_cols)))
    model.add(Activation('relu'))
    model.add(Convolution2D(32, 3, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Convolution2D(64, 3, 3, border_mode='same'))
    model.add(Activation('relu'))
    model.add(Convolution2D(64, 3, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(nb_dim))
    #model.add(Activation('softmax'))
    #TODO: might want a linear activation function here
elif model_style == 'wider':

    model.add(Convolution2D(48, 3, 3, border_mode='same',
                            input_shape=(img_channels, img_rows, img_cols)))
    model.add(Activation('relu'))
    model.add(Convolution2D(48, 5, 5))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Convolution2D(96, 3, 3, border_mode='same'))
    model.add(Activation('relu'))
    model.add(Convolution2D(96, 3, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(1024))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(nb_dim))
    #model.add(Activation('softmax'))
    #TODO: might want a linear activation function here
elif model_style == 'deeper':

    model.add(Convolution2D(32, 3, 3, border_mode='same',
                            input_shape=(img_channels, img_rows, img_cols)))
    model.add(Activation('relu'))
    model.add(Convolution2D(32, 3, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Convolution2D(64, 3, 3, border_mode='same'))
    model.add(Activation('relu'))
    model.add(Convolution2D(64, 3, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Convolution2D(96, 3, 3, border_mode='same'))
    model.add(Activation('relu'))
    model.add(Convolution2D(96, 3, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(nb_dim))
    #model.add(Activation('softmax'))
    #TODO: might want a linear activation function here
elif model_style == 'wider_activation':

    model.add(Convolution2D(48, 3, 3, border_mode='same',
                            input_shape=(img_channels, img_rows, img_cols)))
    model.add(Activation('relu'))
    model.add(Convolution2D(48, 5, 5))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Convolution2D(96, 3, 3, border_mode='same'))
    model.add(Activation('relu'))
    model.add(Convolution2D(96, 3, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(1024))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(nb_dim))
    model.add(Activation('linear'))
    #TODO: might want a linear activation function here
if model_style == 'nodrop_original':

    model.add(Convolution2D(32, 3, 3, border_mode='same',
                            input_shape=(img_channels, img_rows, img_cols)))
    model.add(Activation('relu'))
    model.add(Convolution2D(32, 3, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Convolution2D(64, 3, 3, border_mode='same'))
    model.add(Activation('relu'))
    model.add(Convolution2D(64, 3, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(512))
    model.add(Activation('relu'))
    model.add(Dense(nb_dim))
    #model.add(Activation('softmax'))
    #TODO: might want a linear activation function here
elif model_style == 'nodrop_wider':

    model.add(Convolution2D(48, 3, 3, border_mode='same',
                            input_shape=(img_channels, img_rows, img_cols)))
    model.add(Activation('relu'))
    model.add(Convolution2D(48, 5, 5))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Convolution2D(96, 3, 3, border_mode='same'))
    model.add(Activation('relu'))
    model.add(Convolution2D(96, 3, 3))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(1024))
    model.add(Activation('relu'))
    model.add(Dense(nb_dim))
    #model.add(Activation('softmax'))
    #TODO: might want a linear activation function here

if optimizer == 'sgd':
    # let's train the model using SGD + momentum (how original).
    sgd = SGD(lr=learning_rate, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss=objective, optimizer=sgd)
elif optimizer == 'rmsprop':
    model.compile(loss=objective, optimizer='rmsprop')
else:
    model.compile(loss=objective, optimizer=optimizer)

if pretrain:
    model.load_weights('net_output/%s_weights.h5' % pretrain_name)

if training:
    if not data_augmentation:
        print('Not using data augmentation.')
        history = model.fit(X_train, Y_train, batch_size=batch_size,
                  nb_epoch=nb_epoch, show_accuracy=True,
                  validation_data=(X_test, Y_test), shuffle=True)
    else:
        print('Using real-time data augmentation.')
        if more_augmentation:
            # this will do preprocessing and realtime data augmentation
            datagen = ImageDataGenerator(
                featurewise_center=True,  # set input mean to 0 over the dataset
                samplewise_center=False,  # set each sample mean to 0
                featurewise_std_normalization=True,  # divide inputs by std of the dataset
                samplewise_std_normalization=False,  # divide each input by its std
                zca_whitening=False,  # apply ZCA whitening
                rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
                width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
                height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
                horizontal_flip=True,  # randomly flip images
                vertical_flip=False)  # randomly flip images
        else:
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
        history = model.fit_generator(datagen.flow(X_train, Y_train, batch_size=batch_size),
                            samples_per_epoch=X_train.shape[0],
                            nb_epoch=nb_epoch, show_accuracy=True,
                            validation_data=(X_test, Y_test),
                            nb_worker=1)
    
    model.save_weights('net_output/w2v_%s_weights.h5' % model_name)
    json_string = model.to_json()
    open('net_output/w2v_%s_architecture.json' % model_name, 'w').write(json_string)
    if pretrain:
        history.history['pretrain_name'] = pretrain_name
    pickle.dump(history.history, open('net_output/w2v_%s_history.p' % model_name,'w'))
    print("saving to: w2v_%s" % model_name)
    """
    model.save_weights('net_output/keras_cifar100_w2v_dim_%s_weights.h5' % nb_dim)
    json_string = model.to_json()
    open('net_output/keras_cifar100_w2v_sgd_dim_%s_architecture.json' % nb_dim, 'w').write(json_string)
    pickle.dump(history.history, open('net_output/keras_cifar100_w2v_sgd_dim_%s_history.p' % nb_dim,'w'))
    print("saving to: keras_cifar100_%s" % model_name)
    """
else:
    
    model.load_weights('net_output/w2v_%s_weights.h5' % model_name)
    #model.load_weights('net_output/keras_cifar100_w2v_%s_weights.h5' % model_name)
    #model.load_weights('net_output/keras_cifar100_w2v_sgd_dim_%s_weights.h5' % nb_dim)
    Y_predict_test = model.predict(X_test, batch_size=batch_size, verbose=1)
    Y_predict_train = model.predict(X_train, batch_size=batch_size, verbose=1)
    
    test_accuracy, test_class = accuracy_w2v(Y_predict_test, Y_test)
    print("w2v test accuracy: %f" % test_accuracy)
    
    train_accuracy, train_class = accuracy_w2v(Y_predict_train, Y_train)
    print("w2v train accuracy: %f" % train_accuracy)
    
    sanity_accuracy, sanity_class = accuracy_w2v(Y_test, Y_test)
    print("w2v sanity test accuracy: %f" % sanity_accuracy)

    print(np.sum(test_class,axis=0))
    print(np.sum(train_class,axis=0))
    print(np.sum(sanity_class,axis=0))
    print(bug)
