def column_mapper(column_string):
    mapper= {
        
        "Timestamp":"time_stamp",
        "Email address":"email",
        "First Name(s)/Given Name(s)":"firstname",
        "What is your English level?":"english_level",
        "If you are admitted to 10 Academy's Batch 6 intensive training, are you able to commit full-time (~60 hours/week) without conflicting obligations?":"commitment",
        "Are you able to self-fund and provide the technical requirements for our remote training?":"self_funding",
        "Did you complete your last academic requirement (exam, defense, course) for your undergraduate degree on or after 1 Jan 2020?  If you are still studying, do you expect to complete your last academic requirement (exam, defense, course) for your undergraduate degree by 30 June 2021? (each applicant will be required to present proof, later in the process)":"graduated",
        "Please confirm that you have read and are in agreement with the costs and pay-it-forward model for 10 Academy Batch 6 ":"pay_it_forward",
        "Imagine you were asked to design and implement a project. The project will use technology (AI, Web3, others) to positively impact at least 5 million people in 5 years in a sustainable (financially, environmentally) and scalable way. Briefly describe the problem you would choose (from any field e.g agriculture, education, etc) and how your solution will be impactful, scalable, and sustainable. Detailed answers are helpful. (1500 characters max)":"renowned_idea",
        "Nationality":"nationality",
        "City of current residence":"city",
        "Date of Birth":"date_of_birth",
        "Gender":"gender",
        "Highest completed education level":"education_level",
        "Field of Study":"field_of_study",
        "Name of Institution":"name_of_instituition",
        "Special academic achievements and honors": "honours",
        "GitHub Profile Link":"github_profile",
        "Name of Reference":"referee_name",
        "Have you previously applied for 10 Academy intensive training?":"previously_applied",
        "How did you learn about 10 Academy and this program?":"mode_of_discovery",
        "Work Experience so far if any":"work_experience",
        "Work Experience Specifications":"work_experience_details",
        "Python Proficiency":"python_proficiency",
        "SQL Proficiency":"sql_proficiency",
        "Statistics Proficiency":"statistics_proficiency",
        "Linear Algebra Proficiency": "algebra_proficiency",
        "How many AI/ML/Web3 projects have you completed so far?":"project_compeleted",
        "Kaggle/Zindi Profile Link":"data_science_profile",
        "Please describe, in detail, any self-taught or extra-curricular data science-related courses that you have undertaken or completed.":"self_taught",
        "I agree that 10 Academy can use my application information for processing my application and for keeping me informed of further opportunities in related fields. We will not share/sell your information. Our full terms and conditions are here: https://docs.google.com/document/d/1yduZ66dH5o8vA_scA3N6tOla9OeJuhoFRGTQ35KsG0g/edit?usp=sharing and our privacy policy is here: https://docs.google.com/document/d/1jhZqUb2S92UM5wjMzPlRpHew_A5xjkRgLK7gZfpoAik/edit?usp=sharing":"Accept_terms_and_conditions",
        "What is your current occupation?":"occupation",
        "What is your highest completed level of Education (as on 30 June 2022)?":"highest_completed_level_of_Education",
        "When is your graduation date? Put your expected graduation date if you are still studying (Note: Applicants whose graduation date is between 1 Jan 2022 and 30 April 2022 are likely to be prioritized - a proof will be asked for at a later stage of the process)":"graduation_date",
        "Please share your LinkedIn profile link.  Create one if you do not have one yet (here: https://www.linkedin.com/signup)":"linkedIn_profile",
        
        "Why do you want to join 10 Academy Batch 6 Intensive Training? Help our team to understand your past work, your future goals and how your taking up 10 Academy training will help you (and those around you) to grow. (1500 characters max)":"reason_to_join",
        "Which Batch did you apply for?":"previously_applied_batch",
        "At which stage did you reach?":"stage_to_pevious_application",
        "Family Name(s)/Surname(s)":"familyname",
        "How many months of full-time work experience do you have as of 30 June 2022?":"work_experience_month",
        "Batch":"batch",
       
        
        
    }
    return mapper.get(column_string, column_string)


















