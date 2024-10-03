from flask import Flask, render_template, request, send_from_directory
import linkedin_scraper
import json
import os
import output

app = Flask(__name__)
link = ""

# Function to get the last updated time of a directory
def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

# Homepage
@app.route("/", methods=['POST', 'GET'])
def home():
    return render_template("homepage.html", last_updated=dir_last_updated('static'))

# Form page
@app.route("/form", methods=['POST', 'GET'])
def form():
    if request.method == 'POST':
        link = request.form['profilelink']
    json_string1 = linkedin_scraper.linkedin_scraper1(link)
    return render_template("formhtml.html", json_string=json_string1, last_updated=dir_last_updated('static'))

# Thank you page
@app.route('/handle_data', methods=['POST'])
def handle_data():
    try:
        # Get all the hidden data
        hidden_basic = request.form['hidden_basic1']
        hidden_education = request.form['hidden_education1']
        hidden_projects = request.form['hidden_projects1']
        hidden_certifications = request.form['hidden_certifications1']
        hidden_experience = request.form['hidden_experience1']
        hidden_skils = request.form['hidden_skils1']
        hidden_volunteer = request.form['hidden_volunteer1']
        hidden_accomplishments = request.form['hidden_accomplishments1']
        hidden_hobbies = request.form['hidden_hobbies1']
        
        # Get basic_info_list data
        basic_info_list = [request.form.get(name) for name in ["fname", "lname", "headline", "linkedin", "email", "phone", "age", "github"]]
        
        # Get education_info_list data
        education_info_list_name = ["institute", "degree", "year", "grade"]
        education_info_list = [[request.form.get(f"{education_info_list_name[j]}{i + 1}") for j in range(4)] for i in range(int(hidden_education))]
        
        # Get projects_info_list data
        projects_info_list_name = ["projectname", "projectduration", "projectdescription"]
        projects_info_list = [[request.form.get(f"{projects_info_list_name[j]}{i + 1}") for j in range(3)] for i in range(int(hidden_projects))]
        
        # Get certifications_info_list data
        certifications_info_list_name = ["certificationname", "certificationdate", "certificationorgan"]
        certifications_info_list = [[request.form.get(f"{certifications_info_list_name[j]}{i + 1}") for j in range(3)] for i in range(int(hidden_certifications))]
        
        # Get experience_info_list data
        experience_info_list_name = ["expname", "exprole", "expdate", "expdescription"]
        experience_info_list = [[request.form.get(f"{experience_info_list_name[j]}{i + 1}") for j in range(4)] for i in range(int(hidden_experience))]
        
        # Get skills_info_list data
        skills_info_list = [request.form.get(f"skill{i + 1}") for i in range(int(hidden_skils))]
        
        # Get volunteer_info_list data
        volunteer_info_list_name = ["voname", "vorole", "vodate", "vodescription"]
        volunteer_info_list = [[request.form.get(f"{volunteer_info_list_name[j]}{i + 1}") for j in range(4)] for i in range(int(hidden_volunteer))]
        
        # Get accomplishments_info_list data
        accomplishments_info_list_name = ["accname", "accyear"]
        accomplishments_info_list = [[request.form.get(f"{accomplishments_info_list_name[j]}{i + 1}") for j in range(2)] for i in range(int(hidden_accomplishments))]
        
        # Get hobbies_info_list data
        hobbies_info_list = [request.form.get(f"hobby{i + 1}") for i in range(int(hidden_hobbies))]
        
        # Prepare JSON data
        json_data = {
            'basic_info_list': basic_info_list,
            'education_info_list': education_info_list,
            'projects_info_list': projects_info_list,
            'certifications_info_list': certifications_info_list,
            'experience_info_list': experience_info_list,
            'skills_info_list': skills_info_list,
            'volunteer_info_list': volunteer_info_list,
            'accomplishments_info_list': accomplishments_info_list,
            'hobbies_info_list': hobbies_info_list
        }
        final_json_string = json.dumps(json_data)

        # Call output function
        output.output1(final_json_string)

        # Return PDF file
        filename = "output.pdf"
     #    return send_from_directory("C:/Users/shrut/OneDrive/Desktop/Resume Scraper/yourapp", filename=filename, as_attachment=True)
        return send_from_directory("C:/Users/KOLI/Downloads/Resume-Builder/from-LinkedIn-master/Resume-Builder-from-LinkedIn-master/output", filename=filename, as_attachment=True)

    except Exception as e:
        print(f"An error occurred in handle_data: {e}")
        return "Error processing data", 500  # Return an error response

if __name__ == "__main__":
    app.run(debug=True)
