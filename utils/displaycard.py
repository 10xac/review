import streamlit as st
import re

html_temp = """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <div class="main" style="
    font-family: 'Roboto', sans-serif;
    display: flex;
    align-items: start;
    margin: 10px;
    justify-content: start;">
        <div class="job_post" 
        onMouseOver="this.style.box-shadow='5px 5px 2px 2px rgba(0, 0, 0, 0.5)';"
        style="
        display: flex;
        align-items: start;
        border-radius: 10px;
        width: 200rem;
        height: 15rem;
        box-shadow: 0 1px 5px rgba(0, 0, 0, 0.4);" >
            <div class="initialName" style="
                color: cornsilk;
                font-size: 3rem;
                margin-top: 3rem;
                width: 7rem;
                height: 6rem;
                margin-right: 3rem;
                margin-left: 2rem;
                background-color: rgb(85, 85, 240);
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 1rem;">
                    <span class="logo">
                        {}
                    </span>
            </div>
            <div class="detail" style="
            display: flex;
            flex-direction: column;
            justify-content: space-between; ">
                <div class="title" style="
                    display: flex;
                    align-items: flex-start;
                    justify-content: start;
                    font-size: 1.2rem;
                    font-weight: bold;
                    margin-top: 2rem;
                    margin-bottom: 0.5rem;
                    color: rgba(10, 10, 10, 0.5);">
                    {}
                </div>
                <div class="company" style="
                    display: flex;
                    align-items: center;
                    justify-content: start;
                    font-size: 1rem;
                    font-weight: bold;
                    margin-bottom: 1rem;
                    color: rgba(10, 10, 10, 0.5);">
                    <div class="name" >
                        <i class="fas fa-band-aid"></i>
                        <span>
                            <i class="fa fa-building" style=" margin-right:0.5rem;"></i>
                            {}
                        </span>
                    </div>
                    <div class="location" style="margin-left: 3rem;">
                        <span>
                            <i class="fa fa-map-marker" style="margin-right:0.5rem;"></i>
                            {}
                        </span>
                    </div>
                </div>
                <div class="description">
                    <p style="
                    font-size: 0.8rem;">
                        {}...
                    </p>
                </div>
                <div style=
                    "margin-right: 6rem;
                    display: flex;
                    justify-content: end;">
                        <a href={} target="_blank">
                        <button style=
                            "border-radius: 0.5rem;
                            background-color: #586ff1;
                            color: white;">
                            <i class="fa fa-external-link-square"></i>
                            Apply
                        </button>
                        </a>
            </div>
        </div>   
    </div>
"""

class Job:
    def __init__(self, title, company, location, description, apply_link):
        self.title = title
        self.company = company
        self.location = location
        self.desc = description
        self.apply_link = apply_link

    def  discription(self):
        return self.desc

    def __str__(self):
        
        return html_temp.format(self.company[0],self.title,self.company,self.location, self.desc, self.apply_link)  
            # add a streamlit button to add a job to the list

def display_jobs(jobs):
    for indx in jobs.index:
        jobs_desc = jobs['description'][indx][:200]
        if '\n\n' in jobs_desc:
             double_line = re.search('\n\n',jobs_desc)
             jobs_desc = jobs_desc[double_line.start()+2:]
        st.markdown(Job(jobs['title'][indx], jobs['company'][indx], jobs['location'][indx], jobs_desc, jobs['apply_link'][indx]), unsafe_allow_html=True)
        
        