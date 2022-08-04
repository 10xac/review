# Application Review process.

## Steps to Application Review 

- Collect appplication information from gsheet by passing gsheet id.
- Process the application information by converting the question with the question mapper function to update batch dependent questions.
- Create Review category, Reviewer and alluser 
- To insert review assign the Review Category and the reviewers id to that specific review 
- To switch between enviroment Like dev,stage, and production. Instailze Insert_alluser.py by one of this params  {'dev-cms','stage-cms', 'cms'}

### How to use and contribute



#### To use repository

Assuming that you are working in Project directory


`git clone https://github.com/10xac/review.git`
`git checkout main`

#### To contribute to the the repo

- You can create brach with this naming format ***R-Branch name*** .

`git checkout main`
`git checkout -b R-Branch name`
