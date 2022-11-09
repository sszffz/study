from re import X
from turtle import forward
import torch

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


loaded = torch.jit.load('wrapped_rnn.pt')
print("*"*20)
print(loaded)
print("*"*20)
print(loaded.code)

device = torch.device('cpu')
dummy_input = torch.randn(3, 4, device=device)
dummy_output = loaded(dummy_input)
torch.onnx.export(loaded, dummy_input, "wrapped_rnn.onnx")
