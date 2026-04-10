import numpy as np
from sklearn.linear_model import LinearRegression

# Training data (example)
queue_lengths = np.array([1,2,3,4,5,6,7,8,9,10]).reshape(-1,1)
wait_times = np.array([2,4,6,8,10,12,14,16,18,20])

model = LinearRegression()
model.fit(queue_lengths, wait_times)

def predict_wait_time(queue_size):
    prediction = model.predict([[queue_size]])
    return round(prediction[0], 2)