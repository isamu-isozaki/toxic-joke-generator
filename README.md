# toxic-joke-generator
I fine-tuned the 117M GPT-2 model with jokes from https://github.com/taivop/joke-dataset
# How to get up and running
- Clone this repository
- Clone https://github.com/taivop/joke-dataset and  https://github.com/nshepperd/gpt-2/tree/finetuning by going on the command line and typing
~~~
git clone https://github.com/taivop/joke-dataset.git
git clone https://github.com/nshepperd/gpt-2.git
~~~
- Put makeDatabase.py into joke-database folder and run it by
~~~
python makeDatabase.py
~~~
- This will create a database called Jokes.db and a text file called jokes.txt
- Put jokes.txt into the gpt-2 folder. Put the contents of the src folder into the gpt-2 folder directly and run the following in the gpt-2 folder
~~~
python encode.py jokes.txt jokes.txt.npz
~~~
- Replace the train.py in the gpt-2 folder with the train.py cloned from this repository.
- Zip the gpt-2 folder and upload it to google drive and create an empty folder in google drive named "autoencoder1"
- Run the colaboratory script up to and including 
~~~
!python ./train.py --dataset jokes.txt.npz --batch_size 2 --sample_every 100 --save_every 1000 --folder_id $folder_id
~~~
- The trained models will then be saved to autoencoder1
- The training can be resumed even if disconnected by running the notebook again as it downloads the models from google drive automatically.
# Sample jokes(Reader discretion advised!)
- Why are cemeteries surrounded by walls?....Because people are dying to get in there.

- What is the similarity between Princess Dianna and a cruise ship?....They both circle China, and everyone is Chinese.

- They say women don't like a man with everything.......So I went around the block with my throat pressed to see if that was the flirting I was after.

- My girlfriend told me to get something that makes her look HOT.....So I went home with a DIY candle and rubbed white alcohol all over it, and she burned her fingers.  I swear that exact spot is on my burner
