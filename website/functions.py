# Programmer Name: Ms Lee Wen Xi, APD3F2211CS(IS)
# Program Name: functions.py
# Description: Functions that perform the tasks accordingly
# First Written On: 01/06/2023
# Last Edited On:  22/07/2023

import pandas as pd
from wordcloud import WordCloud
import joblib
import nltk
from nltk.tokenize import word_tokenize
import string
from .constants import *
from datetime import *
from dateutil.relativedelta import *
from .models import *
import re
import nltk
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
from nltk.corpus import stopwords

nltk_stop_words = set(stopwords.words('english'))
punc = list(string.punctuation) + list('‘’')
stop_words = []

# Lexicon of negation cues references: Negation Scope Detection for Twitter Sentiment Analysis + manual filter from nltk stop words
negations = ['aint', 'doesnt', 'havent', 'lacks', 'none', 'mightnt', 'shouldnt', 'cannot', 'dont', 'havnt', 'neither', 'nor', 'mustnt', 'wasnt', 'cant', 'hadnt', 'isnt', 'never', 'not', 'neednt', 'without', 'darent' 'hardly', 'lack', 'no', 'nothing', 'oughtnt', 'wouldnt', 'didnt', 'hasnt', 'lacking', 'nobody', 'nowhere', 'shant', 'ain', 'doesn', 'haven', 'mightn', 'shouldn', 'havn', 'mustn', 'wasn', 'hadn', 'isn', 'needn', 'oughtn', 'wouldn', 'didn', 'hasn', 'shan', 'couldn', 'won', 'don', 'aren', 'arent', 'weren', 'werent' 'against']

for w in nltk_stop_words:
    if not w in negations:
        stop_words.append(w)
        
def remove_emojis(data):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)

def remove_tags(string):
    result = re.sub(r'@[A-Za-z0-9]{0,}(\s|\b)', '', string)   #remove @ tags
    result = re.sub(r'#[A-Za-z0-9]{0,}(\s|\b)', '', result)   #remove # tags
    result = re.sub(r'\b((http|https):\/\/)[-a-zA-Z0-9@:%._\\+~#?&\/\/=]{0,}','',result)   #remove URLs
    result = re.sub(r'\b((http|https):\/\/)[-a-zA-Z0-9@:%._\\+~#?&\/\/=]{0,}','',result)   #remove URLs
    result = remove_emojis(result)    # remove emojis
    result = result.lower()
    
    return result

def text_preprocessing(data_list):
    data = pd.DataFrame({'clean_text': data_list})
    
    data['clean_text'] = data['clean_text'].apply(lambda cw : remove_tags(cw)) 
    data['clean_text'] = data['clean_text'].apply(lambda x: x.replace('"', ''))
    data['clean_text'] = data['clean_text'].apply(lambda x: ' '.join([word for word in word_tokenize(x) if word not in (punc)]))
    data['clean_text'] = data['clean_text'].apply(lambda x: ' '.join([word for word in word_tokenize(x) if word not in (stop_words)]))
    data['clean_text'] = data['clean_text'].apply(lambda x: re.sub('\W+',' ',x).strip())
    data['clean_text'] = data['clean_text'].str.strip()

    return data['clean_text']

def word_cloud(responses, mode):
    sentences = []
    message = 'success'
    wordcloud = None
    
    for r in responses:
        words = word_tokenize(r.answer)
        words = text_preprocessing(words)
        words = [x for x in words if x != '' and not re.match(r'\b[A-Za-z]{1}\b', x)]
        
        if mode == 'word':
            sentences.append(' '.join([word for word in words]))
        elif mode == 'phrase':
            for i in range(0, len(words)-1):
                sentences.append('{}_{}'.format(words[i], words[i+1]))
   
    text = ' '.join([word for word in sentences])
    
    try:
        wordcloud = WordCloud().generate(text)
    except:
        message = 'error'
    
    return wordcloud, message

def load_model():
    model = joblib.load('website\\SVM_Sentiment.joblib')
    vectorizer = joblib.load('website\\vectorizer.pkl')
    
    return model, vectorizer

def get_recommendations(surveys, latest, user):
    recommendations = {}
    result = []
    latest_id = []
    for l in latest:
        latest_id.append(l.id)
    
    for s in surveys:
        recommendations[s.id] = []
        participated = Response.query.group_by(Response.date_submitted).filter_by(survey_id=s.id, user_id=user.id, status='Complete').count()
        
        # initialize recommendations dictionary
        if s.user_id == user.id:
            recommendations[s.id].append(-3)
            recommendations[s.id].append(s)
        elif participated > 0:
            recommendations[s.id].append(-2)
            recommendations[s.id].append(s)
        elif s.id in latest_id:
            recommendations[s.id].append(-1)
            recommendations[s.id].append(s)
        else:
            recommendations[s.id].append(0)
            recommendations[s.id].append(s)
            
            # add value whenever meeting 1 condition
            age_group = calc_age_group(user.dob, 'Short')
            respondents = Response.query.group_by(Response.date_submitted).filter_by(survey_id=s.id, status='Complete').count()
            nearest_id = find_nearest_date_closed(surveys)  # top 3 survey nearest to the date closed
            print(s.id, int(s.target) - respondents)
            
            if s.occupation_tag == user.occupation:
                recommendations[s.id][0] = recommendations[s.id][0] + 1
            if s.field_tag == user.field:
                recommendations[s.id][0] = recommendations[s.id][0] + 1
            if s.age_tag == age_group:
                recommendations[s.id][0] = recommendations[s.id][0] + 1
            if int(s.target) - respondents > 0:
                recommendations[s.id][0] = recommendations[s.id][0] + 1
            if s.id in nearest_id:
                recommendations[s.id][0] = recommendations[s.id][0] + 1
            if int(s.target) - respondents > 0 and s.id in nearest_id:
                recommendations[s.id][0] = recommendations[s.id][0] + 1
    
    # sort the dictionary in descending order
    recommendations = dict(sorted(recommendations.items(), key=lambda x:x[1][0], reverse=True))
    print(recommendations)
    
    # get the top 3 recommendations
    for k, v in recommendations.items():
        result.append(v[1])
        
        if len(result)  == 3:
            break
    
    return result

def calc_age_group(dob, mode):
    age_groups = get_age_group()
    age_group = ''
    
    today = date.today()
    bday = date(int(dob.split('-')[0]), int(dob.split('-')[1]), int(dob.split('-')[2]))
    age = relativedelta(today, bday).years
    
    for key in age_groups:
        min_age = int(key.split('-')[0])
        max_age = int(key.split('-')[1])
        
        if age >= min_age and age <= max_age:
            if mode == 'Full':
                age_group = age_groups[key]
            elif mode == 'Short':
                age_group = key
           
    return age_group

def find_nearest_date_closed(surveys):
    today = date.today()
    days_left = {}
    nearest_id = []
    
    for s in surveys:
        end_date = s.date_closed
        close_dt = date(int(end_date.split('-')[0]), int(end_date.split('-')[1]), int(end_date.split('-')[2]))
        days_left[s.id] = close_dt - today

    days_left = dict(sorted(days_left.items(), key=lambda x:x[1]))
    
    for k, v in days_left.items():
        nearest_id.append(k)
        
        if len(nearest_id)  == 3:
            break
            
    return nearest_id