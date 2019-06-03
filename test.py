import os
model_name = "345M"
with open(os.path.join('models', model_name, 'vocab.bpe'), 'r', encoding="utf-8") as f:
    bpe_data = f.read()
print(tuple(bpe_data.split('\n')[1].split()))
print(tuple(bpe_data.split('\n')[2].split()))
bpe_merges = [tuple(merge_str.split()) for merge_str in bpe_data.split('\n')[1:-1]]
