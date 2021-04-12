import torch

v1 = torch.tensor([1.0, 1.0], requires_grad=True)
v2 = torch.tensor([2.0, 2.0])
v_sum = v1 + v2
v_res = (v_sum*2).sum()

print(v1.is_leaf, v2.is_leaf)
print(v_sum.is_leaf, v_res.is_leaf)

print(v1.requires_grad, v2.requires_grad)
print(v_sum.requires_grad, v_res.requires_grad)
print(v_res)

v_res.backward()
print(v1.grad)
