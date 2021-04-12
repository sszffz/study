import torch
import numpy as np

# three ways to generator tensor

# 1. user constructor
# torch allocate memory. But does not initialize it. call zero_() to initialize it
a0: torch.Tensor = torch.FloatTensor(3, 2)
a0.zero_()
print(a0, type(a0))

# use python iterator
a1 = torch.FloatTensor([[1, 2, 3], [3, 2, 1]])
print(a1)

# 2 convert from a numpy array
n = np.zeros(shape=(3, 2), dtype=np.float32)
a2 = torch.tensor(n)
print(a2)

########################
# operation
b0 = torch.tensor([1, 2, 3])
s = b0.sum()
print(s.item())

b1 = torch.tensor([1, -2, 3])
# b1.abs_()
b1.abs()
print(b1)


#########################
# cuda
print("is cuda available: ", torch.cuda.is_available())
c0 = torch.FloatTensor([2, 3])
c1 = c0.to("cuda:0")
print(c1)


print("Stop")