# View Images in the CIFAR Dataset from the HDF5 format
import numpy as np
import matplotlib.pyplot as plt
import h5py
import sys
import time

fnametrain = 'data/cifar_100_caffe_hdf5/train.h5'
fnametest = 'data/cifar_100_caffe_hdf5/test.h5'

ftrain = h5py.File(fnametest, 'r')
#ftrain = h5py.File(fnametest, 'r', compression='gzip')
print(dir(ftrain))
print(ftrain.keys())
print(ftrain.values())
print(ftrain['data'])
print(ftrain['label_coarse'])
print(ftrain['label_fine'])
