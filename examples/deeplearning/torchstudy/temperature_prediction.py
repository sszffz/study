"""
Temperature prediction
"""
import numpy as np
import torch
from sklearn import preprocessing

features = np.random.randn(384, 14)
label = np.random.randn(384)

input_features = preprocessing.StandardScaler().fit_transform(features)

x = torch.tensor(input_features, dtype=float)
y = torch.tensor(label, dtype=float)

# initialize weight
weights = torch.randn((14, 128), dtype=float, requires_grad=True)
biases = torch.randn(128, dtype=float, requires_grad=True)
weights2 = torch.randn((128, 1), dtype=float, requires_grad=True)
biases2 = torch.randn(1, dtype=float, requires_grad=True)

# learning_rate = 0.001
# losses = []

# for i in range(1000):
#     hidden = x.mm(weights) + biases
#     hidden = torch.relu(hidden)
#     prediction = hidden.mm(weights2) + biases2

#     loss = torch.mean((prediction-y)**2)
#     losses.append(loss.data.numpy())

#     if i % 100 == 0:
#         print("loss:", loss)

#     loss.backward()

#     weights.data.add_(-learning_rate * weights.grad.data)
#     biases.data.add_(-learning_rate * biases.grad.data)
#     weights2.data.add_(-learning_rate * weights2.grad.data)
#     biases2.data.add_(-learning_rate * biases2.grad.data)

#     weights.grad.data.zero_()
#     biases.grad.data.zero_()
#     weights2.grad.data.zero_()
#     biases2.grad.data.zero_()


input_size = input_features.shape[1]
hidden_size = 128
output_size = 1
batch_size = 16

my_nn = torch.nn.Sequential(
    torch.nn.Linear(input_size, hidden_size),
    torch.nn.Sigmoid(),
    torch.nn.Linear(hidden_size, output_size),
)
cost = torch.nn.MSELoss(reduction='mean')
optimizer = torch.optim.Adam(my_nn.parameters(), lr=0.001)

losses = []
for i in range(1000):
    batch_loss = []
    batch_loss = []
    for start in range(0, len(input_features), batch_size):
        end = start + batch_size if start + batch_size < len(input_features) else len(input_features)
        xx = torch.tensor(input_features[start:end], dtype=torch.float, requires_grad=True)
        yy = torch.tensor(label[start:end], dtype=torch.float, requires_grad=True)
        prediction = my_nn(xx)
        loss = cost(prediction, yy)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        batch_loss.append(loss.numpy())
        # batch_loss.append(loss.detach().numpy())
        # batch_loss.append(loss.data.numpy())
        # with torch.no_grad():
        #     batch_loss.append(loss.numpy())
    
    if i % 100:
        losses.append(np.mean(batch_loss))
        print(i, np.mean(batch_loss))

