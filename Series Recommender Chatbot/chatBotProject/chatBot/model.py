from sys import excepthook
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
import random
import re

class chatBot():
    def __init__(self):
        # To display full_text
        #pd.set_option('display.max_colwidth', -1)
        self.switchFlag = "NORMAL"
        self.seriesName = False
        self.seriesDetails = False
        self.rec_text = '\nHere are a few recommendations. Hope you enjoy !!'
        self.df = pd.read_csv("chatBot/static/series.csv")
        # Modifying the dataset
        self.df['Cast'] = self.df['Cast'].str.lower()
        self.df['Genre'] = self.df['Genre'].str.lower()
        self.df['Series Title'] = self.df['Series Title'].str.lower()
        self.df['Series Title'] = self.df['Series Title'].str.strip()
        self.df['Language'] = self.df['Language'].str.lower()
        self.df['Language'] = self.df['Language'].replace(['spanish; castilian'],'spanish')

        ### Functions for recommending series ###

        # Recommendations based on plot
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.df['Overview'] = self.df['Overview'].fillna('')
        # Construct the required TF-IDF matrix by applying 
        # the fit_transform method on the overview feature
        overview_matrix = self.tfidf.fit_transform(self.df['Overview'])
        self.similarity_matrix = linear_kernel(overview_matrix,overview_matrix)
        # series index mapping
        self.mapping = pd.Series(self.df.index,index = self.df['Series Title'])

        # username
        self.user_name = 'YOU'
        self.bot_template = "BOT : {0}"
        self.user_template = self.user_name + " : {0}"

        # basic questions 
        self.name = "Binge Bot" 
        self.weather = "rainy" 
        self.mood = "Happy"
        self.responses = { 
        "what's your name?": [ 
        "They call me {0}".format(self.name), 
        "I usually go by {0}".format(self.name), 
        "My name is the {0}".format(self.name)],

        "Are you a robot?": [ 
        "Maybe yes, maybe no!", 
        "Yes, I am a robot with human feelings."],

        "": [ 
        "Hey! Are you there?", 
        "What do you mean by saying nothing?", 
        "Sometimes saying nothing tells a lot :)"],

        "Hi":[
        "Hi there!",
        "Hello {0}!".format(self.user_name),
        "Hello there!"],

        "Thanks!":[
        "No problem, {0}!".format(self.user_name), 
        "Anytime!",
        "Happy to help!"],

        "No Thanks!":[
        "Alrighty. Bye {0}!".format(self.user_name)],

        "No":[
        "Alrighty. Bye {0}!".format(self.user_name)],

        "default": [
        "If confused what to watch next ask me for recommendations :)"] }

    

    # Recommendations based on language
    def lang_recommendation(self,lang):
        lang_recommendation = self.df.loc[self.df['Language'] == lang].sort_values(by = ['TMDB Popularity'])
        lang_recommendation = lang_recommendation[['Series Title', 'Year Released', 'Genre', 'Overview', 'Language']].head()
        return lang_recommendation

    # ML based Recomendations 
    def recommend_series_based_on_plot(self,series_input):
        try:
            series_index = self.mapping[series_input][0]
        except:
            try:
                series_index = self.mapping[series_input]
            except:
                print("Series not found !!")
                return("Series not found !!")
        # Get similarity values with other movies
        # Similarity_score is the list of index and similarity matrix
        similarity_score = list(enumerate(self.similarity_matrix[series_index]))

        # Sort in descending order the similarity score of movie inputted with all the other movies
        similarity_score = sorted(similarity_score, key=lambda x: x[1], reverse=True)

        # Get the scores of the 15 most similar movies. Ignore the first movie.
        similarity_score = similarity_score[1:15]

        # Return series names using the mapping series
        series_indices = [i[0] for i in similarity_score]
        return (self.df['Series Title'].iloc[series_indices])

    # Recommendations based on year
    def year_recommendation(self,year):
        year_recommendation = self.df.loc[self.df['Year Released'] == year].sort_values(by = ['TMDB Popularity'])
        year_recommendation = year_recommendation[['Series Title', 'Year Released', 'Genre', 'Overview', 'Language']].head()
        return year_recommendation

    # Series Details
    def series_details(self,series_name):
        series_df = self.df.loc[self.df['Series Title'] == series_name]
        return series_df

    # Recommendations based on genre
    def genre_recommendation(self,genre):
        genre_recommendation = self.df.loc[self.df['Genre'] == genre].sort_values(by = ['TMDB Popularity'])
        genre_recommendation = genre_recommendation[['Series Title', 'Year Released', 'Genre', 'Overview', 'Language']].head()
        return genre_recommendation

    # Function to reply to basic messages
    def respond(self,message):
        if message in self.responses: 
            bot_message = random.choice(self.responses[message])
        else: 
            bot_message = random.choice(self.responses["default"])
        return bot_message


    def related(self,user_text):
        #print(user_template.format(x_text))
        ut = user_text.lower()
        if "recommend" in ut or "popular" in ut or "best" in ut or "top" in ut or "suggest" in ut:
            self.switchFlag = "RECOMEND"

        elif "want details" in ut or "info about" in ut or "information" in ut or "series info" in ut or "series details" in ut:
            self.switchFlag = "DETAILS"

        #print(self.switchFlag)

        if self.switchFlag == "NORMAL":
            if "name" in ut: 
                user_text = "what's your name?"
            elif "robot" in ut: 
                user_text = "Are you a robot?"
            elif "hi" in ut or "hey" in ut or "hello" in ut:
                user_text = "Hi"
            elif "thank" in ut or "thanks" in ut or "thanks!" in ut: 
                user_text = "Thanks!"
            elif "no" in ut:
                user_text = "No"
            #print(user_text)
            bot_response = self.respond(user_text)
        
        elif self.switchFlag == "RECOMEND":
            langF = False
            res = True if next((chr for chr in ut if chr.isdigit()), None) else False
            if res is False:
                Languages = ['english', 'korean', 'chinese', 'japanese', 'spanish', 'german', 'arabic', 
                            'portuguese', 'french', 'turkish', 'polish', 'malay']
                
                Genres = ['drama', 'scifi','sci','science', 'fantasy', 'mystery', 'action', 'adventure', 'comedy', 'crime', 'family', 'animation', 'documentary', 'kids']
                
                def Convert(string):
                    li = re.sub(r'[^\w\s]', ' ', string)
                    li = list(li.split(" "))
                    #print(li)
                    return li
                
                li = Convert(ut)

                # Language Based Recommendation
                for i in li:
                    if i in Languages:
                        lang = i
                        lr = None
                        lr = self.lang_recommendation(lang)
                        #'Series Title', 'Year Released', 'Genre', 'Overview', 'Language'
                        #print(lr)
                        lang_rec = ''
                        if not lr.empty:
                            for index, row in lr.iterrows():
                                #print(row['Series Title'])
                                tmp ='\nName: '+str(row['Series Title'])  + '\nYear Released: ' + str(row['Year Released'])  + '\nGenre: ' + row['Genre'] + '\nLanguage: ' + row['Language'] + '\n\n' 
                                lang_rec = lang_rec + tmp
                            lang_rec = lang_rec + self.rec_text
                        else:
                            lang_rec = 'No series found !!'
                        #langF = True
                        self.switchFlag = "NORMAL"
                        return lang_rec

                # Genre Based Recommendation
                gCnt = 3
                genre_list = ''
                gFlag = False
                for i in li:
                    #print(i)
                    if i in Genres:   
                        gFlag = True
                        if gCnt > 0:
                            if i == 'fantasy' or i == 'sci' or i == 'scifi' or i == 'science':
                                genre_list = genre_list + 'sci-fi & fantasy, '
                            elif i == 'action' or i == 'adventure':
                                genre_list = genre_list + 'action & adventure, '
                            else:
                                genre_list = genre_list + i + ', '
                        gCnt = gCnt - 1
                    
                
                if gFlag == True:
                    # genre present in text
                    genre_list = genre_list[:-2]
                    #print(genre_list)
                    genre_rec = ''
                    gr = self.genre_recommendation(genre_list)
                    if not gr.empty:
                        for index, row in gr.iterrows():
                            #print(row['Series Title'])
                            tmp ='\nName: '+str(row['Series Title'])  + '\nYear Released: ' + str(row['Year Released'])  + '\nGenre: ' + row['Genre'] + '\nLanguage: ' + row['Language'] + '\n\n' 
                            genre_rec = genre_rec + tmp
                        genre_rec = genre_rec + self.rec_text
                    else:
                        genre_rec = 'No series found !!'
                    #langF = True
                    self.switchFlag = "NORMAL"
                    return  genre_rec
               

                # Plot Based Recommendation
                if self.seriesName == False:
                    self.seriesName = True
                    return("Enter the series name based on which you want recommendations!")

                #series_name = input()
                series_name = user_text
                #print(user_template.format(series_name))
                cols = ['Series Title', 'Year Released', 'Genre', 'TMDB Popularity', 'Overview']
                recommended_series = pd.DataFrame(columns = cols)
                n = 5
                series_list = self.recommend_series_based_on_plot(series_name.lower())
                for i in series_list:
                    if n > 0:
                        df1 = self.df.loc[(self.df['Series Title'] == i)]
                        tmp_df = df1[['Series Title', 'Year Released', 'Genre', 'TMDB Popularity', 'Overview']]
                        recommended_series = pd.concat([recommended_series,tmp_df])
                    n = n - 1
                ML_rec = ''
                if not recommended_series.empty:
                    for index, row in recommended_series.iterrows():
                        #print(row['Series Title'])
                        tmp ='\nName: '+str(row['Series Title'])  + '\nYear Released: ' + str(row['Year Released'])  + '\nGenre: ' + row['Genre'] + '\nTMDB Popularity: ' + str(row['TMDB Popularity']) + '\nOverview: ' + row['Overview'] + '\n\n' 
                        ML_rec = ML_rec + tmp
                    ML_rec = ML_rec + self.rec_text
                        
                else:
                    ML_rec = 'Series not found'
            
                self.seriesName = False
                self.switchFlag = "NORMAL"
                return ML_rec
                
            # Year Recommendation
            elif res == True:
                year = ""
                for i in user_text:
                    if (i.isdigit()):
                        year = year + i 
                yr = "None"
                yr = self.year_recommendation(year)
                year_rec = ''
                if not yr.empty:
                    for index, row in yr.iterrows():
                        #print(row['Series Title'])
                        tmp ='\nName: '+str(row['Series Title'])  + '\nYear Released: ' + str(row['Year Released'])  + '\nGenre: ' + row['Genre'] + '\nLanguage: ' + row['Language'] + '\n\n' 
                        year_rec = year_rec + tmp
                    year_rec = year_rec + self.rec_text
                else:
                    year_rec = 'No series found !!'
                self.switchFlag = "NORMAL"
                return year_rec

            bot_response = self.respond(user_text)
            self.switchFlag = "NORMAL"
        
        elif self.switchFlag == "DETAILS":
            # display all details of a particular series.  
            # ask the user if they want recommendations based on the series.
            if self.seriesDetails == False:
                self.seriesDetails = True
                return("Enter the name of the series for which you want more details ?") 
            print(ut)
            sd = self.series_details(ut)
            series_details = ''
            if not sd.empty:
                for index, row in sd.iterrows():
                    #print(row['Series Title'])
                    tmp ='Following series was found:\n'+'\nName: '+str(row['Series Title'])  + '\nYear Released: ' + str(row['Year Released'])  + '\nGenre: ' + row['Genre'] + '\nLanguage: ' + row['Language'] + '\nEpisode Duration: '+ str(row['Episode duration']) + '\nOverview: ' + row['Overview'] + '\nSeries Link: ' + row['Series Link'] +  '\n\n' 
                    series_details = series_details + tmp
            else:
                series_details = 'No series found !!'    

            self.seriesDetails = False
            self.switchFlag = "NORMAL"
            return series_details      
        

        return bot_response