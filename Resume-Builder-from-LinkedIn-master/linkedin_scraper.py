import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import re
def linkedin_scraper1(link):
    # Initialize Options to start Chrome as headless in selenium
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['acceptSslCerts'] = True
    capabilities['acceptInsecureCerts'] = True

    # Initialize the chrome webdriver as 'browser'
    browser = webdriver.Chrome(options=chrome_options)

    # Get the login page for LinkedIn
    browser.get('https://www.linkedin.com/uas/login')

    # Open the file with the username and password for LinkedIn login
    with open('config.txt') as file:  # Ensures the file is closed after reading
        lines = file.readlines()
        username = lines[0].strip()  # Remove any leading/trailing whitespace
        password = lines[1].strip()

    # Find the username and password fields and log in
    browser.find_element(By.ID, 'username').send_keys(username)
    browser.find_element(By.ID, 'password').send_keys(password)

    # Submit the login form
    browser.find_element(By.ID, 'password').submit()
    import time
    time.sleep(5)  # Wait for login to complete

    # Go to the profile link you want to scrape
    browser.get(link)

    # More scraping logic would go here...


    # Wait until the body is fully loaded
    SCROLL_PAUSE_TIME = 6
    WebDriverWait(browser, SCROLL_PAUSE_TIME).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Scroll the page to load dynamic content
    last_height = browser.execute_script("return document.body.scrollHeight")
    for i in range(3):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
        time.sleep(SCROLL_PAUSE_TIME / 2)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight*(2/3));")
        time.sleep(SCROLL_PAUSE_TIME / 2)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)

        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Expand various sections
    sections_to_expand = [
        ("//section[@id='education-section']//button", "education"),
        ("//div[@class='pv-accomplishments-block__content break-words']//button[@aria-label='Expand projects section']", "projects"),
        ("//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle']", "certifications"),
        ("//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle']", "experiences"),
        ("//button[@class='pv-profile-section__card-action-bar']", "skills"),
        ("//button[@class='pv-profile-section__see-more-inline']", "volunteering"),
    ]

    for xpath, section in sections_to_expand:
        try:
            button = browser.find_element(By.XPATH, xpath)
            browser.execute_script("arguments[0].click();", button)
        except Exception as e:
            # Catch and ignore exceptions when sections are not found
            pass

    # Get page source and parse with BeautifulSoup
    src = browser.page_source
    soup = BeautifulSoup(src, 'lxml')

    # BASIC INFO LIST
    basic_info_list = []

    # Find name and headline section
    name_div = soup.find('div', {'class': 'flex-1 mr5'})
    
    if name_div:
        name_loc = name_div.find_all('ul')
        fullname = name_loc[0].find('li').get_text().strip()

        # Handle different cases of full name (with/without middle name)
        name_parts = fullname.split()
        if len(name_parts) == 2:
            first_name, last_name = name_parts
            middle_name = ""
        elif len(name_parts) == 3:
            first_name, middle_name, last_name = name_parts
        else:
            first_name = name_parts[0]
            last_name = name_parts[-1]
            middle_name = " ".join(name_parts[1:-1])

        # Append name parts to basic info list
        basic_info_list.append(first_name)
        basic_info_list.append(middle_name)
        basic_info_list.append(last_name)

        # Get headline
        headline = name_div.find('h2').get_text().strip()
        basic_info_list.append(headline)

        # Append profile link
        basic_info_list.append(link)

        # Placeholder for other fields (email, phone, etc.)
        basic_info_list.extend(['', '', '', ''])

    #print(basic_info_list)

    #education section
    education_info_list =[]
    try:
        edu_section = soup.find('section', {'id': 'education-section'}).find('ul')
        edu_section = edu_section.find_all('div', {'class': 'pv-entity__summary-info pv-entity__summary-info--background-section'})
        college_names = []
        degree_names = []
        field_names = []
        grades = []
        dates = []
        for x in range(len(edu_section)):
            curr_section = edu_section[x]
            try:
                college_name = curr_section.find('h3', {'class': 'pv-entity__school-name t-16 t-black t-bold'})
                college_names.append(college_name.get_text())
            except Exception as e:
                #print("Education college_name Exception",e) 
                college_names.append('')

            try:
                degree_name = curr_section.find('p', {'class': 'pv-entity__secondary-title pv-entity__degree-name t-14 t-black t-normal'}).find('span', {'class': 'pv-entity__comma-item'})
                degree_names.append(degree_name.get_text())
            except Exception as e:
                #print("Education degree_name Exception",e)
                degree_names.append('')

            try:
                field_name = curr_section.find('p', {'class': 'pv-entity__secondary-title pv-entity__fos t-14 t-black t-normal'}).find('span', {'class': 'pv-entity__comma-item'})
                field_names.append(field_name.get_text())
            except Exception as e:
                #print("Education field_name Exception",e)
                field_names.append('')

            try:
                grade = curr_section.find('p', {'class': 'pv-entity__secondary-title pv-entity__grade t-14 t-black t-normal'}).find('span', {'class': 'pv-entity__comma-item'})
                grades.append(grade.get_text())
            except Exception as e:
                #print("Education grade Exception",e)
                grades.append('')

            try:
                time = curr_section.find('p', {'class': 'pv-entity__dates t-14 t-black--light t-normal'})
                dates.append((time.find_all('time')[1].get_text()))
            except Exception as e:
                #print("Education time Exception",e)
                dates.append('')

        for i in range(len(edu_section)):
            education_info_list.append([college_names[i], degree_names[i], field_names[i], dates[i], grades[i]])
    except Exception as e:
        #no education added
        #print("Education Section Exception", e)
        pass

    #print(education_info_list)


    #Project Section
    projects_info_list = []
    project_titles = []
    try:
        project_section = soup.find('div', {'id': 'projects-expandable-content'})
        project_section = project_section.find('ul', {'class': 'pv-accomplishments-block__list'})

        projects = project_section.find_all('h4', {'class': 'pv-accomplishment-entity__title t-14 t-bold'})

        for i in range(len(projects)):
            project_name = projects[i].get_text().split('\n')[2]
            project_name = re.sub(' +', ' ', project_name)
            project_titles.append(project_name.strip())


        projects = project_section.find_all('p', {'class': 'pv-accomplishment-entity__date t-14'})
        project_time = []
        for i in range(len(project_titles)):
            try:
                project_date = projects[i].get_text().split('\n')[1]
                project_date = re.sub(' +', ' ', project_date)
                project_time.append(project_date[1:])
            except Exception as e:
                # print("project_date Exception", e)
                project_time.append('')

        project_descriptions = []
        projects2 = project_section.find_all('p', {'class': 'pv-accomplishment-entity__description t-14'})
        for i in range(len(project_titles)):
            try:
                next_empty_elem = projects2[i].findNext('div')
                curr_proj_desc = next_empty_elem.next_sibling
                project_descriptions.append(curr_proj_desc.strip())
            except Exception as e:
                # print("curr_proj_desc Exception", e)
                project_descriptions.append('')

        #Construct projects_info_list from above data
        for i in range(len(project_titles)):
            projects_info_list.append([project_titles[i], project_time[i], project_descriptions[i]])
    except Exception as e:
        #no projects added
        #print("Project Section Exception", e)
        pass
    #print(projects_info_list)

    #certifications section
    certifications_info_list = []
    try:
        certificates_section = soup.find('section', {'id': 'certifications-section'})

        list_items = certificates_section.find('ul', {'class': 'pv-profile-section__section-info section-info pv-profile-section__section-info--has-more'})
    except Exception as e:
        #print("certificates_section Exception", e)
        pass
    try:
        if list_items is None:
            list_items = certificates_section.find('ul', {'class': 'pv-profile-section__section-info section-info pv-profile-section__section-info--has-no-more'})

        items = list_items.find_all('li', {'class' : 'pv-profile-section__sortable-item pv-certification-entity ember-view'})
        cert_names_list = []
        cert_issuer_list = []
        cert_dates_list = []

        for i in range(len(items)):
            curr_cert_name = items[i].find('h3', {'class': 't-16 t-bold'})
            curr_cert_name = curr_cert_name.get_text().strip()
            cert_names_list.append(curr_cert_name)

            curr_issuer_name = items[i].find_all('p', {'class': 't-14'})[0]
            curr_issuer_name = curr_issuer_name.get_text().strip()
            curr_issuer_name = curr_issuer_name.replace('Issuing authority\n', '')
            cert_issuer_list.append(curr_issuer_name)

            curr_cert_date = items[i].find_all('p', {'class': 't-14'})[1]
            curr_cert_date = curr_cert_date.get_text().strip()
            curr_cert_date = curr_cert_date.replace('Issued date and, if applicable, expiration date of the certification or license\n', '').replace('No Expiration Date', '').replace('Issued ', '')
            cert_dates_list.append(curr_cert_date)

        #adding elements in certifications_info_list as per schema
        for i in range(len(cert_names_list)):
            certifications_info_list.append([cert_names_list[i], cert_dates_list[i], cert_issuer_list[i]])

    except Exception as e:
        #no certificates added
        #print("Certificates Section Exception", e)
        pass

    #print(certifications_info_list)

    #Experience Section
    experience_info_list = []
    list_items = []
    items = []

    try:
        experience_section = soup.find('section', {'class': 'experience-section'})
        #print(experience_section)

        list_items = experience_section.find('ul', {'class': 'pv-profile-section__section-info section-info pv-profile-section__section-info--has-more'})
    except Exception as e:
        #print("experience_section Exception", e)
        pass

    try:
        if list_items is None:
            list_items = experience_section.find('ul', {'class': 'pv-profile-section__section-info section-info pv-profile-section__section-info--has-no-more'})

        items = list_items.find_all('li', {'class' : 'pv-entity__position-group-pager pv-profile-section__list-item ember-view'})
        company_names_list = []
        position_list = []
        dates_employed_list = []
        description_list = []

        for i in range(len(items)):
            try:
                curr_name = items[i].find('p', {'class' : 'pv-entity__secondary-title t-14 t-black t-normal'})
                curr_name = curr_name.get_text().strip()
                curr_name = curr_name.split('\n')[0].strip()
                #print("1st currname", curr_name)
                company_names_list.append(curr_name)
            except Exception as e:
                #print("Experience curr_name Exception:", e)
                pass
                
            try:
                if curr_name is None:
                    curr_name = items[i].find('h3', {'class': 't-16 t-black t-bold'})
                    curr_name = curr_name.get_text().strip()
                    curr_name = curr_name.replace("Company Name\n", '')
                    company_names_list.append(curr_name)
            except Exception as e:
                #print("Experience curr_name Exception:", e)
                pass
            
            try:
                curr_position = items[i].find('h3', {'class': 't-16 t-black t-bold'})
                curr_position = curr_position.get_text().strip()
                curr_position = curr_position.replace("Company Name\n", '')
                position_list.append(curr_position)
            except Exception as e:
                #print("Experience curr_position Exception:", e)
                pass

            try:
                curr_dates = items[i].find('h4', {'class': 'pv-entity__date-range t-14 t-black--light t-normal'})
                curr_dates = curr_dates.get_text().strip()
                curr_dates = curr_dates.replace('Dates Employed\n', '')
                dates_employed_list.append(curr_dates)
            except Exception as e:
                #print("Experience curr_dates Exception:", e)
                pass

            try:
                curr_description = items[i].find('div', {'class': 'pv-entity__extra-details t-14 t-black--light ember-view'})
                curr_description = curr_description.get_text().strip()
                curr_description = curr_description.replace('\n\n\n\n\n        see less', '')
                curr_description = curr_description.replace('\n\n   \n  \n\n\n\n\n\n\n\n\n\n', ' ')
                curr_description = curr_description.replace('\n\n    \n…\n\n        see more', '')
                curr_description = curr_description.replace('\n       ', '.')
                curr_description = curr_description.replace('\n\n', '.')
                description_list.append(curr_description)
            except Exception as e:
                #print("Experience curr_description Exception:", e)
                pass
                #Add empty description for normalization of data
                description_list.append('')

        #create company_names_list from above data
        for i in range(len(company_names_list)):
            experience_info_list.append([company_names_list[i], position_list[i], dates_employed_list[i], description_list[i]])

    except Exception as e:
        #No Experience Added
        #print("Experience Section Exception:", e)
        pass
    #print(experience_info_list)


    #Skills Section
    skills_info_list = []
    try:
        skills_section = soup.find('section', {'class': 'pv-profile-section pv-skill-categories-section artdeco-container-card ember-view'})
    except Exception as e:
        #print("skills_section Exception", e)
        pass

    try:
        if skills_section is None:
            skills_section = soup.find('section', {'class': 'pv-profile-section pv-skill-categories-section artdeco-container-card first-degree ember-view'})

        all_skills = skills_section.find_all('span', {'class': 'pv-skill-category-entity__name-text t-16 t-black t-bold'})

        for i in range(len(all_skills)):
            skills_info_list.append(all_skills[i].get_text().strip())

    except Exception as e:
        #No skills added
        #print("Skills Section Exception:", e)
        pass

    #print(skills_info_list)


    #Volunteering Section:
    volunteer_info_list = []
    items = []
    list_items = []
    try:
        volunteer_section = soup.find('section', {'class': 'pv-profile-section volunteering-section ember-view'})
        list_items = volunteer_section.find('ul', {'class': 'pv-profile-section__section-info section-info pv-profile-section__section-info--has-more ember-view'})
    except Exception as e:
        #print("Volunteering volunteer_section Exception:", e)
        pass

    try:
        if list_items is None:
            list_items = volunteer_section.find('ul', {'class': 'pv-profile-section__section-info section-info pv-profile-section__section-info--has-no-more'})
    except Exception as e:
        #print("Volunteering list_items Exception:", e)
        pass

    try:
        items = list_items.find_all('li', {'class': 'pv-profile-section__sortable-item pv-profile-section__section-info-item relative pv-profile-section__sortable-item--v2 pv-profile-section__list-item sortable-item ember-view'})
    except Exception as e:
        # print("Volunteering list_items Exception:", e)
        pass

    try:
        if items == []:
            items = list_items.find_all('li', {'class': 'pv-profile-section__list-item pv-volunteering-entity pv-profile-section__card-item ember-view'})
    except Exception as e:
        # print("Volunteering items Exception:", e)
        pass

    try:
        for i in range(len(items)):
            curr_name = items[i].find('span', {'class': 'pv-entity__secondary-title'})
            curr_name = curr_name.get_text().strip()

            curr_role = items[i].find('h3', {'class': 't-16 t-black t-bold'})
            curr_role = curr_role.get_text().strip()

            try:
                curr_dates = items[i].find('h4', {'class': 'pv-entity__date-range detail-facet inline-block t-14 t-black--light t-normal'})
                curr_dates = curr_dates.get_text().strip()
                curr_dates = curr_dates.replace('Dates volunteered\n', '')
            except Exception as e:
                    #print("curr_dates Exception", e)
                    curr_dates = ''

            try:
                curr_description = items[i].find('p', {'class': 'pv-entity__description t-14 t-normal mt4'})
                curr_description = curr_description.get_text().strip()
            except Exception as e:
                #print("curr_description Exception", e)
                curr_description = ''

            #Construct volunteer_info_list from above data
            volunteer_info_list.append([curr_name, curr_role, curr_dates, curr_description])

    except Exception as e:
        #no volunteering added
        #print("Volunteering Section Exception", e)
        pass

    try:
        # click to expand honors and awards section because only either projects or honors and awards can be expanded at a time
        honors_and_awards_expand_button = browser.find_element_by_xpath("//section[@class='pv-profile-section pv-accomplishments-section artdeco-container-card ember-view']//button[@aria-label='Expand honors & awards section']")
        browser.execute_script("arguments[0].click();", honors_and_awards_expand_button)

        # click to expand honors and awards section to show more
        honors_and_awards_expand_button2 = browser.find_element_by_xpath(
            "//section[@class='pv-profile-section pv-accomplishments-section artdeco-container-card ember-view']//button[@aria-controls='honors-expandable-content' and @aria-expanded='false']")
        browser.execute_script("arguments[0].click();", honors_and_awards_expand_button2)
    except Exception as e:
        #print("honors_and_awards_expand_button Exception", e)
        pass


    #accomplishments section
    accomplishments_info_list = []
    try:
        accomplishments_section = soup.find_all('section', {'class': 'pv-profile-section pv-accomplishments-section artdeco-container-card ember-view'})

        honors_section = accomplishments_section[0].find('div', {'aria-labelledby': 'honors-title'})

        list_items = honors_section.find_all('li', {'class': 'pv-accomplishments-block__summary-list-item'})

        for i in range(len(list_items)):
            # appending empty string for year field
            accomplishments_info_list.append([list_items[i].get_text().strip(), ""])

    except Exception as e:
        #No accomplishments added
        #print("Accomplishments Section Exception", e)
        pass


    #empty hobbies_info_list because it is not available on linkedin
    hobbies_info_list = []

    #Close the browser once scraping is done
    browser.close()

    #TESTING OUTPUTS
    #print("LISTS")
    #print(basic_info_list)
    #print(education_info_list)
    #print(projects_info_list)
    #print(certifications_info_list)
    #print(experience_info_list)
    #print(skills_info_list)
    #print(volunteer_info_list)
    #print(accomplishments_info_list)

    final_all_lists = [basic_info_list, education_info_list, projects_info_list, certifications_info_list, experience_info_list, skills_info_list, volunteer_info_list, accomplishments_info_list, hobbies_info_list]

    json_data = {'basic_info_list' : basic_info_list, 'education_info_list': education_info_list, 'projects_info_list': projects_info_list, 'certifications_info_list': certifications_info_list, 'experience_info_list': experience_info_list, 'skills_info_list': skills_info_list, 'volunteer_info_list': volunteer_info_list, 'accomplishments_info_list': accomplishments_info_list, 'hobbies_info_list': hobbies_info_list}

    final_json_string = json.dumps(json_data)
    #print(final_json_string)

    fileheader = open("scraped_data.json", 'w')

    fileheader.writelines(final_json_string)

    return (json_data)