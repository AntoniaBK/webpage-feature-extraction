from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Step 1: Load dataset and split into training and testing sets
dataset = None
X_train, X_test, y_train, y_test = train_test_split(dataset.data, dataset.target, test_size=0.3, random_state=42)

# Step 2: Train a Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 3: Get confidence values (probabilities) for the test set
probabilities = model.predict_proba(X_test)

# Step 4: Display the predicted class and corresponding confidence for the first test sample
predicted_class = model.predict(X_test)
print("Predicted Class:", predicted_class[0])
print("Class Probabilities:", probabilities[0])
print("Confidence in the Predicted Class:", max(probabilities[0]))
