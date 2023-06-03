import torch
import torch.nn as nn

l = nn.Linear(2, 5)
v = torch.FloatTensor([1, 2])
res = l(v)
print(res)

pass