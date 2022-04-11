import pandas as pd
import plotly.express as px

def missed_skills(row):
    required_skill = row['required_skills']
    rskill = required_skill.split(',')
    matched_skill = row['matched_skills']
    skill = matched_skill.split(',')
    
    missed_skill = list(set(rskill)- set(skill))
    return missed_skill

def get_trainee_df(df, trainee_name: str):
    """
    Function to return trainee dataframe from json metadata

    """
    match_degree = df[trainee_name]['match_degree']
    required_skills = df[trainee_name]['required_skills']
    matched_skills = df[trainee_name]['matched_skills']

    df_new = pd.DataFrame(list(zip(match_degree,required_skills,matched_skills)),
               columns =['match_degree','required_skills','matched_skills'])
    #df_new['missed_skill'] = df_new.apply(missed_skills, axis=1)
    return df_new


def convert_list_single_data(df):
    ### Converting list of skills into single data frame row
    skills = []
    for n, row in df.iterrows():
        skill = row['missed_skill']
        for item in skill:
            skills.append(item.strip())
    skills.sort()
    return skills

def plot_missed_skills_from_all_JD(df):
    """ Accepts data frame that have skill extracted from JDs filtered by name"""
    #df_plot = df.loc[df['name'] == name]
    #df['missed_skill'] = df.apply(missed_skills, axis=1)
    skills= convert_list_single_data(df)
    #missed_skill= Counter(skills)
    missed_skill = {x:skills.count(x) for x in skills}
    df_missed_skill= pd.DataFrame(missed_skill.items(), columns=['Skill', 'Count'])
    df_missed_skill= df_missed_skill.sort_values("Count", ascending=False)
    countdf = df_missed_skill[df_missed_skill['Count'] >= 300]
    fig = px.bar(countdf, x='Skill', y = "Count", title=f"Missed skill from for jobs with above selected match percentage")
    return fig

def convert_list_single_required_data(df):
    ### Converting list of skills into single data frame row
    skills = []
    for n, row in df.iterrows():
        skill = row['required_skills'].split(",")
        for item in skill:
            skills.append(item)
    skills.sort()
    return skills

def plot_most_common_skills_from_all_JD(df):
    """ Accepts data frame that have required skill extracted from JDs filtered by name """
    skills= convert_list_single_required_data(df)
    #missed_skill= Counter(skills)
    missed_skill = {x:skills.count(x) for x in skills}
    df_missed_skill= pd.DataFrame(missed_skill.items(), columns=['Skill', 'Count'])
    df_missed_skill= df_missed_skill.sort_values("Count", ascending=False)
    fig = px.bar(df_missed_skill, x='Skill', y = "Count", title="Most common skills for jobs with above selected match percentage ")
    return fig


def tag_boxes(tags: list) -> str:
    """ HTML scripts to render tag boxes. """
    html = ''
    for tag in tags:
        html += f"""
            <a id="tags" href="#">
                {tag.replace('-', ' ')}
            </a>
            """

    html += '<br><br>'
    return html