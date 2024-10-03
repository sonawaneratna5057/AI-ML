import pandas as pd
from transformers import pipeline,AutoTokenizer,AutoModelForCausalLM

def ai_model():
    model_name ="gpt2"
    # Load the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name, clean_up_tokenization_spaces=True)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Specify pad_token_id (optional, if your model has a pad token)
    model.config.pad_token_id = tokenizer.eos_token_id  # Set pad token id explicitly
    return tokenizer,model

def generate_smart_message(lead):
    """Generate a smart message using a pre-trained language model."""
    name = lead['Name']
    role = lead['Role']
    industry = lead['Industry']
    engagement_rate = lead['Engagement Rate']
    
    prompt = f"Draft a connection message for {name}, a {role} in {industry} with an engagement rate of {engagement_rate}."
    # Generate the message using the model
    tokenizer, model = ai_model()

    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    output = model.generate(input_ids, max_length=50)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return generated_text

def recommend_next_action(lead):
    """Recommend the next best action using a pre-trained language model."""
    engagement_score = lead['engagement_score']
    recent_activity = lead['Recent Activity']
    prompt = f"With an engagement score of {engagement_score} and recent activity '{recent_activity}', suggest the next action."

    # Generate the message using the model
    tokenizer, model = ai_model()

    input_ids = tokenizer(prompt, return_tensors="pt").input_ids
    output = model.generate(input_ids, max_length=50)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return generated_text