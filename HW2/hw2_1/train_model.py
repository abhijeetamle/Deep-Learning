# -*- coding: utf-8 -*-
"""train_playground.ipynb

Automatically generated by Colaboratory.

"""

# Commented out IPython magic to ensure Python compatibility.
%tensorflow_version 1.x
import tensorflow as tf
import pandas as pd
import numpy as np
import os
import sys
import time
import json
import random
import pickle

tf.__version__

from model import Seq2Seq_Model

def padding_seq(sequences, maxlen=None):
    
    dtype='int32'
    truncating='pre'
    value=0.
   
    lengths = []
    for x in sequences:
        lengths.append(len(x))

    num_samples = len(sequences)

    if maxlen is None:
        maxlen = np.max(lengths)

    # take the sample shape from the first non empty sequence
    # checking for consistency in the main loop below.
    sample_shape = tuple()
    for s in sequences:
        if len(s) > 0:
            sample_shape = np.asarray(s).shape[1:]
            break

    x = (np.ones((num_samples, maxlen) + sample_shape) * value).astype(dtype)
    for idx, s in enumerate(sequences):
        if not len(s):
            continue  # empty list/array was found
        if truncating == 'pre':
            trunc = s[-maxlen:]
        trunc = np.asarray(trunc, dtype=dtype)
        x[idx, :len(trunc)] = trunc       

    return x

if __name__ == "__main__":

    np.random.seed(9487)
    random.seed(9487)
    tf.set_random_seed(9487)

    max_decoder_steps=15
    max_encoder_steps=64
    batch_size=55
    training_sample_size=1450
    video_frame_dim=80
    total_epoch=200

    model_dir="/content/drive/My Drive/Deep_Learning/Training1/models4/"

    word2index = pickle.load(open('/content/drive/My Drive/Deep_Learning/Training1/word2index.obj', 'rb'))
    index2word = pickle.load(open('/content/drive/My Drive/Deep_Learning/Training1/index2word.obj', 'rb'))
    video_IDs = pickle.load(open('/content/drive/My Drive/Deep_Learning/Training1/video_IDs.obj', 'rb'))
    video_caption_dict = pickle.load(open('/content/drive/My Drive/Deep_Learning/Training1/video_caption_dict.obj', 'rb'))
    video_feat_dict = pickle.load(open('/content/drive/My Drive/Deep_Learning/Training1/video_feat_dict.obj', 'rb'))
    index2word_series = pd.Series(index2word)

    print('Reading completed for pickle files.')

    with tf.Session() as sess:
        model = Seq2Seq_Model(
            rnn_size=1024, 
            num_layers=2, 
            dim_video_feat=4096, 
            embedding_size=1024, 
            learning_rate=0.0001, 
            word_to_idx=word2index, 
            max_gradient_norm=5.0, 
            max_encoder_steps=64, 
            max_decoder_steps=15
        )
        ckpt = tf.train.get_checkpoint_state(model_dir)
        if ckpt and tf.train.checkpoint_exists(ckpt.model_checkpoint_path):
            print("Reloading saved model's parameters.")
            model.saver.restore(sess, ckpt.model_checkpoint_path)
        else:
            print('Creating new model parameters')
            sess.run(tf.global_variables_initializer())

        summary_writer = tf.summary.FileWriter('/content/drive/My Drive/Deep_Learning/Training1/models4/', graph=sess.graph)

        total_training_time = time.time()

        for epoch in range(total_epoch):
            start_time = time.time()

            # Random sample ID_caption.
            sampled_ID_caption = []
            for ID in video_IDs:
                sampled_caption = random.sample(video_caption_dict[ID], 1)[0]
                sampled_video_frame = sorted(random.sample(range(video_frame_dim), max_encoder_steps))
                sampled_video_feat = video_feat_dict[ID][sampled_video_frame]
                sampled_ID_caption.append((sampled_video_feat, sampled_caption))

            # Random shuffle training set 
            random.shuffle(sampled_ID_caption)

            for batch_start, batch_end in zip(range(0, training_sample_size, batch_size), range(batch_size, training_sample_size, batch_size)):
                print ("%04d/%04d" %(batch_end, training_sample_size), end='\r')

                batch_sampled_ID_caption = sampled_ID_caption[batch_start : batch_end]
                batch_video_feats = [elements[0] for elements in batch_sampled_ID_caption]
                batch_video_frame = [max_decoder_steps] * batch_size
                
                batch_captions = np.array(["<bos> "+ elements[1] for elements in batch_sampled_ID_caption])

                for index, caption in enumerate(batch_captions):
                    caption_words = caption.lower().split(" ")
                    if len(caption_words) < max_decoder_steps:
                        batch_captions[index] = batch_captions[index] + " <eos>"
                    else:
                        new_caption = ""
                        for i in range(max_decoder_steps - 1):
                            new_caption = new_caption + caption_words[i] + " "
                        batch_captions[index] = new_caption + "<eos>"

                batch_captions_words_index = []
                for caption in batch_captions:
                    words_index = []
                    for caption_words in caption.lower().split(' '):
                        if caption_words in word2index:
                            words_index.append(word2index[caption_words])
                        else:
                            words_index.append(word2index['<unk>'])
                    batch_captions_words_index.append(words_index)

                batch_captions_matrix = padding_seq(batch_captions_words_index, maxlen=max_decoder_steps)
                
                batch_captions_length = [len(x) for x in batch_captions_matrix]
               
                loss, summary = model.train(
                    sess, 
                    batch_video_feats, 
                    batch_video_frame, 
                    batch_captions_matrix, 
                    batch_captions_length)
            

            model.saver.save(sess, '/content/drive/My Drive/Deep_Learning/Training1/models4/model', global_step=epoch+1)
            print ("Epoch %d/%d, loss: %.6f, Elapsed time: %.2fs" %(epoch+1, total_epoch, loss, (time.time() - start_time)))

        print('Total training time: %.2fm' %((time.time() - total_training_time)/60))

