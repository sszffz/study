import numpy as np
import torch
import torch.nn as nn


class LinearRegressionModel(nn.Module):
    def __init__(self, input_dim, out_dim):
        super().__init__()
        self._linear = nn.Linear(input_dim, out_dim, bias=True)

    def forward(self, x):
        out= self._linear(x)
        return out


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

x_value = np.array([i for i in range(11)], dtype=np.float32)
x_value = x_value.reshape(-1, 1)
y_value = x_value * 2 + 1

model = LinearRegressionModel(1, 1).to(device)
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
criterion = nn.MSELoss()

for epoch in range(1000):
    epoch += 1
    
    inputs = torch.from_numpy(x_value).to(device)
    labels = torch.from_numpy(y_value).to(device)

    optimizer.zero_grad()

    output = model(inputs)

    loss = criterion(output, labels)

    loss.backward()

    optimizer.step()

    if epoch % 50 == 0:
        print('epoch {}, loss {}'.format(epoch, loss.item()))


predicted = model(torch.from_numpy(x_value).to(device).requires_grad_()).data.to('cpu').numpy()
print(predicted)

torch.save(model.state_dict(), "model.pkl")


# state_dict = torch.load("model.pkl")
# model.load_state_dict(state_dict)