import pickle
from matplotlib import pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import Dropout
from tensorflow.keras.regularizers import l2

from tensorflow.keras.models import load_model



# Load the data from the pickle file
with open('data.pickle', 'rb') as f:
    data_dict = pickle.load(f)

data = data_dict['data']
labels = data_dict['labels']

data = np.array(data, dtype=object)
labels = np.array(labels)

print("Data array shape:", data.shape)
print("Labels array shape:", labels.shape)

data = np.array([np.pad(sample, (0, 42 - len(sample))) if len(sample) < 42 else sample[:42] for sample in data])

data = data.reshape(-1, 21, 2, 1)

print(f"Reshaped data shape: {data.shape}")

from sklearn.preprocessing import LabelEncoder
label_encoder = LabelEncoder()
labels_encoded = label_encoder.fit_transform(labels)

labels_encoded = to_categorical(labels_encoded)

x_train, x_test, y_train, y_test = train_test_split(data, labels_encoded, test_size=0.2, shuffle=True, stratify=labels_encoded)

print(f"x_train shape: {x_train.shape}")
print(f"x_test shape: {x_test.shape}")
print(f"y_train shape: {y_train.shape}")
print(f"y_test shape: {y_test.shape}")
model = load_model('asl.h5')


# hist = model.fit(x_train, y_train, epochs=150, batch_size=32, validation_data=(x_test, y_test))

test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2)
train_loss, train_acc = model.evaluate(x_train, y_train, verbose=2)
# model.save('asl.h5')  
print(f"Test accuracy: {test_acc}")
print(f"Test Loss: {test_loss}")

print(f"train accuracy: {train_acc}")
print(f"train Loss: {train_loss}")