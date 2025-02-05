# -*- coding: utf-8 -*-
"""regression_cos.ipynb

Automatically generated by Colaboratory.

"""

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 1.x
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
from math import sin, pi

tf.__version__

#set seed 

tf.set_random_seed(1)
np.random.seed(1)

"""# Data preparation"""

# creating fake data

x = np.linspace(-1, 1, 200)[:, np.newaxis]    # shape (200, 1)

y = (np.cos(7 * x * np.pi))

# ploting the above generated data

plt.plot(x,y)
plt.show()

"""# Creating placeholder"""

# Model 1 
input_m1_x = tf.placeholder(tf.float32, [None, 1])   # x
output_m1_y = tf.placeholder(tf.float32, [None, 1])  # y

# Model 2
input_m2_x = tf.placeholder(tf.float32, [None, 1])   # x
output_m2_y = tf.placeholder(tf.float32, [None, 1])  # y

# Model 3
input_m3_x = tf.placeholder(tf.float32, [None, 1])   # x
output_m3_y = tf.placeholder(tf.float32, [None, 1])  # y

# Keep probability 
keep_prob = tf.placeholder(tf.float32)

"""# Counting parameters"""

def count_parameters():

  total_parameters = 0
  for variable in tf.trainable_variables():
      # shape is an array of tf.Dimension
#      print(variable)
      shape = variable.get_shape()
#      print(shape)
      #print(len(shape))
      variable_parameters = 1
      for dim in shape:
          #print(dim)
          variable_parameters *= dim.value
#      print(variable_parameters)
      total_parameters += variable_parameters
  return(total_parameters)

"""# Creating layers"""

# Model 1 

h1_model_1 = tf.layers.dense(input_m1_x, units=100, activation=tf.nn.relu, name='h1_model_1')
dropout_h1_model_1 = tf.layers.dropout(h1_model_1, 0.8)
h2_model_1 = tf.layers.dense(dropout_h1_model_1, units=10, activation=tf.nn.relu, name='h2_model_1')
h3_model_1 = tf.layers.dense(h2_model_1, units=5, activation=tf.nn.relu, name='h3_model_1')
h4_model_1 = tf.layers.dense(inputs=h3_model_1, units=1, name='h4_model_1')

parameters_model_1 = count_parameters()
print(parameters_model_1)

# Model 2

h1_model_2 = tf.layers.dense(input_m2_x, units=10, activation=tf.nn.relu, name='h1_model_2')
h2_model_2 = tf.layers.dense(h1_model_2, units=10, activation=tf.nn.relu, name='h2_model_2')
dropout_h2_model_2 = tf.layers.dropout(h2_model_2, 0.5)
h3_model_2 = tf.layers.dense(dropout_h2_model_2, units=10, activation=tf.nn.relu, name='h3_model_2')
h4_model_2 = tf.layers.dense(h3_model_2, units=50, activation=tf.nn.relu, name='h4_model_2')
dropout_h4_model_2 = tf.layers.dropout(h4_model_2, 0.5)
h5_model_2 = tf.layers.dense(dropout_h4_model_2, units=6, activation=tf.nn.relu, name='h5_model_2')
h6_model_2 = tf.layers.dense(h5_model_2, units=10, activation=tf.nn.relu, name='h6_model_2')
h7_model_2 = tf.layers.dense(h6_model_2, units=5, activation=tf.nn.relu, name='h7_model_2')
h8_model_2 = tf.layers.dense(h7_model_2, units=7, activation=tf.nn.relu, name='h8_model_2')
output_layer_model_2 = tf.layers.dense(inputs=h8_model_2, units=1, name='output_layer_model_2')

parameters_model_2 = count_parameters() - parameters_model_1
print(parameters_model_2)

# Model 3

h1_model_3 = tf.layers.dense(input_m3_x, units=10, activation=tf.nn.relu, name='h1_model_3')
dropout_h1_model_3 = tf.layers.dropout(h1_model_3, 0.5)
h2_model_3 = tf.layers.dense(dropout_h1_model_3, units=44, activation=tf.nn.relu, name='h2_model_3')
h3_model_3 = tf.layers.dense(h2_model_3, units=6, activation=tf.nn.relu, name='h3_model_3')
h4_model_3 = tf.layers.dense(h3_model_3, units=25, activation=tf.nn.relu, name='h4_model_3')
dropout_h4_model_3 = tf.layers.dropout(h4_model_3, 0.5)
h5_model_3 = tf.layers.dense(dropout_h4_model_3, units=10, activation=tf.nn.relu, name='h5_model_3')
h6_model_3 = tf.layers.dense(h5_model_3, units=5, activation=tf.nn.relu, name='h6_model_3')
output_layer_model_3 = tf.layers.dense(inputs=h6_model_3, units=1, name='output_layer_model_3')


parameters_model_3 = count_parameters() - parameters_model_1 - parameters_model_2
print(parameters_model_3)

"""# Defining Loss function"""

loss_model_1 = tf.losses.mean_squared_error(output_m1_y, h4_model_1)

loss_model_2 = tf.losses.mean_squared_error(output_m2_y, output_layer_model_2)

loss_model_3 = tf.losses.mean_squared_error(output_m3_y, output_layer_model_3)

"""# Optimization method"""

optimizer_model_1 = tf.train.GradientDescentOptimizer(learning_rate=0.093)
grads_and_vars_model_1 = optimizer_model_1.compute_gradients(loss_model_1)
train_op_model_1 = optimizer_model_1.apply_gradients(grads_and_vars_model_1)

optimizer_model_2 = tf.train.GradientDescentOptimizer(learning_rate=0.075)
train_op_model_2 = optimizer_model_2.minimize(loss_model_2)

optimizer_model_3 = tf.train.GradientDescentOptimizer(learning_rate=0.0004)
train_op_model_3 = optimizer_model_2.minimize(loss_model_3)

"""### Getting weights"""

print (tf.trainable_variables())

# Function for getting weights from the network
def get_weights_variable(layer_name):

    with tf.variable_scope(layer_name, reuse=True):
        variable = tf.get_variable('kernel')

    return variable

# Model 1

weights_m1_fc1 = get_weights_variable(layer_name='h1_model_1')
print(weights_m1_fc1)

weights_m1_fc2 = get_weights_variable(layer_name='h2_model_1')
print(weights_m1_fc2)

weights_m1_fc3 = get_weights_variable(layer_name='h3_model_1')
print(weights_m1_fc3)

weights_m1_fc4 = get_weights_variable(layer_name='h4_model_1')
print(weights_m1_fc4)

"""# Creating TensorFlow session"""

sess = tf.Session()

"""# Initializing variables"""

sess.run(tf.global_variables_initializer())

"""### Getting Gradients"""

grads = tf.gradients(loss_model_1, weights_m1_fc4)[0]
print(grads)

"""### Computing Hessian"""

hessian = tf.reduce_sum(tf.hessians(loss_model_1, weights_m1_fc4)[0], axis = 2)
print(hessian)

"""# Training the models"""

epoch_arr, loss_arr_1, loss_arr_2, loss_arr_3, grads_vals_arr, tmp_arr = [], [], [], [], [], []
max_epoch = 1000

"""**Training Model 1**"""

epoch_m1 = 0
epoch_arr_m1 = []

converged_m1 = False
while not converged_m1:

  epoch_m1 +=1

  # Total 200 values in the dataset
  for i in range(200): 

    # Training the model for all 200 values 
    _, l_1, pred_model_1 = sess.run([train_op_model_1, loss_model_1, h4_model_1], feed_dict={input_m1_x: x, output_m1_y: y, keep_prob: 0.5})
  
  # Storing loss and epoch for further plotting
  epoch_arr_m1.append(epoch_m1)
  loss_arr_1.append(l_1)

  # Printing epoch and loss after every 50 epochs 
  if epoch_m1 % 50 == 0:
    print('Epoch: {}  Loss Model 1: {}'.format(epoch_m1, l_1))

  # First condition for convergence: model should not train after reaching maximum epoch number
  if epoch_m1 >= max_epoch:
    converged_m1 = True
    print('\nModel 1 Max epoch reached')

  # Sencond condition for convergence: differnece in loss should not be less than 1.0e-05
  if (epoch_m1 > 5) and (loss_arr_1[-1] < 0.001):
    if abs(loss_arr_1[-1] - loss_arr_1[-2]) < 1.0e-05:
      if abs(loss_arr_1[-2] - loss_arr_1[-3]) < 1.0e-05:
        converged_m1 = True
        print('\nModel 1 training stopped due to overfitting')

print('\nModel 1: Training completed\n')
print('Epoch: {}  Loss Model 1: {}'.format(epoch_m1, l_1))

"""**Training Model 2**"""

epoch_m2 = 0
epoch_arr_m2 = []

converged_m2 = False
while not converged_m2:

  epoch_m2 +=1

  # Total 200 values in the dataset
  for i in range(200):

    # Training the model for all 200 values 
    _, l_2, pred_model_2 = sess.run([train_op_model_2, loss_model_2, output_layer_model_2], feed_dict={input_m2_x: x, output_m2_y: y, keep_prob: 0.5})
  
  # Storing epoch and loss for further plotting
  epoch_arr_m2.append(epoch_m2)
  loss_arr_2.append(l_2)

  # Printing epoch and loss after every 50 epochs 
  if epoch_m2 % 50 == 0:
    print('Epoch: {}  Loss Model 2: {}'.format(epoch_m2, l_2))

  # First condition for convergence: model should not train after reaching maximum epoch number
  if epoch_m2 >= max_epoch:
    converged_m2 = True
    print('Model 2 Max epoch reached')

  # Sencond condition for convergence: differnece in loss should not be less than 1.0e-05
  if (epoch_m2 > 5) and (loss_arr_2[-1] < 0.001):
    if abs(loss_arr_2[-1] - loss_arr_2[-2]) < 1.0e-05:
      if abs(loss_arr_2[-2] - loss_arr_2[-3]) < 1.0e-05:
        converged_m2 = True
        print('\nModel 2 training stopped due to overfitting')

print('\nModel 2: Training completed\n')
print('Epoch: {}  Loss Model 2: {}'.format(epoch_m2, l_2))

"""**Training Model 3**"""

epoch_m3 = 0
epoch_arr_m3 = []

converged_m3 = False
while not converged_m3:

  epoch_m3 +=1

  # Total 200 values in the dataset
  for i in range(200):

    # Training the model for all 200 values 
    _, l_3, pred_model_3 = sess.run([train_op_model_3, loss_model_3, output_layer_model_3], feed_dict={input_m3_x: x, output_m3_y: y, keep_prob: 0.5})
  
  # Storing epoch and loss for further plotting
  epoch_arr_m3.append(epoch_m3)
  loss_arr_3.append(l_3)

  # Printing epoch and loss after every 50 epochs 
  if epoch_m3 % 50 == 0:
    print('Epoch: {}  Loss Model 3: {}'.format(epoch_m3, l_3))

  # First condition for convergence: model should not train after reaching maximum epoch number
  if epoch_m3 >= max_epoch:
    converged_m3 = True
    print('Model 3 Max epoch reached')

  # Sencond condition for convergence: differnece in loss should not be less than 1.0e-05
  if (epoch_m3 > 5) and (loss_arr_3[-1] < 0.001):
    if abs(loss_arr_3[-1] - loss_arr_3[-2]) < 1.0e-05:
      if abs(loss_arr_3[-2] - loss_arr_3[-3]) < 1.0e-05:
        converged_m3 = True
        print('\nModel 3 training stopped due to overfitting')

print('\nModel 3: Training completed\n')
print('Epoch: {}  Loss Model 3: {}'.format(epoch_m3, l_3))

"""## Plotting graph"""

# Model predictions and ground-truth

plt.cla()
plt.plot(x, pred_model_1, 'r', label='Model 1')
plt.plot(x, pred_model_2, 'g', label='Model 2')
plt.plot(x, pred_model_3, 'b', Label='Model 3')
plt.plot(x,y, 'k', label='Model')
plt.title('Model Predictions')
plt.legend()
plt.show()

# Training loss vs epochs

plt.plot(epoch_arr_m1, loss_arr_1, 'r', label = "Model 1 Total Epoch: {}".format(epoch_m1))
plt.plot(epoch_arr_m2, loss_arr_2, 'g', label="Model 2 Total Epoch: {}".format(epoch_m2))
plt.plot(epoch_arr_m3, loss_arr_3, 'b', label="Model 3 Total Epoch: {}".format(epoch_m3))
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show();

