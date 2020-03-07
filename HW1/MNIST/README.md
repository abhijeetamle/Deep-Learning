All the required results will be shown on the console after executing the .py files.

Gradient norm is calculated for both the models in MNIST DNN only.

Label shuffling is done only in MNIST DNN for Model 1. For getting the results for the same, you need to uncomment np.random.shuffle(y_true_batch)
line in the training of the model and also need to mention the required number of total epochs (variable for total epochs: total_epoch) above the training loop. 

Graph for training and testing, loss and epochs will be generated at the end of the code.
