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

page_sel = st.sidebar.selectbox('Select a page here:',('Data Exploration','Classification'), index=1)

if page_sel.lower() == 'data exploration':
    st.write('''
    # Data Job Title Analysis
    ## Exploratory analysis
    I wrote a web scraper for uk.indeed.com job adverts.  To gather a broad dataset I scraped over 2000 jobs related to the Data Analytics field using the below queries:
    ''')
    st.write("**Job title =** `Data Scientist`,`Data Engineer`,`Data Analyst`,`Business Analyst`,`Machine Learning Engineer`,`Machine Learning`,`Artificial Intelligence`,`AI`,`Data`")
    st.write("**Location =** `Scotland`,`England`,`Remote`")
    st.write('''
    ## Visualisations
    Below shows the class distribution after manually aggregating and labelling the each job by it\'s advertised title. 
    
    Many of the jobs were not easy to manually label and fitted best in the "other" category.  When building a text  classifier on this data, only the `Data Scientist`, `Data Analyst` and `Data Engineer` classes were used, dropping all other classes.
    ''')
    df = pd.read_csv('df_preprocessed.csv', index_col=0)
    # st.dataframe(df)
    
    # Barplot of job distrib    
    fig = plt.figure()
    fig.set_size_inches(10,5)
    value_counts = df.title_simplified.value_counts()
    ax = sns.barplot(y=value_counts.index, x=value_counts.values, palette='rocket');
    ax.set_title('Number of jobs with each value of [title_simplified]');
    ax.set_xlabel('Num jobs');
    def show_values_on_bars(axs, h_v="v", space=0.4):
        def _show_on_single_plot(ax):
            if h_v == "v":
                for p in ax.patches:
                    _x = p.get_x() + p.get_width() / 2
                    _y = p.get_y() + p.get_height()
                    value = int(p.get_height())
                    ax.text(_x, _y, value, ha="center") 
            elif h_v == "h":
                for p in ax.patches:
                    _x = p.get_x() + p.get_width() + float(space)
                    _y = p.get_y() + p.get_height() *  3/4
                    value = int(p.get_width())
                    ax.text(_x, _y, value, ha="left")

        if isinstance(axs, np.ndarray):
            for idx, ax in np.ndenumerate(axs):
                _show_on_single_plot(ax)
        else:
            _show_on_single_plot(axs)
    show_values_on_bars(ax, "h", 0.3)
    st.pyplot(fig)
    
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
    
    
    
elif page_sel.lower() == 'classification':
    st.write('''
    # Data Job Title Analysis
    ## Classifier
    Enter a job description for a `Data Scientist`, `Data Analyst` or `Data Engineer` position.  

    A NaiveBayes based classifier will attempt to identify which of the 3 job titles matches the description best.
    ''')

    input_str = st.text_area('Copy & paste a job description here', height=200)
    process_button = st.button('Classify')
    
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('wordnet')

    @st.cache(suppress_st_warning=True, show_spinner=False,allow_output_mutation=True)
    def load_clf():
        with open('clf.pkl','rb') as f:
            clf = pickle.load(f)
            st.write('Classifier reloaded')
        return clf

    clf_ = load_clf()
    clf = deepcopy(clf_)

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
            st.write(f'This is a **{job_result}** with a probability of {y_pred_proba[0,max_idx]*100:.1f}%')
            # st.write(y_pred_proba,list_of_classes,max_idx,y_pred_proba[0,max_idx])
