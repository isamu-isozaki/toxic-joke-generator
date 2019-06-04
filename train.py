#!/usr/bin/env python3
# Usage:
#  PYTHONPATH=src ./train --dataset <file|directory|glob>

import argparse
import json
import os
import numpy as np
import tensorflow as tf
import time

import model, sample, encoder
from load_dataset import load_dataset, Sampler
from accumulate import AccumulatingOptimizer
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials

# 1. Authenticate and create the PyDrive client.
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

CHECKPOINT_DIR = 'checkpoint'
SAMPLE_DIR = 'samples'


parser = argparse.ArgumentParser(
	description='Fine-tune GPT-2 on your custom dataset.',
	formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('--dataset', metavar='PATH', type=str, required=True, help='Input file, directory, or glob pattern (utf-8 text, or preencoded .npz files).')
parser.add_argument('--model_folder_name', metavar='MODELFOL', type=str, default='model', help='Model folder name in google drive')
parser.add_argument('--past_model_folder_name', metavar='PASTMODELFOL', type=str, default='past', help='Folder name where past models go in google drive')
parser.add_argument('--model_name', metavar='MODEL', type=str, default='117M', help='Pretrained model name')
parser.add_argument('--combine', metavar='CHARS', type=int, default=50000, help='Concatenate input files with <|endoftext|> separator into chunks of this minimum size')

parser.add_argument('--batch_size', metavar='SIZE', type=int, default=8, help='Batch size')
parser.add_argument('--learning_rate', metavar='LR', type=float, default=0.0001, help='Learning rate for Adam')
parser.add_argument('--accumulate_gradients', metavar='N', type=int, default=5, help='Accumulate gradients across N minibatches.')

parser.add_argument('--restore_from', type=str, default='latest', help='Either "latest", "fresh", or a path to a checkpoint file')
parser.add_argument('--run_name', type=str, default='run1', help='Run id. Name of subdirectory in checkpoint/ and samples/')
parser.add_argument('--sample_every', metavar='N', type=int, default=1, help='Generate samples every N steps')
parser.add_argument('--sample_length', metavar='TOKENS', type=int, default=200, help='Sample this many tokens')
parser.add_argument('--sample_num', metavar='N', type=int, default=1, help='Generate this many samples')
parser.add_argument('--save_every', metavar='N', type=int, default=250, help='Write a checkpoint every N steps')



def maketree(path):
	try:
		os.makedirs(path)
	except:
		pass
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials

# 1. Authenticate and create the PyDrive client.
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)

def ListFolder(parent, show=False):
  filelist=[]
  file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % parent}).GetList()
  for f in file_list:
    if show:
      print(f"{f['title']}, {f['id']}")
    if f['mimeType']=='application/vnd.google-apps.folder': # if folder
        if f['title'] == folder_name or f['title'] == past_folder_name:
          filelist.append({"id":f['id'],"title":f['title'], "mimeType": 'application/vnd.google-apps.folder', "list":ListFolder(f['id'])})
        else:
          for f1 in ListFolder(f['id']):
            filelist.append(f1)
    else:
        filelist.append({"id":f['id'],"title":f['title'],"mimeType":"file","title1":f['alternateLink']})
  return filelist
fl = ListFolder("root")
def main():
	args = parser.parse_args()
	enc = encoder.get_encoder(args.model_name)
	hparams = model.default_hparams()
	with open(os.path.join('models', args.model_name, 'hparams.json')) as f:
		hparams.override_from_dict(json.load(f))

	if args.sample_length > hparams.n_ctx:
		raise ValueError(
			"Can't get samples longer than window size: %s" % hparams.n_ctx)

	config = tf.ConfigProto()
	config.gpu_options.allow_growth = True
	with tf.Session(config=config) as sess:
		context = tf.placeholder(tf.int32, [args.batch_size, None])
		output = model.model(hparams=hparams, X=context)
		loss = tf.reduce_mean(
			tf.nn.sparse_softmax_cross_entropy_with_logits(
				labels=context[:, 1:], logits=output['logits'][:, :-1]))

		tf_sample = sample.sample_sequence(
			hparams=hparams,
			length=args.sample_length,
			context=context,
			batch_size=args.batch_size,
			temperature=1.0,
			top_k=40)

		train_vars = [v for v in tf.trainable_variables() if 'model' in v.name]
		if args.accumulate_gradients > 1:
			opt = AccumulatingOptimizer(
				opt=tf.train.AdamOptimizer(learning_rate=args.learning_rate),
				var_list=train_vars)
			opt_reset = opt.reset()
			opt_compute = opt.compute_gradients(loss)
			opt_apply = opt.apply_gradients()
			summary_loss = tf.summary.scalar('loss', opt_apply)
		else:
			opt_apply = tf.train.AdamOptimizer(
				learning_rate=args.learning_rate).minimize(
					loss, var_list=train_vars)
			summary_loss = tf.summary.scalar('loss', loss)

		summary_log = tf.summary.FileWriter(
			os.path.join(CHECKPOINT_DIR, args.run_name))

		saver = tf.train.Saver(
			var_list=train_vars,
			max_to_keep=1,
			keep_checkpoint_every_n_hours=2)
		sess.run(tf.global_variables_initializer())

		if args.restore_from == 'latest':
			ckpt = tf.train.latest_checkpoint(
				os.path.join(CHECKPOINT_DIR, args.run_name))
			if ckpt is None:
				# Get fresh GPT weights if new run.
				ckpt = tf.train.latest_checkpoint(
					os.path.join('models', args.model_name))
		elif args.restore_from == 'fresh':
			ckpt = tf.train.latest_checkpoint(
				os.path.join('models', args.model_name))
		else:
			ckpt = tf.train.latest_checkpoint(args.restore_from)
		print('Loading checkpoint', ckpt)
		saver.restore(sess, ckpt)

		print('Loading dataset...')
		chunks = load_dataset(enc, args.dataset, args.combine)
		data_sampler = Sampler(chunks)
		print('dataset has', data_sampler.total_size, 'tokens')
		print('Training...')

		counter = 1
		counter_path = os.path.join(CHECKPOINT_DIR, args.run_name, 'counter')
		if os.path.exists(counter_path):
			# Load the step number if we're resuming a run
			# Add 1 so we don't immediately try to save again
			with open(counter_path, 'r') as fp:
				counter = int(fp.read()) + 1
		def get_folder_id(name):
			global fl
			for i in fl:
				if i["name"] == name:
					return i['id']
		def get_children(name):
			global fl
			for i in fl:
				if i["name"] == name:
					return i.get("list", [])
		def save():
			global fl
			for content in os.listdir(os.path.join(f"./{CHECKPOINT_DIR}", args.run_name)):
				if content[0] != "e":#summary file
					os.remove(os.path.join(f"./{CHECKPOINT_DIR}", args.run_name)+"/"+content)
			maketree(os.path.join(CHECKPOINT_DIR, args.run_name))
			print(
				'Saving',
				os.path.join(CHECKPOINT_DIR, args.run_name,
							 'model-{}').format(counter))
			saver.save(
				sess,
				os.path.join(CHECKPOINT_DIR, args.run_name, 'model'),
				global_step=counter)
			with open(counter_path, 'w') as fp:
				fp.write(str(counter) + '\n')
			from pydrive.auth import GoogleAuth
			from pydrive.drive import GoogleDrive
			from google.colab import auth
			from oauth2client.client import GoogleCredentials

			# 1. Authenticate and create the PyDrive client do this every time because sometimes the client.json just dissapears.
			auth.authenticate_user()
			gauth = GoogleAuth()
			gauth.credentials = GoogleCredentials.get_application_default()
			drive = GoogleDrive(gauth)
			#Delete folders from model_folder_name
			for file in get_children(args.model_folder_name):
				f = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": file["id"]}]})
				f.Delete()
			#Upload to model_folder_name
			for content in os.listdir(os.path.join(f"./{CHECKPOINT_DIR}", args.run_name)):
				f = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": get_folder_id(args.model_folder_name)}]})
				f.SetContentFile(os.path.join(f"./{CHECKPOINT_DIR}", args.run_name)+"/"+content)
				f.Upload()
			#Upload to past_model_folder_name
			for content in os.listdir(os.path.join(f"./{CHECKPOINT_DIR}", args.run_name)):
				f = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": get_folder_id(args.past_model_folder_name)}]})
				f.SetContentFile(os.path.join(f"./{CHECKPOINT_DIR}", args.run_name)+"/"+content)
				f.Upload()
			#update folder list
			fl = ListFolder("root")

		def generate_samples():
			context_tokens = data_sampler.sample(1)
			all_text = []
			index = 0
			while index < args.sample_num:
				out = sess.run(
					tf_sample,
					feed_dict={context: args.batch_size * [context_tokens]})
				for i in range(min(args.sample_num - index, args.batch_size)):
					text = enc.decode(out[i])
					text = '======== SAMPLE {} ========\n{}\n'.format(
						index + 1, text)
					all_text.append(text)
					index += 1
			print(text)
			maketree(os.path.join(SAMPLE_DIR, args.run_name))
			with open(
					os.path.join(SAMPLE_DIR, args.run_name,
								 'samples-{}').format(counter), 'w') as fp:
				fp.write('\n'.join(all_text))

		def sample_batch():
			return [data_sampler.sample(1024) for _ in range(args.batch_size)]

		avg_loss = (0.0, 0.0)
		start_time = time.time()

		try:
			while True:
				if counter % args.save_every == 0:
					save()
				if counter % args.sample_every == 0:
					generate_samples()

				if args.accumulate_gradients > 1:
					sess.run(opt_reset)
					for _ in range(args.accumulate_gradients):
						sess.run(
							opt_compute, feed_dict={context: sample_batch()})
					(v_loss, v_summary) = sess.run((opt_apply, summary_loss))
				else:
					(_, v_loss, v_summary) = sess.run(
						(opt_apply, loss, summary_loss),
						feed_dict={context: sample_batch()})

				summary_log.add_summary(v_summary, counter)

				avg_loss = (avg_loss[0] * 0.99 + v_loss,
							avg_loss[1] * 0.99 + 1.0)

				print(
					'[{counter} | {time:2.2f}] loss={loss:2.2f} avg={avg:2.2f}'
					.format(
						counter=counter,
						time=time.time() - start_time,
						loss=v_loss,
						avg=avg_loss[0] / avg_loss[1]))

				counter += 1
		except KeyboardInterrupt:
			print('interrupted')
			save()


if __name__ == '__main__':
	main()
