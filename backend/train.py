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
from sklearn.preprocessing import LabelEncoder


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

label_encoder = LabelEncoder()
labels_encoded = label_encoder.fit_transform(labels)

labels_encoded = to_categorical(labels_encoded)

x_train, x_test, y_train, y_test = train_test_split(data, labels_encoded, test_size=0.2, shuffle=True, stratify=labels_encoded)

model = Sequential()

model.add(Conv2D(32, (3, 3), activation='relu', input_shape=(21, 2, 1), padding='same'))
model.add(MaxPooling2D((2, 2), padding='same'))  
model.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
model.add(MaxPooling2D((2, 2), padding='same')) 
model.add(Dropout(0.3))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(y_train.shape[1], activation='softmax'))  

model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

hist = model.fit(x_train, y_train, epochs=150, batch_size=32, validation_data=(x_test, y_test))

test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2)
train_loss, train_acc = model.evaluate(x_train, y_train, verbose=2)
model.save('asl.h5')  

fig = plt.figure()
plt.plot(hist.history['loss'], color='teal', label='loss')
plt.plot(hist.history['val_loss'], color='orange', label='val_loss')
fig.suptitle('Loss', fontsize=20)
plt.legend(loc="upper left")
plt.show()

fig = plt.figure()
plt.plot(hist.history['accuracy'], color='teal', label='accuracy')
plt.plot(hist.history['val_accuracy'], color='orange', label='val_accuracy')
fig.suptitle('Accuracy', fontsize=20)
plt.legend(loc="upper left")
plt.show()



