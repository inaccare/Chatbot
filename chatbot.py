#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA6, CS124, Stanford, Winter 2018
# v.1.0.2
# Original Python code by Ignacio Cases (@cases)
######################################################################
import csv
import math
import re
import numpy as np
from PorterStemmer import PorterStemmer
from movielens import ratings
from random import randint
import random
#from scipy import spatial
import collections

# Title dictionary fields
PARSED  = "parsed"
PSEUDOS = "pseudonyms"
YEAR    = "year"
INDEX   = "index"
GENRES  = "genres"
CAP     = "capitalized"


def replace_articles(title):
    # Remove leading and trailing whitespaces
    title = title.strip()
    
    # To remove the a, an, the, we must first deal with the comma case
    articles = ['a', 'an', 'the']
    for art in articles:
        if title.lower().endswith(', ' + art):
            title = title[:len(title) - len(", " + art)]
        if title.lower().startswith(art + ' '):
            title = title[len(art + " "):]
    return title.strip()

def parse_year(title):
    # First get the year using a regex.
    year = re.findall("\(([0-9]+-?[0-9]*)\)", title)
    m_year = "" 
    if len(year) > 0:
        # Take the year out of th title
        title = title.replace("(" + year[0] + ")", "")
        m_year = year[0]
    return title, m_year

def parse_pseudonyms(title):
    # Now loop through and get all pseudoyms
    pseudonyms = []
    start_ind = title.find("(")
    while start_ind != -1:
        # find corresponding 
        stop_ind = title[start_ind:].find(")")
        stop_ind += start_ind
        if stop_ind == -1:
            break
        pseudo = title[start_ind + 1:stop_ind]
        
        # Strip out aka
        akas = ['aka ', 'a.k.a. ']
        for ak in akas:
            if pseudo.startswith(ak):
                pseudo = pseudo[len(ak):]
        pseudonyms.append(replace_articles(pseudo))
        title = title.replace(title[start_ind:stop_ind+1], "")
        start_ind = title.find("(")
    return title, pseudonyms

def move_articles(title):
    title = title.strip()
    articles = ['A', 'An', 'The']
    for art in articles:
        if title.lower().endswith(', ' + art.lower()):
            title = art + ' ' + title[:len(title) - len(", " + art)]
    return title

"""
This function will take a title and strip out the year and other names (whether it be
an "aka" name or a foreign name).  It additionally will strip out the beginning articles
for a film (ie The, a, an).  It returns the title, a list of other names, the year, and the
proper name of the film to use when printing out stuff.
A large assumption in this is that any parenthesis in the title contain the year or a pseudonym
"""
def title_parse(title):
    title, m_year = parse_year(title)
    title, pseudonyms = parse_pseudonyms(title)
    full_title = move_articles(title)
    title = replace_articles(title)
    return title, pseudonyms, m_year, full_title


class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    #############################################################################
    # `moviebot` is the default chatbot. Change it to your chatbot's name       #
    #############################################################################
    def __init__(self, is_turbo=False):
      self.name = 'IAN'
      self.is_turbo = is_turbo
      self.read_data()
      self.stemmer = PorterStemmer()
      self.counter = 0
      self.already_seen = []
      self.recommendations = []
      self.delimiters = [".", ",", ";", "!", "?", ":"]
      self.usersentiment = 0
      self.usermovie = ""
      self.clarify = 0
      self.check_spelling_flag = 0
      # build stemmed dictionary
      self.stemmed_sentiment = {}
      for word in self.sentiment.keys():
        self.stemmed_sentiment[self.stemmer.stem(word, 0, len(word)-1)] = self.sentiment[word]
      # build editCounts dictionary for spell checking
      self.editCounts = collections.defaultdict(list)
      with open("deps/count_1edit.txt") as f:
        for line in f:
          rule, countString = line.split("\t")
          originalText, editedText = rule.split("|")
          if self.editCounts[originalText] is None:
            self.editCounts[originalText] = [(editedText, int(countString))]
          else:
            self.editCounts[originalText].append((editedText, int(countString)))
            sorted(self.editCounts[originalText], key=lambda x: x[1])
      self.check_spelling = ""
      self.already_mentioned = []
      self.fromList = []

    #############################################################################
    # 1. WARM UP REPL
    #############################################################################

    def greeting(self):
      """chatbot greeting message"""
      #############################################################################
      # TODO: Write a short greeting message                                      #
      #############################################################################

      greeting_message = """Hello! My name is IAN! I'm here to help you with all of your movie-selecting needs! But first I need to hear about the movies you like in order to make recommendations. Can you tell me about movies you like or dislike? Please put the movie title in quotation marks!"""

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return greeting_message

    def goodbye(self):
      """chatbot goodbye message"""
      #############################################################################
      # TODO: Write a short farewell message                                      #
      #############################################################################

      goodbye_message = 'I hope this was helpful! Enjoy your movie :)'

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

      return goodbye_message

    #############################################################################
    # 2. Modules 2 and 3: extraction and transformation                         #
    #############################################################################
    def process(self, input):
      """Takes the input string from the REPL and call delegated functions
      that
        1) extract the relevant information and
        2) transform the information into a response to the user
      """
      #############################################################################
      # TODO: Implement the extraction and transformation in this method, possibly#
      # calling other functions. Although modular code is not graded, it is       #
      # highly recommended                                                        #
      #############################################################################
      #if self.is_turbo == True:
      #  response = 'processed %s in creative mode!!' % input
      #else:
      if 'recommend' in input and self.counter >= 5:
        return self.give_recommendation()
      elif input == 'recommend':
        return "I need at least 5 data points to make a recommendation!"
      if input == 'restart':
        self.reset()
        return "Preferences reset! Please tell me about movies you like or dislike!"
      if len(self.fromList) > 0:
#        print(self.fromList)
        for titleTemp in self.fromList:
          if input.replace('"', '').lower() in titleTemp.lower().split():
#            print(titleTemp)
            response = self.form_response(self.usersentiment, titleTemp, None)
            self.fromList = []
            return response
      if self.clarify == 0:
        movie, response, movie_in = self.get_movie(input)
        if type(movie) is list:
          self.fromList = movie
          return "It appears there are several movies with the name " + movie_in + ". Here are your choices: \n" + ", ".join(movie) + ".  Please pick one!"
        elif movie is None:
          return response
        elif (movie == "Unclear" and self.usersentiment == 0):
          response = self.form_response(self.usersentiment, self.usermovie, movie_in)
          return response
        elif (movie == "Unclear" and self.usersentiment != 0) or (self.usersentiment == 0 and movie != "Unclear"):
          self.clarify = 1
          response = self.form_response(self.usersentiment, self.usermovie, movie_in)
          return response
        else:
          response = self.form_response(self.usersentiment, movie, None)
          self.already_mentioned.append(movie)
          self.clearFlags()
          return response

      else:
        if self.usersentiment == 0 and self.usermovie != "":
          self.usersentiment = self.get_sentiment(input)
          response = self.form_response(self.usersentiment, self.usermovie, None)
          self.already_mentioned.append(self.usermovie)
          self.clearFlags()
          return response
        elif self.usersentiment != 0 and self.usermovie == "" and self.check_spelling_flag == 1:
          if 'y' in input:
            movie, _, year, _ = title_parse(self.check_spelling)
            key = self.find_movie(movie.lower(), year)
            self.usermovie = key
            self.already_mentioned.append(self.usermovie)
            response = self.form_response(self.usersentiment, self.usermovie, None)
            self.clearFlags()
          if 'n' in input:
            self.check_spelling = ""
            self.check_spelling_flag = 0
            response = self.form_response(self.usersentiment, self.usermovie, "this movie")
          return response
        elif self.usersentiment != 0 and self.usermovie == "":
          if input == 'no':
            return "Please tell me about a different movie then!"
          sentimentHolder = self.usersentiment
          movie, response, movie_in = self.get_movie(input)
          self.usersentiment = sentimentHolder
          if movie is None:
            return response
          elif movie == "Unclear":
            response = self.form_response(self.usersentiment, self.usermovie, movie_in)
            return response
          else:
            response = self.form_response(self.usersentiment, movie, None)
            self.already_mentioned.append(movie)
            self.clearFlags()
            return response
        else:
          response = self.form_response(self.usersentiment, self.usermovie, None)
          self.already_mentioned.append(self.usermovie)
          self.clearFlags()
          return response

    def clearFlags(self):
      self.usersentiment = 0
      self.usermovie = ""
      self.clarify = 0
      self.check_spelling_flag = 0
      self.check_spelling = ""

    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################
    """
    To deal with year ambiguities, the key to the dictionary will be title (year).
    So, we must do a search for the movie in case they do not pass in the year.
    """
    def find_movie(self, movie, year):
      movie = movie.lower()
      key = movie
      if key in self.titles_dict or key in self.pseudonyms:
        return key
      if year != "":
        key += ' (' + year + ')'
        if key in self.titles_dict or key in self.pseudonyms:
          return key
      # Now need to search through movies to see if we can find the movie
      for k in self.titles_dict.keys():
        if self.titles_dict[k][PARSED] == movie:
          return k
      return None
    
    """
    This function takes in an input string and extracts the movie.  If no movie
    is detected, the movie is not recognized, or there are two movies in the
    string, the movie is returned as None and a response string is returned.
    I added an additional output that is what they wrote in for the movie as
    the third argument returned.
    """
    def get_movie(self, s):
      q = '"'
      matches = re.findall(q + '([^"]+)' + q, s)
      movie_input = ""
      # Check they gave us a movie in quotations

      # EMOTIONS
      if len(matches) < 1:
        if re.search("angry", s) != None or re.search("upset", s) != None or re.search("outrag", s) != None or re.search("sad", s) != None or re.search("disappoint", s) != None or re.search("depress", s) != None or re.search("enraged", s) != None or re.search("hate", s) != None:
          return None, "I'm sorry to hear you're not feeling too happy. Why don't I try to help you find a movie that will cheer you up?", movie_input

        if re.search("ill", s) != None or re.search("unwell", s) != None or re.search("tired", s) != None or re.search("exhausted", s) != None or re.search("overwhelmed", s) != None:
          return None, "I'm sorry to hear you're not feeling well. Movies are a great way to feel better! Let me know what you might like and I can help pick one out for you.", movie_input
        
        if re.search("happy", s) != None or re.search("ecstatic", s) != None or re.search("joyful", s) != None or re.search("upbeat", s) != None or re.search("awesome", s) != None:
          return None, "Stoked to hear you're feeling that way! Let's use that positive energy and select a great movie for you :)", movie_input
        
        if re.search("annoyed", s) != None or re.search("bored", s) != None or re.search("done", s) != None or re.search("stop", s) != None:
          return None, "Is it something I said? You can always type ':quit' if you're not in the mood right now!", movie_input

        if re.search("confused", s) != None or re.search("shy", s) != None or re.search("suspiscious", s) != None or re.search("frightened", s) != None or re.search("cautious", s) != None:
          return None, "I don't bite, I promise! Just talk to me like you'd talk to your frind about movies you like!", movie_input

        if  re.search("lonely", s) != None or re.search("alone", s) != None or re.search("depressed", s) != None:
          return None, "I'll be your friend! Why don't we get back to choosing a movie for you! A good movie will make you feel like you really KNOW the characters", movie_input

        if re.search("lovestruck", s) != None:
          return None, "Let's find you a good romcom ;)", movie_input

        # ARBITRARY INPUT
        if re.search("[Ww]hat is", s) != None:
          separated = re.split("[Ww]hat is", s)
          return None, "I'm not sure what%s is...let's get back to helping you find a good movie!" %separated[1], movie_input

        if re.search("[Hh]ow do[es]*", s) != None:
          separated = re.split("[Hh]ow do[es]*", s)
          return None, "I'm not sure how%s...let's get back to helping you find a good movie!" %separated[1], movie_input

        if re.search("[Cc]an you", s) != None:
          separated = re.split("[Cc]an you", s)
          return None, "The question isn't can I%s? It's WILL I! Okay jokes aside...let's get back to helping you find a good movie!" %separated[1], movie_input

        if re.search("[Ww]here do[es]*", s) != None:
          return None, "Hmmm...%s...that seems like a question for Google, not IAN. All I know about are movies :)" %s, movie_input   

        movie_not_found_messages = ["Don't think I caught a movie there...please try again making sure its in quotation marks!", "Are you sure you gave me a movie there? Didn't quite catch it!", "Let's get back on track here...we're supposed to be discussing movies! Remember to put them in quotation marks.", "Hmmm didn't catch a movie there. Is this your way of telling me you're bored? Movies are fun! Just be sure to put them in quotation marks ;)", "Didn't catch a title there...I think we're getting a little off topic, let's go back to movies!"]
        if len(matches) < 1:
          return None, random.choice(movie_not_found_messages), movie_input
      
      # Check they only gave us one movie
      if len(matches) > 1:
        return None, "Ruh roh system overload! Unfortunately, I can only process one movie at a time and I think you might've given me more. Can you try again listing just one per statement?", movie_input
      
      # Parse movie title
      movie, _, year, _ = title_parse(matches[0])
      movie_input = matches[0]
      key = self.find_movie(movie.lower(), year)
      
      sentence = s.replace('"' + movie + '"', "")
      self.usersentiment = self.get_sentiment(sentence)

      # Check that this is a movie we have seen. 
      if key is None:
        self.check_spelling = self.spellcheck(movie, year)
        if self.check_spelling != "":
          self.check_spelling_flag = 1
        seriesList = self.checkForSeries(movie_input)
        if len(seriesList) > 0:
          return seriesList, None, movie_input
        return "Unclear", None, movie_input
      
      # Return the movie, None, and what they input
      if key in self.pseudonyms:
        self.usermovie = self.pseudonyms[key]
        return self.pseudonyms[key], None, movie_input
      self.usermovie = key
      return key, None, movie_input
    
    def checkForSeries(self, movie_input):
      seriesList = []
      validTitles = list(self.titles_dict.keys())
      for title in validTitles:
        if movie_input.lower() in title:
          seriesList.append(title)
      return seriesList

    def checkMovieTitleWord(self, word, index, validTitles, count):
      newTitles = []
      for title, count in validTitles:
        words = title.lower().split(" ")
        if words[index] == word.lower():
          newTitles.append((title, count))

      return newTitles

    """
    Checks the spelling of a movie and returns a list of suggested titles.
    Uses the editCounts from assignment 2 to look for errors
    """
    def spellcheck(self, movie_title, year):
      validTitles = list(self.titles_dict.keys())
      suggestion_list = []
      movie_title_words = movie_title.lower().split(" ")

      validTitles = [(self.titles_dict[title][PARSED], 1) for title in validTitles if len(self.titles_dict[title][PARSED].split(" ")) == len(movie_title_words)]

      # Loop over each word in title
      for wordIndex in range(len(movie_title_words)):
        suggestedTitles = []
        word = movie_title_words[wordIndex]
        # Loop over letters one at a time
        for letterIndex in range(len(word)):
          letter = word[letterIndex]
          if letter in self.editCounts.keys():
            for option in self.editCounts[letter]:
              newLetter, count = option
              newWord = word[:letterIndex] + newLetter + word[letterIndex+1:]
              suggestedTitles.extend(self.checkMovieTitleWord(newWord, wordIndex, validTitles, count))

        # Loop over letters two at a time
        for letterIndex2 in range(len(word)-1):
          letters = word[letterIndex2:(letterIndex2+2)]
          if letters in self.editCounts.keys():
            for option in self.editCounts[letters]:
              newLetter, count = option
              newWord = word[:letterIndex2] + newLetter + word[letterIndex2+2:]
              suggestedTitles.extend(self.checkMovieTitleWord(newWord, wordIndex, validTitles, count))
        suggestedTitles.extend(self.checkMovieTitleWord(word, wordIndex, validTitles, count))

        validTitles = suggestedTitles

      sorted(validTitles, key=lambda x: x[1])
      if len(validTitles) > 0:
        title, count = validTitles[0]
        return title
      else:
        return ""

    """
    This function will return the sentiment.  Currently it takes a count of positive
    and negative words with a few additions.  It checks if each word or its stem
    is in the list of sentiment words.  It also weights double the words appearing
    at the end of the sentence.  It also hangs onto negation words such as "none"
    or "not" and switches the sentiment of the following words until hitting a delimiter
    or the words "but" or "however."  Returns a number where positive
    is positive sentiment, negative is negative sentiment, and 0 is neutral.
    """
    def get_sentiment(self, sentence):
      sent = 0
      negation_words = ["not", "never", "neither", "nor", "no", "none", "nobody"]
      intensifying_words = ["very", "really", "especially", "totally", "lot", "completely", "absolutely", "definitely", "truly"]
      strong_pos_sentiment = ["love", "loved", "incredible", "amazing", "best", "favorite", "unparalleled", "blown", "adore", "adored", "wonderful", "outstanding"]
      strong_neg_sentiment = ["hate", "hated", "despise", "despised", "worst", "least", "crap", "terrible", "horrible", "horrendous", "atrocious", "never", "sucks"]
      negation_token = False
      negation_effect = 1
      counter = 0

      if re.search("\"", sentence) != None:
        start = sentence.find('\"')
        end = sentence.rfind('\"')
        if start != -1 and end != -1:
          sentence = sentence[:start] + sentence[end + 1:]

      for word in sentence.split(" "):
        counter += 1 # keep track if we're near the end of the review
        if word is not "":
          # switches sentiment of words if negation word is active
          if negation_token: negation_effect = -1
          if not negation_token: negation_effect = 1
          
          # turns off negation
          if (word[len(word)-1] in self.delimiters or word == "but" or word == "however") and negation_token == True:
            negation_token = False
          # turns on negation
          if word in negation_words or re.search("n\'*t$", word) != None:
            negation_token = True
          # removes delimiters from end of words
          if word[len(word)-1] in self.delimiters:
            word = word[:-1]
          # doubles weight of word if near end of statement
          if len(sentence.split(" ")) - counter < 3:
            negation_effect *= 2
        
          if word in self.sentiment:
            sent += 1*negation_effect if self.sentiment[word] == 'pos' else -1*negation_effect
          elif self.stemmer.stem(word, 0, len(word)-1) in self.stemmed_sentiment:
            word = self.stemmer.stem(word, 0, len(word)-1)
            sent += 1*negation_effect if self.stemmed_sentiment[word] == 'pos' else -1*negation_effect
          if word in strong_neg_sentiment and negation_token == False:
            sent -= 1
          if word in strong_pos_sentiment and negation_token == False:
            sent += 1
        # print(word)
        # print(sent)
      if re.search("!+", sentence):
        sent *= 1.25

      multiplier = len(re.findall('very|really|especially|totally|lot|completely|absolutely|definitely|truly"', sentence))
      multiplier = min(multiplier,2)
      sent *= (multiplier + 1)
      #print(sent)
      return sent

    def give_recommendation(self):
      restart = "To restart the search process, type 'restart'. \n"
      rerecommend = "To get another recommendation, type 'recommend'. You can also tell me about another movie so I can further optimize my recommendations! \n"
      response = "You didn't like any of those recommendations?! Okay... " 
      quit = "You can also type ':quit' if you'd like to exit"
      if len(self.recommendations) == 0:
        return response + restart + quit
      movie = self.recommendations[0]
      self.recommendations = self.recommendations[1:]
      movie, _, year, _ = title_parse(movie)
      while movie in self.already_seen and len(self.recommendations) > 0:
        movie = self.recommendations[0]
        self.recommendations = self.recommendations[1:]
        movie, _, year, _ = title_parse(movie)
      if movie not in self.already_seen:
        key = self.find_movie(movie, year)
        response = "You should watch: " + self.titles_dict[key][CAP] + '.\n'
        response += rerecommend
      self.already_seen.append(movie)
      return response + restart + quit


    def form_response(self, sent, movie, movie_name):
      # First update the user ratings vector and form initial repsonse
      if movie == "" and sent != 0:
        if self.check_spelling_flag == 1:
          movie, _, year, _ = title_parse(self.check_spelling)
          response = "Sorry, I am not familiar with " + movie_name + ".  Did you mean \"" + movie + "\"?[y/n]"
        else:
          response = "Sorry, I am not familiar with " + movie_name + ".  Do you know it by any other name? (Please provide the name - in quotes ideally :))"
      
      elif movie != "" and sent == 0:
        response = "Thanks for sharing! Can you tell me a bit more about how you felt about \"" + movie + "\" so I can make the best recommendation for you?"

      elif movie == "" and sent == 0:
        self.clearFlags()
        response = "I didn't quite catch that movie or if you liked it; could you try that again?"

      else:
        movieTemp, _, year, _ = title_parse(movie)
        moviekey = self.find_movie(movieTemp.lower(), year)
        if sent > 0:
          if str(moviekey) in self.already_mentioned:
            response = 'Perfect, I\'ve already got that you liked \"%s.\" Tell me about another movie!' % self.titles_dict[movie][CAP]
          else:
            if sent > 0 and sent <= 2:
              score = 1
              response = 'I understand that you liked "%s." Thanks!' % self.titles_dict[movie][CAP]
            if sent > 2 and sent <= 4:
              score = 2
              response = '"%s" is a favorite of mine too! Good choice ;)' % self.titles_dict[movie][CAP]
            if sent > 4: 
              score = 2.5
              response = 'Wow! "%s" must be one of your all-time favorites, huh? Will certainly keep that in mind!' % self.titles_dict[movie][CAP]
            self.user_ratings.append((self.ratings[self.titles_dict[movie][INDEX]], score))
        elif sent < 0:
          if str(moviekey) in self.already_mentioned:
            response = 'Gotcha, I\'ve already got that you didn\'t like \"%s.\" How about a movie that you did like now?' % self.titles_dict[movie][CAP]
          else:
            if sent < 0 and sent >= -2:
              score = -1
              response = 'Got it, not a huge fan of "%s." Thanks!' % self.titles_dict[movie][CAP]
            if sent < -2 and sent >= -4:
              score = -2
              response = 'Honestly, didn\'t like "%s" much either. Great minds think alike!' % self.titles_dict[movie][CAP]
            if sent < -4:
              score = -2.5
              response = 'Woah there! What did "%s" ever do to you? Dont worry, I certainly won\'t suggest it!' % self.titles_dict[movie][CAP]
            self.user_ratings.append((self.ratings[self.titles_dict[movie][INDEX]] , score))
        if self.titles_dict[movie][PARSED] not in self.already_seen and sent != 0:
          self.counter += 1
          self.already_seen.append(self.titles_dict[movie][PARSED])
        if self.counter >= 5:
          # TIME TO RECOMMEND!!
          response += "\nI now have enough to recommend a movie!\n"
          self.recommendations = self.recommend(self.user_ratings)
          response += self.give_recommendation()
      
      return response

    """
    This function resets information about recommendations.
    """
    def reset(self):
      self.counter = 0
      self.already_seen = []
      self.recommendations = []
      self.already_mentioned = []
      self.user_ratings = []

    def read_data(self):
      """Reads the ratings matrix from file"""
      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j
      self.titles, self.ratings = ratings()
      self.normalize()

      #This will be a dictionary containing all information to a parsed title,
      #a list mapping pseudonyms to titles, and the initial user ratings vec
      self.titles_dict = {}
      self.pseudonyms = {}
      self.user_ratings = []
 
      # For storing, I thought maybe we could just use all lower case.  That way
      # we can generalize to the creative case right away.
      # The only problem we have here is we are assuming unique names...
      # Think I am going to change this a bit...
      for i in range(len(self.titles)):
        p_title, pseudos, year, f_title = title_parse(self.titles[i][0])
        key = p_title.lower()
        if year != "":
          key += ' (' + year + ')'
        self.titles_dict[key] = {
                PARSED  : p_title.lower(),   # Parsed version of title
                PSEUDOS : pseudos,           # List of pseudonyms
                YEAR    : year,              # Year the movie was made
                GENRES  : self.titles[i][1], # Genres of movie
                INDEX   : i,                 # Row index into the rating matrix
                CAP     : f_title            # Capitalized version of movie
                }
        for p in pseudos:
          self.pseudonyms[p.lower()] = key
      # !!!!!!!EDITED FOR PYTHON3!!!!!!!!
      reader = csv.reader(open('data/sentiment.txt', 'rt', encoding="utf-8"))
      self.sentiment = dict(reader)

    def normalize(self):
      """Modifies the ratings matrix to make all of the ratings normalized"""
      indst = np.where(self.ratings > 0)
      for i in range(indst[0].shape[0]):
        self.ratings[indst[0][i]][indst[1][i]] -= 2.5

    def binarize(self):
      """Modifies the ratings matrix to make all of the ratings binary"""
      inds = np.where(self.ratings >= 3.0)
      indst = np.where(self.ratings > 0)
      for i in range(indst[0].shape[0]):
        self.ratings[indst[0][i]][indst[1][i]] = -1
      for i in range(inds[0].shape[0]):
        self.ratings[inds[0][i]][inds[1][i]] = 1
      """ 
      for i in range(self.ratings.shape[0]):
          for j in range(self.ratings.shape[1]):
              r = int(self.ratings[i][j])
              self.ratings[i][j] = r
              if r > 0:
                  print r
       """
    def distance(self, u, v):
      """Calculates a given distance function between vectors u and v"""
      if np.linalg.norm(u) == 0 or np.linalg.norm(v) == 0:
        return 0
      return np.dot(u, v)/(np.linalg.norm(u) * np.linalg.norm(u))


    def recommend(self, u):
      """Generates a list of movies based on the input vector u using
      collaborative filtering"""
      # TODO: Implement a recommendation function that takes a user vector u
      # and outputs a list of movies recommended by the chatbot
      recommendations = [None, None, None]
      s1, s2, s3 = 0, 0, 0
      for i in range(self.ratings.shape[0]):
        p_title, _, year, _ = title_parse(self.titles[i][0])
        key = p_title.lower()
        if year != "":
          key += ' (' + year + ')'
        if self.titles_dict[key][PARSED] not in self.already_seen:
          i_rate = self.ratings[i]
          user_rating = sum([p[1] * self.distance(p[0], i_rate) for p in self.user_ratings])
          if user_rating > s1 or recommendations[0] is None:
            s3 = s2
            s2 = s1
            s1 = user_rating
            recommendations[1:] = recommendations[:2]
            recommendations[0] = self.titles[i][0]
          elif user_rating > s2 or recommendations[1] is None:
            s3 = s2
            s2 = user_rating
            recommendations[2] = recommendations[1]
            recommendations[1] = self.titles[i][0]
          elif user_rating > s3 or recommendations[2] is None:
            s3 = user_rating
            recommendations[2] = self.titles[i][0]
      """
      d = None
      user = None
      for i in range(self.ratings.shape[1]):
        dist = self.distance(u, self.ratings[:, i])
        if d is None or dist < d:
          d = dist
          user = i
      for j in range(self.ratings.shape[0]):
        if self.ratings[j][user] > 0:
          recommendations.append(self.titles[j][0])
      """
      return recommendations


    #############################################################################
    # 4. Debug info                                                             #
    #############################################################################

    def debug(self, input):
      """Returns debug information as a string for the input string from the REPL"""
      # Pass the debug information that you may think is important for your
      # evaluators
      debug_info = 'debug info'
      print(self.already_mentioned)
      return debug_info


    #############################################################################
    # 5. Write a description for your chatbot here!                             #
    #############################################################################
    def intro(self):
      return """
      The creative functionality of this chatbot is:
      - Fine-grained sentiment extraction
      - Spell-checking movie titles
      - Disambiguating movie titles for series and year ambiguities
      - Identifying and responding to emotions
      - Understanding references to things said previously:
        - this also notes whether or not you've already told us about a movie
      - Responding to arbitrary input
      - Speaking very fluently
      - Using non-binarized dataset
      - Alternate/foreign titles
      - Can type restart to reset selections or recommend to get a recommendation
      """


    #############################################################################
    # Auxiliary methods for the chatbot.                                        #
    #                                                                           #
    # DO NOT CHANGE THE CODE BELOW!                                             #
    #                                                                           #
    #############################################################################

    def bot_name(self):
      return self.name


if __name__ == '__main__':
    Chatbot()