import torch
import torchvision

# from pathlib import Path
# import requests
# import pickle
# import gzip


# DATA_PATH=Path("data")
# PATH = DATA_PATH/"mnist"

# PATH.mkdir(parents=True, exist_ok=True)

# URL = "http://deeplearning.net/data/mnist/"
# FILENAME = 'mnist.pk1.gz'

# if not (PATH / FILENAME).exists():
#     content = requests.get(URL + FILENAME).content
#     (PATH/FILENAME).open("wb").write(content)


# with gzip.open((PATH/FILENAME).as_posix(), "rb") as f:
#     ((x_train, y_train), (x_valid, y_valid), _) = pickle.load(f, encoding="latin-1")


mnist_data = torchvision.datasets.MNIST('D:/download/DL/dataset/MNIST/', download=True)
data_loader = torch.utils.data.DataLoader(mnist_data,
                                          batch_size=4,
                                          shuffle=True,
                                          num_workers=1)
pass
