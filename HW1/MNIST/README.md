Gradient norm is calculated for both the models in MNIST DNN.

Principal component analysis is done for MNIST DNN Model-1.

Label shuffling is done in MNIST DNN for Model-1. For getting the results for the same, you need to uncomment np.random.shuffle(y_true_batch)
line in the training of the model and also need to mention the required number of total epochs (variable for total epochs: total_epoch) above the training loop. 
