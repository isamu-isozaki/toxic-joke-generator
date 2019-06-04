# Apologies
Sorry for the horrible file structure! I'll make sure to fix it.
# toxic-joke-generator
The toxic joke generator is a model that generates jokes. The reason that it is toxic is because it tends to output offensive jokes because the dataset it was trained on.
I fine-tuned the 117M GPT-2 model with jokes from https://github.com/taivop/joke-dataset. By finetuned I mean I trained the pretrained 117M GPT-2 model with additional data from  https://github.com/taivop/joke-dataset which lead it to generate jokes. Be warned, these jokes are quite dark!
# How to get up and running
- Create an empty folder in google drive named "model" and "past" to past, all the previous models including the current model will get saved and to model only the current model will be saved
- Run the colaboratory script up to and including 
~~~
!python ./train.py --dataset jokes_400_2_3.0_1.txt.npz --batch_size 2 --sample_every 100 --save_every 1000 \
--model_folder_name $model_folder_name --past_model_folder_name $past_folder_name
~~~
- The training can be resumed even if disconnected by running the notebook again as it downloads the models from google drive automatically.
# Explanation of filename
The data was created from makeDatabase.py given the name jokes_200_2_3.0_1.txt.npz
the 200 refers to the maximum length of the joke. 2 refers to the minimum upvotes to include it for jokes from r/Jokes. 3.0 refers to the minium score out of 5 to include joke from stupidstuff.org.
# How to see results
- When executing the colab notebook, execute everything except
~~~
!python ./train.py --dataset jokes.txt.npz --batch_size 2 --sample_every 100 --save_every 1000 --folder_id $folder_id
~~~
then the last cell will start generating some vile jokes!
# Sample jokes(Reader discretion advised!)
- Why are cemeteries surrounded by walls?....Because people are dying to get in there.

- What is the similarity between Princess Dianna and a cruise ship?....They both circle China, and everyone is Chinese.

- They say women don't like a man with everything.......So I went around the block with my throat pressed to see if that was the flirting I was after.

- My girlfriend told me to get something that makes her look HOT.....So I went home with a DIY candle and rubbed white alcohol all over it, and she burned her fingers.  I swear that exact spot is on my burner
# How data was gathered
- All the data is in the repository for anybody who wants to work with the original datasets.
- Download csvs from [here](https://www.kaggle.com/cuddlefish/reddit-rjokes) and [here](https://www.kaggle.com/bfinan/jokes-question-and-answer) and include the jokes_score_name_clean.csv and qajokes1.1.2.csv into the joke-dataset directory with jokes.csv from this repository. The jokes.csv came from modifying [this repository's code](https://github.com/amoudgl/short-jokes-dataset) so that it's not just short jokes.
- Put makeDatabase.py into joke-database folder and run it by
~~~
python makeDatabase.py --joke_length=200
~~~
- This will create a text file called jokes_200_3_3.0_1.txt
- Put jokes.txt into the gpt-2 folder. Put the contents of the src folder into the gpt-2 folder directly and run the following in the gpt-2 folder
~~~
python encode.py jokes.txt jokes.txt.npz
~~~
- Replace the train.py in the gpt-2 folder with the train.py cloned from this repository.
# Thanks
I'll give my sincerest thanks to 
https://www.reddit.com/r/MachineLearning/comments/bgvzdu/d_jokes_generated_via_gpt2/ for teaching me the basics of how to fine tune the model and fix encoding errors as well as the two repositories above.
https://github.com/taivop/joke-dataset
and 
https://github.com/nshepperd/gpt-2/tree/finetuning
