from re import X
import torch
import imageio


# class MyDecisionGate(torch.nn.Module):
#     def forward(self, x):
#         if x.sum() > 0:
#             return x
#         else:
#             return -x

# class MyCell(torch.nn.Module):
#     def __init__(self, dg):
#         super(MyCell, self).__init__()
#         # self.dg = MyDecisionGate()
#         self.dg = dg
#         self.linear = torch.nn.Linear(4, 4)

#     def forward(self, x, h):
#         new_h = torch.tanh(self.dg(self.linear(x)) + h)
#         # new_h = torch.tanh(self.linear(x) + h)
#         return new_h, new_h


# scripted_gate = torch.jit.script(MyDecisionGate())
# my_cell = MyCell(scripted_gate)
# scripted_cell = torch.jit.script(my_cell)
# print(scripted_gate.code)
# print("*"*20)
# print(scripted_cell.code)
# print("*"*20)
# x, h = torch.rand(3, 4), torch.rand(3, 4)
# print(scripted_cell(x, h))

# # # my_cell = MyCell()
# # x = torch.rand(3, 4)
# # h = torch.rand(3, 4)
# # print(my_cell)
# # print(my_cell(x, h))
# # traced_cell = torch.jit.trace(my_cell, (x, h))
# # print(traced_cell)
# # print("*"*20)
# # print(traced_cell.dg.code)
# # # traced_cell(x, h)
# # # print(traced_cell.graph)
# # print("*"*20)
# # print(traced_cell.code)
# # # print('*'*20)
# # # print(my_cell(x, h))
# # # print("*"*20)
# # # print(traced_cell(x, h))


# class MyRNNLoop(torch.nn.Module):

#     def __init__(self):
#         super(MyRNNLoop, self).__init__()
#         self.cell = torch.jit.trace(MyCell(scripted_gate), (x, h))

#     def forward(self, xs):
#         h, y = torch.zeros(3, 4), torch.zeros(3, 4)
#         for i in range(xs.size(0)):
#             y, h = self.cell(xs[i], h)
#         return y, h

# rnn_loop = torch.jit.script(MyRNNLoop())
# print(rnn_loop.code)


# class WrapRNN(torch.nn.Module):
#     def __init__(self):
#         super(WrapRNN, self).__init__()
#         self.loop = torch.jit.script(MyRNNLoop())

#     def forward(self, xs):
#         y, h = self.loop(xs)
#         return torch.relu(y)

# traced = torch.jit.trace(WrapRNN(), (torch.rand(10, 3, 4)))
# print("*"*20)
# print(traced.code)
# print("*"*20)
# print(traced(torch.rand(3, 4)))

# traced.save('wrapped_rnn.pt')
# loaded = torch.jit.load('wrapped_rnn.pt')
# print("*"*20)
# print(loaded)
# print("*"*20)
# print(loaded.code)


# loaded = torch.jit.load('wrapped_rnn.pt')
# print("*"*20)
# print(loaded)
# print("*"*20)
# print(loaded.code)

# device = torch.device('cpu')
# dummy_input = torch.randn(3, 4, device=device)
# dummy_output = loaded(dummy_input)
# torch.onnx.export(loaded, dummy_input, "wrapped_rnn.onnx")


# print(torch.__version__)
# # a = torch.ones(3, 2)
# a = torch.tensor([[1, 2], [3, 4], [5, 6]])
# b = a.reshape(2, 3)

# a_s = a.storage()
# b_s = b.storage()


# ix = torch.tensor([0, 0, 0], dtype=torch.int64)
# iy = torch.tensor([0, 1, 2], dtype=torch.int64)

# c = a[iy, ix]

# print(c)
# print(c.storage())

# img_arr = imageio.imread('C:/Users/yunfe/OneDrive/Pictures/iphone110522/HJZA0007.JPG')
# print(img_arr.shape)

# batch_size = 3
# batch = torch.zeros(batch_size, 3, 256, 256, dtype=torch.uint8)

# test = batch[:,0]


vol_arr = imageio.volread("C:/Users/yunfe/Downloads/LVSA_1/LVSA_1/series1301-B/", 'DICOM')
print(vol_arr.shape)
vol = torch.from_numpy(vol_arr).float()
vol = torch.unsqueeze(vol, 0)
print(vol.shape)


import csv
import numpy as np
wine_path = "D:/download/DL/winequality-white.csv"
col_list = next(csv.reader(open(wine_path), delimiter=';'))

wineq_numpy = np.loadtxt(wine_path, dtype=np.float32, delimiter=";", skiprows=1)

print(wineq_numpy)

wineq = torch.from_numpy(wineq_numpy)

data = wineq[:,:-1]
target = wineq[:,-1].long()

target_onehot = torch.zeros(target.shape[0], 10)
target_onehot.scatter_(1, target.unsqueeze(1), 1.0)

print(target_onehot)

data_mean = torch.mean(data, dim=0)
data_var = torch.var(data, dim=0)
print(data_mean)
print(data_var)

data_normalized = (data - data_mean) / torch.sqrt(data_var + 0.001)
print(data_normalized)

bad_indexes = target <= 3
print(bad_indexes.shape, bad_indexes.dtype, bad_indexes.sum())

bad_data = data[bad_indexes]
print(bad_data.shape)

bad_data = data[target <=3]
mid_data = data[(target > 3) & (target < 7)]
good_data = data[target >= 7]

bad_mean = torch.mean(bad_data, dim=0)
mid_mean = torch.mean(mid_data, dim=0)
good_mean = torch.mean(good_data, dim=0)

for i, args in enumerate(zip(col_list, bad_mean, mid_mean, good_mean)):
    print('{:2} {:20} {:6.2f} {:6.2f} {:6.2f}'.format(i, *args))

pass