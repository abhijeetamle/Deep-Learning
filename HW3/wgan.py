# -*- coding: utf-8 -*-
"""WGAN.ipynb

Automatically generated by Colaboratory.

"""


# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 1.x
import tensorflow as tf

from urllib.request import urlretrieve
import os
from os.path import isfile, isdir
from tqdm import tqdm 
import tarfile
import scipy.misc

import pickle
import numpy as np
import matplotlib.pyplot as plt
import random

tf.__version__

def one_hot_encoded(class_numbers, num_classes=None):

    # Assumes the lowest class-number is zero.
    if num_classes is None:
        num_classes = np.max(class_numbers) + 1

    return np.eye(num_classes, dtype=float)[class_numbers]

"""### Load and prepare the dataset

Downloading CIFAR-10 dataset (will download around 171MB)
"""

cifar10_dataset_folder_path = 'cifar-10-batches-py'

class DownloadProgress(tqdm):
    last_block = 0

    def hook(self, block_num=1, block_size=1, total_size=None):
        self.total = total_size
        self.update((block_num - self.last_block) * block_size)
        self.last_block = block_num

""" 
    check if the data (zip) file is already downloaded
    if not, download it from "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz" and save as cifar-10-python.tar.gz
"""
if not isfile('cifar-10-python.tar.gz'):
    with DownloadProgress(unit='B', unit_scale=True, miniters=1, desc='CIFAR-10 Dataset') as pbar:
        urlretrieve(
            'https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz',
            'cifar-10-python.tar.gz',
            pbar.hook)

if not isdir(cifar10_dataset_folder_path):
    with tarfile.open('cifar-10-python.tar.gz') as tar:
        tar.extractall()
        tar.close()

"""10 classes in CIFAR-10"""

def load_label_names():
    return ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

"""Function to load, reshape, and normalize a batch from dataset"""

def load_cfar10_batch(cifar10_dataset_folder_path, batch_id):
    with open(cifar10_dataset_folder_path + '/data_batch_' + str(batch_id), mode='rb') as file:
        
        batch = pickle.load(file, encoding='latin1')

    # reshaping the data    
    features = batch['data'].reshape((len(batch['data']), 3, 32, 32)).transpose(0, 2, 3, 1)

    # normalizing the data
    features = np.array(features, dtype=float) / 255.0

    labels = batch['labels']
        
    return features, labels


img_size = 32
num_channels = 3

# Number of classes.
num_classes = 10

# Number of files for the training-set.
num_files_train = 5

# Number of images for each batch-file in the training-set.
images_per_file = 10000

# Total number of images in the training-set.
# This is used to pre-allocate arrays for efficiency.
num_images_train = num_files_train * images_per_file

def load_training_data():

    # Pre-allocate the arrays for the images and class-numbers for efficiency.
    images = np.zeros(shape=[num_images_train, img_size, img_size, num_channels], dtype=float)
    labels = np.zeros(shape=[num_images_train], dtype=int)

    # Begin-index for the current batch.
    begin = 0
    
    # For each data-file.
    for i in range(num_files_train):
        # Load the images and class-numbers from the data-file.
        images_batch, labels_batch = load_cfar10_batch('/content/cifar-10-batches-py', str(i + 1))

        # Number of images in this batch.
        num_images = len(images_batch)

        # End-index for the current batch.
        end = begin + num_images

        # Store the images into the array.
        images[begin:end, :] = images_batch

        # Store the class-numbers into the array.
        labels[begin:end] = labels_batch

        # The begin-index for the next batch is the current end-index.
        begin = end

    return images, labels, one_hot_encoded(class_numbers=labels, num_classes=num_classes)

def load_test_data():

    images, labels = load_cfar10_batch('/content/cifar-10-batches-py/test_batch')

    return images, labels, one_hot_encoded(class_numbers=labels, num_classes=num_classes)

# parameters

input_height = 32
input_width = 32
output_height = 32
output_width = 32
channel = 3
n_noise = 64

"""##Create the model

Defining activation function leaky relu
"""

def lrelu(x, leak=0.2):

    f1 = 0.5 * (1 + leak)
    f2 = 0.5 * (1 - leak)
    return f1 * x + f2 * abs(x)

"""###The Discriminator"""

def make_discriminator_model(img_in, reuse=False, is_training=True):
        
        with tf.variable_scope("discriminator", reuse=reuse):

            weights_init=tf.truncated_normal_initializer(stddev=0.02)        

            net = lrelu(tf.layers.conv2d(inputs=img_in, filters=32, kernel_size=[5, 5], strides=2, kernel_initializer=weights_init, padding='same'))

            net = lrelu(tf.compat.v1.layers.batch_normalization(tf.layers.conv2d(inputs=net, filters=64, kernel_size=[5, 5], strides=2, kernel_initializer=weights_init, padding='same'),
                    training=is_training, momentum=0.9, epsilon=1e-5))

            net = lrelu(tf.compat.v1.layers.batch_normalization(tf.layers.conv2d(inputs=net, filters=128, kernel_size=[5, 5], strides=2, kernel_initializer=weights_init, padding='same'),
                    training=is_training, momentum=0.9, epsilon=1e-5))
            
            net = lrelu(tf.compat.v1.layers.batch_normalization(tf.layers.conv2d(inputs=net, filters=256, kernel_size=[5, 5], strides=2, kernel_initializer=weights_init, padding='same'),
                    training=is_training, momentum=0.9, epsilon=1e-5))

            flatten = tf.reshape(net, (-1, 2*2*256))

            logits = tf.layers.dense(flatten, 1, activation=None, kernel_initializer=weights_init, name='logits')

        return out

"""###The Generator"""

def make_generator_model(z, reuse=False, is_training=True):
    print('Creating generator')

    with tf.variable_scope("generator", reuse=reuse):

        weights_init=tf.truncated_normal_initializer(stddev=0.02)

        net = tf.layers.batch_normalization(
            tf.contrib.layers.fully_connected(z,  2 * 2 * 256),
            training=is_training, momentum=0.9, epsilon=1e-5)
        
        net = lrelu(net)
        
        net = tf.reshape(net, [-1, 2, 2, 256])
        
        net = tf.compat.v1.layers.batch_normalization(tf.compat.v1.layers.conv2d_transpose(net, 128, [5, 5], strides=2, kernel_initializer=weights_init, padding='same'), 
                training=is_training, momentum=0.9, epsilon=1e-5)
        
        net = lrelu(net)
        
        net = tf.compat.v1.layers.batch_normalization(tf.compat.v1.layers.conv2d_transpose(net, 64, [5, 5], strides=2, kernel_initializer=weights_init, padding='same'), 
                training=is_training, momentum=0.9, epsilon=1e-5)
        
        net = lrelu(net)

        net = tf.compat.v1.layers.batch_normalization(tf.compat.v1.layers.conv2d_transpose(net, 32, [5, 5], strides=2, kernel_initializer=weights_init, padding='same'), 
                training=is_training, momentum=0.9, epsilon=1e-5)
        
        net = lrelu(net)
        
        net = tf.compat.v1.layers.conv2d_transpose(net, 3, [5, 5], strides=2, padding='same', kernel_initializer=weights_init, activation=None) 
        net = tf.nn.tanh(net)
        return net

"""####Placeholders"""

random_dim = 100

with tf.variable_scope('input'):
        #real and fake image placholders
        real_image = tf.placeholder(tf.float32, shape = [None, input_height, input_width, channel], name='real_image')
        random_input = tf.placeholder(tf.float32, shape=[None, random_dim], name='rand_input')
        is_training = tf.placeholder(tf.bool, name='is_training')

"""###Define the loss and optimizers"""

g = make_generator_model(random_input, reuse=False, is_training=True)

d_fake = make_discriminator_model(g)

d_real = make_discriminator_model(real_image, reuse=True)

d_loss = tf.reduce_mean(d_fake) - tf.reduce_mean(d_real)
g_loss = tf.reduce_mean(d_fake)

vars_t = tf.trainable_variables()

vars_g = [var for var in tf.trainable_variables() if var.name.startswith("generator")]
vars_d = [var for var in tf.trainable_variables() if var.name.startswith("discriminator")]

trainer_d = tf.train.RMSPropOptimizer(learning_rate=2e-4).minimize(d_loss, var_list=vars_d)
trainer_g = tf.train.RMSPropOptimizer(learning_rate=2e-4).minimize(g_loss, var_list=vars_g)


# clip discriminator weights
d_clip = [v.assign(tf.clip_by_value(v, -0.01, 0.01)) for v in vars_d]

sess = tf.Session()
sess.run(tf.global_variables_initializer())

"""###Train the model"""

train_batch_size = 128

images_train, cls_train, labels_train = load_training_data()

def plot_images(images, cls_true, cls_pred=None, smooth=True):

    assert len(images) == len(cls_true) == 9

    # Create figure with sub-plots.
    fig, axes = plt.subplots(3, 3)

    # Adjust vertical spacing if we need to print ensemble and best-net.
    if cls_pred is None:
        hspace = 0.3
    else:
        hspace = 0.6
    fig.subplots_adjust(hspace=hspace, wspace=0.3)

    for i, ax in enumerate(axes.flat):
        # Interpolation type.
        if smooth:
            interpolation = 'spline16'
        else:
            interpolation = 'nearest'

        # Plot image.
        ax.imshow(images[i, :, :, :],
                  interpolation=interpolation)
            
        # Name of the true class.
        cls_true_name = class_names[cls_true[i]]

        # Show true and predicted classes.
        if cls_pred is None:
            xlabel = "True: {0}".format(cls_true_name)
        else:
            # Name of the predicted class.
            cls_pred_name = class_names[cls_pred[i]]

            xlabel = "True: {0}\nPred: {1}".format(cls_true_name, cls_pred_name)

        # Show the classes as the label on the x-axis.
        ax.set_xlabel(xlabel)
        
        # Remove ticks from the plot.
        ax.set_xticks([])
        ax.set_yticks([])
    
    # Ensure the plot is shown correctly with multiple plots
    # in a single Notebook cell.
    plt.show()

class_names = load_label_names()

# Get the first images from the test-set.
images = images_train[0:9]

# Get the true classes for those images.
cls_true = cls_train[0:9]

# Plot the images and labels using our helper-function above.
plot_images(images=images, cls_true=cls_true, smooth=False)

def random_batch():
    # Number of images in the training-set.
    num_images = len(images_train)

    # Create a random index.
    idx = np.random.choice(num_images,
                           size=train_batch_size,
                           replace=False)

    # Use the random index to select random images and labels.
    x_batch = images_train[idx, :, :, :]
    y_batch = labels_train[idx, :]

    return x_batch, y_batch

saver = tf.train.Saver()
save_path = saver.save(sess, '/content/model.ckpt')
ckpt = tf.train.latest_checkpoint('/content/model/')
saver.restore(sess, save_path)
coord = tf.train.Coordinator()
threads = tf.train.start_queue_runners(sess=sess, coord=coord)

total_epoch = 100
batch_num = int(len(images_train) / train_batch_size)
batch_num

print('start training')

for i in range(total_epoch):
        print("Running epoch {}/{}...".format(i, total_epoch))
        for j in range(batch_num):
            if j%25 == 0:
                print('current batch number: {}/{}'.format(j,batch_num))
            d_iters = 5
            g_iters = 1

            train_noise = np.random.uniform(-1.0, 1.0, size=[train_batch_size, random_dim]).astype(np.float32)
            for k in range(d_iters):

                train_image, train_label = random_batch()
                #wgan clip weights
                sess.run(d_clip)
                
                # Update the discriminator
                _, dLoss = sess.run([trainer_d, d_loss],
                                    feed_dict={random_input: train_noise, real_image: train_image, is_training: True})

            # Update the generator
            for k in range(g_iters):

                _, gLoss = sess.run([trainer_g, g_loss],
                                    feed_dict={random_input: train_noise, is_training: True})

        # save check point
        if i%5 == 0:
            if not os.path.exists('/content/model/'):
                os.makedirs('/content/model/')
            saver.save(sess, '/content/model/' + '/' + str(i))  
                  
            print('train:[%d],d_loss:%f,g_loss:%f' % (i, dLoss, gLoss))  
coord.request_stop()
coord.join(threads)



