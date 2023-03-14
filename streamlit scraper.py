%%writefile app.py
import streamlit as st
import snscrape.modules.twitter as sntwitter
import pandas as pd
import datetime
import pymongo



client = pymongo.MongoClient("mongodb://localhost:27017/")  
mydb = client["Twitter_Database"]
tweets_df = pd.DataFrame()
word = st.text_input('Please enter a keyword')
start = st.date_input("From", datetime.date(2022, 1, 1),key='d1')
end = st.date_input("To", datetime.date(2023, 3, 11),key='d2')
tweet_c = st.slider('How many tweets do you want to scrape?', 0, 250, 50)
tweets_list = []

# Snscraper
if word:
    
    for i,tweet in enumerate(sntwitter.TwitterSearchScraper(f'{word} + since:{start} until:{end}').get_items()):
        if i>tweet_c:
            break
            tweets_list.append([ tweet.id, tweet.date,  tweet.content, tweet.lang, tweet.user.username,tweet.likeCount ])
        tweets_df = pd.DataFrame(tweets_list, columns=['ID','Date','Content', 'Language', 'Username', 'LikeCount'])
    




# Download data with different format


if not tweets_df.empty:
    col1, col2 = st.columns(2)
    with col1:
        csv = tweets_df.to_csv().encode('utf-8')
        csv_file=st.download_button(label="Download data as CSV",data=csv,file_name='Twitter_data.csv')        
    with col2:   
        json_string = tweets_df.to_json(orient ='records')
        json_file=st.download_button(label="Download data as JSON",file_name="Twitter_data.json",data=json_string)

    

    if csv_file:
        st.success("Downloaded your csv file")  
    if json_file:
        st.success("Downloaded your json file")     
    

    if st.button('Upload Tweets to Database'):
        coll=word
        coll=coll.replace(' ','_')+'_Tweets'
        mycoll=mydb[coll]
        dict=tweets_df.to_dict('records')
        if dict:
            mycoll.insert_many(dict) 
            ts = time.time()
            mycoll.update_many({}, {"$set": {"KeyWord_or_Hashtag": word+str(ts)}}, upsert=False, array_filters=None)
            st.success('Successfully uploaded to database', icon="✅")
            st.balloons()
        else:
            st.warning('Cant upload because there are no tweets', icon="⚠️")

    # SHOW TWEETS
    if st.button('Show Tweets'):
        st.write(tweets_df)