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
from wordcloud import WordCloud


st.write('''
# Job titles in the data field
### Background
In the Data field there is often a crossover and blurring of skills and responsibilities between disciplines. (sometimes the job title does not accurately reflect the role described!)

A *statistically determined* model of job titles against role descriptions, could help to accurately match job applicants with vacancies. 
We can use machine learning and natural language processing
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
        st.balloons()
        # st.write(y_pred_proba,list_of_classes,max_idx,y_pred_proba[0,max_idx])
        

# OTHER SECTION

st.write('''
# How it works
## The Data
I web-scraped over 2000 job adverts from uk.indeed.com for roles across the data analytics field.

Below shows the class distribution of my dataset after labelling the each job by it\'s base job title. Indeed's job search seems to 
include lots of relevant, but uncommon job titles so the `other` category is over-represented.  This may impact the classifier's 
performance but I was able to achieve good results with some resampling.

Ignoring this, the dataset included a large number of `Data Scientist` and `Data Analyst` positions. However 
`Data Engineer` jobs seemed to be poorly represented on Indeed's database.
''')


# Barplot of job distrib    
st.image('image/overall_class_distrib.png')

# Skills heatmap
st.write('''
### Manually encoded "skills"
I manually extracted common skills from the description text.  In the future I may build a Named Entity Recognition model
to automatically extract these kinds of tags but for now these are manually encoded using *regular expressions*.

Below shows a heatmap of how these *"skill tags"* varied depending on the job title, normalised against class distribution.
''')
st.image('image/overall_skills_heatmap.png')
st.write('''
As a summary of what this illustrates:
- Predictably, excel is required quite universally across disciplines, esp. in **Admin** roles.
- **Data Engineer** are the only ones commonly mentioning ETL
- **Data Engineers** are needed to be experts in cloud platorms, so are **SW engineers**
- **Data scientists** and **Data Engineers** are required to have SQL skills
- Predictably **ML Engineers** require ML knowledge, but the plain **Scientist** role also has high demand for it, maybe these roles were just given a generic title?
- Devops is most relevant to **Software Engineer** and **Data Engineer** jobs
- Statistics is most relevant to **Data Scientist** and plain **Scientist** roles
- NLP was actually mentioned fairly rarely amongst **Data Scientist** roles
''')

with st.expander('Explore the data interactively', True):
    st.write('''
    Use the below to explore the raw data across all the scraped job ads
    ''')

    # Raw data view
    # Load in the data
    @st.cache(suppress_st_warning=True, show_spinner=False)
    def load_df():
        df = pd.read_csv('df_preprocessed.csv', index_col=0)
        return df
    df = load_df().copy()

    # Display a listbox
    title_options = df['title_simplified'].unique().tolist()
    title_sel = st.selectbox('To explore the data interactively, select a job title from the dropdown below:',title_options)

    # Display a sample of text data
    st.write(f'Below is a randomly sampled job description for **{title_sel}** jobs')
    # btn_shuffle_df = st.button('Shuffle')

    def shuffle_df(title_sel, changed):
        mask = df['title_simplified'] == title_sel
        df_display = df[mask].sample(1)
        df_display = df_display[['title_simplified', 'description']]
        # df_display.description = df_display.description.apply(lambda x: x[:300]+'...')
        df_display = df_display.rename(columns={'title_simplified':'Job Title', 'description':'Job Description'})
        return df_display

    btn_shuffle_df = True
    changed = True if btn_shuffle_df else False
    df_display = shuffle_df(title_sel, changed)
    changed = False
    st.text_area('Sampled job description text',value=df_display['Job Description'].values[0], height=300)

    # Wordcloud
    st.write(f'''
    It can be quite powerful to view the word frequencies for a given set of text data using a wordcloud below is a wordcloud 
    generated for **{title_sel}** jobs
    ''')

    @st.cache(suppress_st_warning=True, show_spinner=False)
    def get_wordcloud(title_sel):
        mask = df.title_simplified == title_sel
        text = ' '.join(df[mask].description)
        # text = df[mask].description
        wordcloud = WordCloud(max_font_size=100, width=800, height=400, random_state=42).generate(text)
        WordCloud()
        return wordcloud

    wc = get_wordcloud(title_sel)
    fig = plt.figure(figsize=[10,10])
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    st.pyplot(fig)

with st.expander('Classification model', True):
    st.write('''
    ## Classification model
    The classifier was based on a Multinomial Naive-Bayes model from Scikit-learn.  
    
    To keep the modelling simple, it was trained on a subset of the dataset for only 3 classes: **Data Scientist**, **Data Analyst**, 
    and **Data Engineer** roles.  At a later date I may look to re-train a modela across all classes in the dataset, but as shown in 
    the heatmap earlier, the class boundaries are fuzzy and 

    The NLP model training pipeline includes the following steps before the classifier:
      - Custom text preprocessor which takes each job description and generates a "bag-of-words":
        - Tokenise by sentence
        - Tokenise by word
        - Remove stopwords (common "filler" words)
        - Lemmatize (strips each word back to it's root meaning)
        - Add Bigrams (double-word combinations)
      - Vectorise the bag-of-words using the TF-IDF method
      - Apply SMOTE resampling to compensate for the class imbalance

    The NaiveBayes model does not have many hyperparameters to play with, but the finished classifer was tuned using 
    the Grid Search method, with 3-fold cross validation to tune for the best parameters of the TF-IDF vectoriser.  
    
    The most accurate and generalisable classifier model was one which ignores out any tokens which occurred extremely 
    frequently in many job adverts, and words which occur very infrequently.
    ''')


