"""
Test the dataset api
"""

import tensorflow as tf

X = tf.range(10)
dataset = tf.data.Dataset.from_tensor_slices(X)
print(dataset)

# range from api
dataset2 = tf.data.Dataset.range(10)

# repeat
dataset2 = dataset.repeat(3).batch(7, drop_remainder=True)

dataset2 = dataset2.apply(tf.data.experimental.unbatch())

# map
dataset2 = dataset.map(lambda x: x * 2)

# filter
dataset2 = dataset.filter(lambda x: x < 5)

#shuffle
dataset2 = dataset.shuffle(buffer_size=2, reshuffle_each_iteration=False).repeat(2)

# for item in dataset2:
#     # print("*"*20)
#     print(item)

# for item in dataset2.take(3):
#     print("*"*20)
#     print(item)


# for i in range(10):
#     file_name = "interleave_{:02}.txt".format(i+1)
#     with open(file_name, "w") as fp:
#         fp.write("house_age, houseValue\n")
#         for j in range(5):
#             fp.write("{:8}, {:8}\n".format(i*5+j, i*5+j))

train_filepaths = "interleave_*.txt"
file_path_dataset = tf.data.Dataset.list_files(train_filepaths, shuffle=False)
# file_path_dataset = tf.data.Dataset.list_files(train_filepaths)

# for item in file_path_dataset:
#     print(item)

# for item in tf.data.TextLineDataset('interleave_01.txt').skip(1):
#     print(item)

# n_readers = 5
# dataset = file_path_dataset.interleave(lambda filepath: tf.data.TextLineDataset(filepath).skip(1), cycle_length=5)
# for item in dataset:
#     print(item)

data = [tf.data.Dataset.range(i*5, (i+1)*5) for i in range(10)]
dataset = tf.data.Dataset.from_tensor_slices(data)
# for item in dataset:
#     print(item)

# dataset2 = dataset.interleave(lambda x: x, cycle_length=5)
# for item in dataset2:
#     print(item)

dataset2 = tf.data.Dataset.from_tensors((range(10), range(10)))
print(len(dataset2))
for item in dataset2:
    print(item)