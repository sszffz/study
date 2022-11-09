import torch.nn as nn

s = nn.Sequential(
    nn.Linear(2, 5),
    nn.ReLU(),
    nn.Linear(5, 20),
    nn.ReLU(),
    nn.Linear(20, 10),
    nn.Dropout(p=0.3),
    nn.Softmax(dim=1)
)

print(s)

for parameters in s.parameters():
    print(parameters)

# s.to("cuda")
print("*"*20)

stat_dict = s.state_dict()
for key, value in s.state_dict().items():
    print(key, value)
