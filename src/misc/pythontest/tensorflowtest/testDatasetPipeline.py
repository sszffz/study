"""
https://www.tensorflow.org/guide/data

"""
import random

import tensorflow as tf
import pathlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

np.set_printoptions(precision=4)


def _main0_7():
    dataset = tf.data.Dataset.from_tensor_slices([8, 3, 0, 8, 2, 1])
    print(dataset)

    # for item in dataset:
    #     print(item)

    it = iter(dataset)
    print(next(it).numpy())

    print(dataset.reduce(0, lambda state, value: state + value).numpy())

    spec = tf.RaggedTensorSpec(shape=[None, None], dtype=tf.int32)

    @tf.function(input_signature=[spec])
    def double(x):
        return x * 2

    #
    # print(double(tf.ragged.constant([[1, 2, 3], [3]])))
    # tf.RaggedTensor([[1, 2, 3], [3]], row_partition=)

    dataset1 = tf.data.Dataset.from_tensor_slices(tf.random.uniform([4, 10]))
    print(dataset1.element_spec)
    for item in dataset1:
        print(item)

    dataset2 = tf.data.Dataset.from_tensor_slices((tf.random.uniform([4]), tf.random.uniform([4, 10], maxval=100)))
    print("dataset2 length: ", dataset2.element_spec, len(dataset2))
    for item in dataset2:
        print(item)

    dataset3 = tf.data.Dataset.zip((dataset1, dataset2))
    print("*" * 20)
    print('dataset 3 length: ', len(dataset3))
    print('dataset3 element spec: ', dataset3.element_spec)
    for item1, (item2, item3) in dataset3:
        print("*" * 10)
        print(item1.numpy())
        print(item2.numpy())
        print(item3.numpy())

    # dataset contain sparse matrix
    sparse_tensor = tf.SparseTensor(indices=[[0, 0], [1, 2]], values=[1.0, 2.0], dense_shape=[3, 4])
    print(sparse_tensor)
    dataset4 = tf.data.Dataset.from_tensors(sparse_tensor)
    print("dataset4 length: ", len(dataset4))
    print("dataset4 element spec: ", dataset4.element_spec)

    print("*" * 20 + " dataset 5 " + "*" * 20)
    train, test = tf.keras.datasets.fashion_mnist.load_data()
    images, labels = train
    images = tf.cast(images / 255, tf.float32)
    print(images.shape)
    datasets5 = tf.data.Dataset.from_tensor_slices((images, labels))
    print("len: ", len(datasets5))
    print("spec: ", datasets5.element_spec)

    print("*" * 20 + " dataset 6 " + "*" * 20)

    def count(stop):
        i = 0
        while i < stop:
            yield i
            i += 1

    # print(len(list(count(10))))
    # for n in count(5):
    #     print(n)

    dataset6 = tf.data.Dataset.from_generator(generator=count, args=[25], output_types=tf.int32, output_shapes=())
    # print("len: ", len(dataset6))
    print("spec: ", dataset6.element_spec)
    # for item in dataset6:
    #     print(item)

    for item in dataset6.repeat().batch(10).take(count=10):
        print(item)

    print("*" * 20 + " dataset 7 " + "*" * 20)

    def var_size_gen():
        i = 0
        while True:
            size = random.randint(0, 10)
            yield i, np.random.normal(size=size)
            i += 1

    # for i, series in var_size_gen():
    #     print(series)
    #     if i > 5:
    #         break

    dataset7 = tf.data.Dataset.from_generator(var_size_gen, output_types=(tf.int32, tf.float32),
                                              output_shapes=((), (None,)))
    print("spec: ", dataset7.element_spec)

    # specify padded shape
    # https://stackoverflow.com/questions/49840100/tf-data-dataset-padded-batch-pad-differently-each-feature
    dataset7_1 = dataset7.shuffle(20).padded_batch(3, padded_shapes=((), (10,)))
    for item in dataset7_1.take(3):
        print(item)

    print("*" * 20 + " dataset 8 " + "*" * 20)
    train, test = tf.keras.datasets.fashion_mnist.load_data()
    train_x, train_y = train
    train_x = np.expand_dims(train_x, axis=3)
    train_y = tf.keras.utils.to_categorical(train_y)
    # image_gen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1.0/255, rotation_range=20)
    image_gen = tf.keras.preprocessing.image.ImageDataGenerator()
    dataset8 = tf.data.Dataset.from_generator(lambda: image_gen.flow(train_x, train_y),
                                              output_types=(tf.float32, tf.int32),
                                              output_shapes=((None, None, None), ()))
    print(dataset8)
    # image, label = next(dataset8)
    # print(image, label)
    for item in dataset8.take(2):
        print(item)


def _main8():
    flowers = tf.keras.utils.get_file('flower_photos',
                                      'https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz',
                                      untar=True)
    img_gen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1.0/255, rotation_range=20)
    # images, labels = next(img_gen.flow_from_directory(flowers))
    # print(images.dtype, images.shape)
    # print(labels.dtype, labels.shape)
    # plt.imshow(images[0, :, :, :])
    # plt.show()
    ds = tf.data.Dataset.from_generator(lambda: img_gen.flow_from_directory(flowers),
                                        output_types=(tf.float32, tf.float32),
                                        output_shapes=([32, 256, 256, 3], [32, 5]))
    print(ds.element_spec)


def _main9():
    fsns_test_file = tf.keras.utils.get_file('fsns.tfrec', "https://storage.googleapis.com/download.tensorflow.org/data/fsns-20160927/testdata/fsns-00000-of-00001")
    dataset = tf.data.TFRecordDataset(filenames=[fsns_test_file])
    # for item in dataset:
    #     print(item)
    print(dataset.element_spec)
    raw_example = next(iter(dataset))
    parsed = tf.train.Example.FromString(raw_example.numpy())
    print(parsed.features.feature['image/text'])


def _main10():
    directory_url = 'https://storage.googleapis.com/download.tensorflow.org/data/illiad/'
    file_names = ['cowper.txt', 'derby.txt', 'butler.txt']
    file_paths = [tf.keras.utils.get_file(file_name, directory_url+file_name) for file_name in file_names]
    dataset = tf.data.TextLineDataset(file_paths)
    # for line in dataset.take(5):
    #     print(line)

    files_ds = tf.data.Dataset.from_tensor_slices(file_paths)
    lines_ds = files_ds.interleave(tf.data.TextLineDataset, cycle_length=3)
    for i, line in enumerate(lines_ds.take(9)):
        if i % 3 == 0:
            print()
        print(line.numpy())


def _main11():
    def survived(line):
        return tf.not_equal(tf.strings.substr(line, 0, 1), "0")
    titanic_file = tf.keras.utils.get_file("train.csv", "https://storage.googleapis.com/tf-datasets/titanic/train.csv")
    titanic_lines = tf.data.TextLineDataset(titanic_file)
    # for item in titanic_lines:
    #     print(item)
    # print(titanic_lines.element_spec)

    # survivors = titanic_lines.skip(1).filter(survived)
    # survivors = titanic_lines.skip(1).filter(lambda line: tf.not_equal(tf.strings.substr(line, 0, 1), "0"))
    # for item in survivors:
    #     print(item)
    # print(titanic_lines.element_spec)

    # df = pd.read_csv(titanic_file)
    # # print(df.head())
    # titanic_slices = tf.data.Dataset.from_tensor_slices(dict(df))
    # for feature_batch in titanic_slices.take(3):
    #     for key, value in feature_batch.items():
    #         print("  {!r:20s}: {}".format(key, value))

    # titanic_batches = tf.data.experimental.make_csv_dataset(
    #     titanic_file, batch_size=4, label_name="survived",
    #     select_columns=['class', 'fare', 'survived'])
    #
    # for feature_batch, label_batch in titanic_batches.take(1):
    #     print("survived: {}".format(label_batch))
    #     print("features:")
    #     for key, value in feature_batch.items():
    #         print("  {!r:20s}: {}".format(key, value))

    titanic_types = [tf.int32, tf.string, tf.float32, tf.int32, tf.int32, tf.float32, tf.string, tf.string, tf.string,
                     tf.string]
    dataset = tf.data.experimental.CsvDataset(titanic_file, titanic_types, header=True)

    for line in dataset.take(10):
        print([item.numpy() for item in line])


def _main12():
    # record_defaults = [999, 999, 999, 999]
    # dataset = tf.data.experimental.CsvDataset(r'C:\Users\yunfe\.keras\datasets\missing.csv', record_defaults)
    # # print(dataset.element_spec)
    # dataset = dataset.map(lambda *items: tf.stack(items))
    # print(dataset)
    # print(dataset.element_spec)
    # for line in dataset:
    #     print(line.numpy())

    record_defaults = [999, 999]
    dataset = tf.data.experimental.CsvDataset(
        r'C:\Users\yunfe\.keras\datasets\missing.csv', record_defaults=record_defaults, select_cols=[1, 3])
    dataset = dataset.map(lambda *items: tf.stack(items))
    print(dataset.element_spec)
    for item in dataset:
        print(item)


def _main13():
    flowers_root = tf.keras.utils.get_file(
        'flower_photos',
        'https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz',
        untar=True)
    flowers_root = pathlib.Path(flowers_root)
    for item in flowers_root.glob("*"):
        print(item.name)
    print()
    list_ds = tf.data.Dataset.list_files(str(flowers_root/'*/*'))
    for f in list_ds.take(5):
        print(f.numpy())


if __name__ == '__main__':
    # _main0_7()
    # _main8()
    # _main9()
    # _main10()
    # _main11()
    # _main12()
    _main13()