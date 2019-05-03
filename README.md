# toxic-joke-generator
I fine-tuned the 117M GPT-2 model with jokes from https://github.com/taivop/joke-dataset
# How to just generate some short jokes
- Download the autoencoder1-short_joke.zip and extract it.
- Create a folder in google drive called autoencoder1.
- Put the contents of autoencoder1-short_joke into autoencoder1.
- Execute all cells in the colab notebook except the cell containing the code 
~~~
!python ./train.py --dataset jokes.txt.npz --batch_size 2 --sample_every 100 --save_every 1000 --folder_id $folder_id
~~~
- The last cell will start generating jokes!
# How to train model more
- Run 
~~~
!python ./train.py --dataset jokes.txt.npz --batch_size 2 --sample_every 100 --save_every 1000 --folder_id $folder_id
~~~
in the colab notebook as well as all the cells above in additon to the first three steps of previous section.
