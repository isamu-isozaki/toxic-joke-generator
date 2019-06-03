#!/usr/bin/env python3

import fire
import json
import os
import numpy as np
import tensorflow as tf

import model, sample, encoder

from tensorflow.python.saved_model import builder as saved_model_builder
from tensorflow.python.saved_model import signature_constants
from tensorflow.python.saved_model import signature_def_utils
from tensorflow.python.saved_model import tag_constants
from tensorflow.python.saved_model import utils
from tensorflow.python.util import compat




def export_model(
    model_name='117M',
    seed=None,
    nsamples=0,
    batch_size=1,
    length=None,
    top_k=0,
    version=1,
    folder_id=None,
):
    """
    Run the sample_model
    :model_name=117M : String, which model to use
    :seed=None : Integer seed for random number generators, fix seed to
     reproduce results
    :nsamples=0 : Number of samples to return, if 0, continues to
     generate samples indefinately.
    :batch_size=1 : Number of batches (only affects speed/memory).
    :length=None : Number of tokens in generated text, if None (default), is
     determined by model hyperparameters
    :top_k=0 : Integer value controlling diversity. 1 means only 1 word is
     considered for each step (token), resulting in deterministic completions,
     while 40 means 40 words are considered at each step. 0 (default) is a
     special setting meaning no restrictions. 40 generally is a good value.
     :version=1 : Integer value giving the version the model is exported as.
     :folder_id=None : If the google drive is being used, specify the folder to upload here. Otherwise, keep as None
    :
    """
    enc = encoder.get_encoder(model_name)
    hparams = model.default_hparams()
    with open(os.path.join('models', model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if length is None:
        length = hparams.n_ctx
    elif length > hparams.n_ctx:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.Session(graph=tf.Graph()) as sess:
        np.random.seed(seed)
        tf.set_random_seed(seed)
        temperature = tf.placeholder("float", [1])
        output_tensor = sample.sample_sequence(
            hparams=hparams, length=length,
            start_token=enc.encoder['<|endoftext|>'],
            batch_size=batch_size,
            temperature=temperature, top_k=top_k
        )[:, 1:]

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join('models', model_name))
        saver.restore(sess, ckpt)

        def export_model(path):#Thanks Siraj! Couldn't have done it without you!
            #Link is https://github.com/llSourcell/How-to-Deploy-a-Tensorflow-Model-in-Production/blob/master/custom_model.py
            print("Exporting trained model to ", path)
            builder = saved_model_builder.SavedModelBuilder(path)
            input_temperature = utils.build_tensor_info(temperature)
            output = utils.build_tensor_info(output_tensor)
            prediction_signature = signature_def_utils.build_signature_def(
              inputs={'temperature': input_temperature},
              outputs={'output': output},
              method_name=signature_constants.PREDICT_METHOD_NAME)
            builder.add_meta_graph_and_variables(
              sess, [tf.saved_model.tag_constants.SERVING],
              signature_def_map={
                   'predict':
                       prediction_signature
              },
              main_op=tf.tables_initializer())
            builder.save()
        base_directory = "./export_model"
        export_path = f"./export_model/{version}"
        export_model(export_path)
        if(folder_id != None):
            from pydrive.auth import GoogleAuth
            from pydrive.drive import GoogleDrive
            from google.colab import auth
            from oauth2client.client import GoogleCredentials

            # 1. Authenticate and create the PyDrive client.
            auth.authenticate_user()
            gauth = GoogleAuth()
            gauth.credentials = GoogleCredentials.get_application_default()
            drive = GoogleDrive(gauth)
            for content in os.listdir(export_path):
                f = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": folder_id}]})
                f.SetContentFile(f"{export_path}"+"/"+content)
                f.Upload()

if __name__ == '__main__':
    fire.Fire(export_model)
