# Main application script
import pandas as pd
import joblib
from ai_recommendations import generate_smart_message, recommend_next_action

def load_model():
    return joblib.load('models/lead_scoring_model.pkl')

def predict_lead_score(lead_data):
    model = load_model()
    lead_score = model.predict([lead_data])
    return lead_score

def main():
    data = pd.read_csv('data/linkedin_leads.csv')
    

    data['engagement_score'] = (data['Posts Engaged'] * data['Engagement Rate']) / data['Connections']
    for idx, lead in data.iterrows():
        lead_data = [lead['Posts Engaged'], lead['Connections'], lead['Engagement Rate'],lead['engagement_score']]
        lead_score = predict_lead_score(lead_data)
        message = generate_smart_message(lead)
        next_action = recommend_next_action(lead)
        
        print(f"Lead: {lead['Name']}, Score: {lead_score}")
        print(f"Message: {message}")
        print(f"Next Action: {next_action}")
        print("="*50)

if __name__ == "__main__":
    main()
