import spacy
import os
import PyPDF2
from pdfminer.high_level import extract_text
import pandas as pd
import streamlit as st
import plotly.express as px
import landingPage as lp

# st.set_page_config(layout="wide", page_title="Job Model")


def get_desc():
    st.title("Enter Job Description Below:")
    job_desc = st.text_area(label=" ", height=400,
                            help="Paste or Enter your job description here")
    return job_desc


def load_skill_pattern():
    skill_pattern_path = "../data/skill_patterns.jsonl"
    return skill_pattern_path


def load_nlp_model():
    # Load pre-trained English language model
    nlp = spacy.load('en_core_web_sm')
    return nlp


cv_path = "../data/trainees_cv/"


def extract_text_from_pdf(file):
    '''Opens and reads in a PDF file from path'''

    fileReader = PyPDF2.PdfFileReader(open(file, 'rb'))
    page_count = fileReader.getNumPages()
    text = [fileReader.getPage(i).extractText() for i in range(page_count)]

    return str(text).replace("\\n", "")


def add_newruler_to_pipeline(skill_pattern_path, nlp):
    '''Reads in all created patterns from a JSONL file and adds
     it to the pipeline after PARSER and before NER'''

    config = {"phrase_matcher_attr": None,
              "validate": True,
              "overwrite_ents": True,
              "ent_id_sep": "|"}

    ruler = nlp.add_pipe('entity_ruler', after='parser', config=config)
    ruler.from_disk(skill_pattern_path)


def create_skill_set(doc):
    '''Create a set of the extracted skill entities of a doc'''

    return set([ent.label_.upper()[6:] for ent in doc.ents
                if 'skill' in ent.label_.lower()])


def create_skillset_dict(resume_names, resume_texts):
    '''Create a dictionary containing a set of the extracted
    skills. Name is key, matching skillset is value'''
    skillsets = [create_skill_set(resume_text) for resume_text in resume_texts]

    return dict(zip(resume_names, skillsets))


def match_skills(job_desc, cv_set, resume_name):
    '''Get intersection of resume skills and job description
     skills and return match percentage'''

    if len(job_desc) < 1:
        print('could not extract skills from job description text')
    else:
        pct_match = round(len(job_desc.intersection(cv_set[resume_name])) / len(job_desc) * 100, 0)
        print(resume_name + " has a {}% skill match on this job description".format(pct_match))
        matched_skills = job_desc.intersection(skillset_dict[resume_name])
        print('Required skills: {} '.format(job_desc))
        print('Matched skills: {} \n'.format(matched_skills))

        return (resume_name, pct_match, job_desc, matched_skills)


def create_tokenized_texts_list(extension, nlp):
    '''Create two lists, one with the names of the
        candidate and one with the tokenized
       resume texts extracted from either a .pdf or .doc'''

    resume_texts, resume_names, profiles_text = [], [], []
    for resume in list(filter(lambda x: 'txt' in x, os.listdir('../data/trainees_skill_profile/'))):
        try:
            txt = open('../data/trainees_skill_profile/' + resume, 'r').readlines()[5:]
            profiles_text.append(nlp(str(txt)))
        except Exception as e:
            print(f"Error: {e}")

    for resume in list(filter(lambda x: extension in x, os.listdir(cv_path))):
        if extension == 'pdf':
            try:
                resume_texts.append(nlp(extract_text(cv_path + resume)))
                resume_names.append(resume.split("_")[1].split('@')[0].capitalize())
            except Exception as e:
                print(resume)
                print('error', e)

    return resume_texts, resume_names, profiles_text

def main():
    extension = 'pdf'
    skill_pattern_path = load_skill_pattern()
    nlp = load_nlp_model()

    add_newruler_to_pipeline(skill_pattern_path, nlp)

    resume_texts, resume_names, profiles_text = \
        create_tokenized_texts_list(extension, nlp)

    skillset_dict = create_skillset_dict(resume_names, resume_texts)
    colB1, colB2, colB3 = st.columns([.3, .2, .5])
    with colB1:
        empty_btn = st.empty()
    with colB2:
        company_name = st.empty()
    with colB3:
        pass
    name = empty_btn.text_input(label='Enter your Name:')
    com_name = company_name.text_input(label='Enter the Company Name:')

    jd_text = str(get_desc())
    if st.button('Get Match') and jd_text != ' ':
        # Create a set of the skills extracted from the job description text
        acad_skillset = create_skill_set(nlp(jd_text))
        match_pairs = [match_skills(acad_skillset, skillset_dict, name)
                        for name in skillset_dict.keys()]

        # Sort tuples from high to low on match percentage
        match_pairs.sort(key=lambda tup: tup[1], reverse=True)
        names, pct, req_skill, matched_skill = zip(*match_pairs)
        df = pd.DataFrame(data=zip(names, pct, req_skill, matched_skill),
                            columns=['names', 'pct', 'req_skill', 'matched_skill'])

        option = st.selectbox('Select your Name:', df['names'].values)
        st.write(option)

        st.table(df.query(f"name == {option}"))

        fig = px.bar(df.head(10), x='names', y='pct')
        st.plotly_chart(fig)


if __name__ == "__main__":
    if "hasLoggedIn" not in st.session_state or st.session_state["hasLoggedIn"] == False:
        st.session_state["hasLoggedIn"] == False
        lp.main()
    if "access" in st.session_state and st.session_state["access"] == "staff":
        main()