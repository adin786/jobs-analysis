import streamlit as st
import pickle
import pandas as pd
from clf_funcs import TextPreprocessor, dummy
import time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
from copy import deepcopy


st.write('''
# Job titles in the data field
### Background
In the Data field there is often a crossover and blurring of skills and responsibilities between disciplines.  
A *statistically determined* model of job titles against role descriptions, could help to consistently 
and accurately match job applicants with vacancies.  We can use machine learning and natural language processing
for this purpose.

### Classifier model
Below is a deployed version of the final text classifier tool.
Enter a job description for a `Data Scientist`, `Data Analyst` or `Data Engineer` position and the tool will 
assign the statistically most likely job title.  
''')

input_str = st.text_area('Copy & paste a job description here', height=200)
process_button = st.button('Run classifier')

nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

@st.cache(suppress_st_warning=True, show_spinner=False, allow_output_mutation=True)
def load_clf():
    with open('clf.pkl','rb') as f:
        clf = pickle.load(f)
        st.write('Classifier loaded')
    return clf

clf_ = load_clf()
clf = deepcopy(clf_) # Coppy with trained params

if process_button:
    
    if len(input_str) < 1:
        st.write('Can\'t classify a blank job description')
    else:
        # Classify
        X_pred = [input_str]
        y_pred = clf.predict(X_pred)
        
        # Probabilities
        y_pred_proba = clf.predict_proba(X_pred)
        list_of_classes = list(clf['clf'].classes_)
        max_idx = np.argmax(y_pred_proba)
        # y_pred_proba_max = y_pred_proba[max_idx]
        
        job_result = y_pred[0]
        job_result_proba = y_pred_proba[0,max_idx]
        st.write(f'This is a **{job_result}** job, with a probability of {job_result_proba*100:.1f}%')
        # st.write(y_pred_proba,list_of_classes,max_idx,y_pred_proba[0,max_idx])
        

# OTHER SECTION
st.write('''
# How does it work?
### The data
I wrote a web scraper for uk.indeed.com job adverts.  To gather a broad dataset I scraped over 2000 jobs 
across to the Data Analytics field using the below queries:
''')
st.write('''
** Job title =** `Data Scientist`,`Data Engineer`,`Data Analyst`,`Business Analyst`,`Machine Learning Engineer`,`Machine Learning`,`Artificial Intelligence`,`AI`,`Data`

**Location =** `Scotland`,`England`,`Remote`
''')
st.write('''
## Visualisations
Below shows the class distribution after manually aggregating and labelling the each job by it\'s advertised title. 

Many of the jobs were not easy to manually label and fitted best in the "other" category.  When building a text  classifier on this data, only the `Data Scientist`, `Data Analyst` and `Data Engineer` classes were used, dropping all other classes.
''')
df = pd.read_csv('df_preprocessed.csv', index_col=0)
# st.dataframe(df)

# Barplot of job distrib    
st.image('image/overall_class_distrib.png')


# Skills heatmap
st.write('''
            ## Heatmap of skills
            I manually extracted the presence of certain skills and plotted a heatmap to show how this varies across each role type''')
cols = [x for x in df.columns.tolist() if 'is_' in x]
piv = df.pivot_table(values=cols, index='title_simplified', aggfunc=np.sum, margins=True)  
count_per_job = [len(df[df['title_simplified'] == x]) for x in list(piv.index)]
piv_normalised = piv.div(count_per_job, axis='rows')

# Plot a normalised heatmap to visually see the most popularly requested skills for each job title.
fig2 = plt.figure(figsize=(15,7))
sns.heatmap(piv_normalised, square=True,  cmap='rocket', vmin=0, vmax=1);
st.pyplot(fig2)

# Wordcloud for data scientist, analyst and engineer
from wordcloud import WordCloud
st.write('''
            ## Wordclouds
            Below shows a wordcloud computed for all job descriptions labelled `Data Scientist`
            ''')
mask = df.title_simplified == 'data scientist'
text = ' '.join(df[mask].description)
wordcloud = WordCloud(max_font_size=100, width=800, height=400, random_state=42).generate(text)
WordCloud()
fig = plt.figure(figsize=[10,10])
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
st.pyplot(fig)

st.write('Again, for `Data Analyst')
mask = df.title_simplified == 'data analyst'
text = ' '.join(df[mask].description)
wordcloud = WordCloud(max_font_size=100, width=800, height=400, random_state=42).generate(text)
WordCloud()
fig = plt.figure(figsize=[10,10])
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
st.pyplot(fig)

st.write('And finally for `Data Engineer')
mask = df.title_simplified == 'data engineer'
text = ' '.join(df[mask].description)
wordcloud = WordCloud(max_font_size=100, width=800, height=400, random_state=42).generate(text)
WordCloud()
fig = plt.figure(figsize=[10,10])
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
st.pyplot(fig)
