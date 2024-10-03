import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def load_and_preprocess_data(file_path):
    data = pd.read_csv(file_path)
    
    # Handle missing values (if any)
    data.fillna(0, inplace=True)
    
    # Calculate engagement score
    data['engagement_score'] = (data['Posts Engaged'] * data['Engagement Rate']) / data['Connections']
    
    # Feature scaling (optional)
    scaler = StandardScaler()
    data[['Posts Engaged', 'Connections', 'Engagement Rate']] = scaler.fit_transform(data[['Posts Engaged', 'Connections', 'Engagement Rate']])
    
    # Split the data
    X = data[['Posts Engaged', 'Connections', 'Engagement Rate', 'engagement_score']]
    y = data['Recent Activity']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test
