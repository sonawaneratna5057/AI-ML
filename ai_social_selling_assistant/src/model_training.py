# Script for model training
from sklearn.ensemble import RandomForestClassifier
import joblib
from data_preprocessing import load_and_preprocess_data

from sklearn.model_selection import cross_val_score

def train_lead_scoring_model(data_file):
    X_train, X_test, y_train, y_test = load_and_preprocess_data(data_file)
    
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        class_weight='balanced',
        random_state=42
    )
    
    # Cross-validation
    scores = cross_val_score(model, X_train, y_train, cv=5)

    cross_accuracy_percentage = scores.mean() * 100

    print(f"Cross-Validation Accuracy: {cross_accuracy_percentage:.2f}%")
    
    # Train on the full training set
    model.fit(X_train, y_train)
    
    # Save the model
    joblib.dump(model, 'models/lead_scoring_model.pkl')
    
    # Evaluate the model
    accuracy = model.score(X_test, y_test)

    accuracy_percentage = accuracy * 100
    print(f"Model Accuracy: {accuracy_percentage:.2f}%")

    importances = model.feature_importances_
    features = X_train.columns
    for feature, importance in zip(features, importances):
        print(f"{feature}: {importance:.2f}")


if __name__ == "__main__":
    train_lead_scoring_model('data/linkedin_leads.csv')



