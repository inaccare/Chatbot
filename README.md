Chatbot:
This program is for a movie-recommending chatbot which will recommend movies to the user based on the user's prior input.  It uses item-item collaborative filtering and a utility matrix for ~6000 other users in order to make these recommendations.  It also comes with other features such as spell-checking the movie title the user input, responding to user emotions, remembering things said previously, and being able to recognize a movie based on an incomplete title as well as movies in foreign languages.

To run:
- Have Python 3
- Download all files here
- Unzip the data folder
run: python repl.py

Example Usage:
Welcome to Stanford CS124
     _______  _______         ___
    |       ||   _   |       |   |
    |    _  ||  |_|  | ____  |   |___
    |   |_| ||       ||____| |    _  |
    |    ___||       |       |   | | |
    |   |    |   _   |       |   |_| |
    |___|    |__| |__|       |_______|
     _______  __   __  _______  _______  _______  _______  _______  __
    |       ||  | |  ||   _   ||       ||  _    ||       ||       ||  |
    |       ||  |_|  ||  |_|  ||_     _|| |_|   ||   _   ||_     _||  |
    |       ||       ||       |  |   |  |       ||  | |  |  |   |  |  |
    |      _||       ||       |  |   |  |  _   | |  |_|  |  |   |  |__|
    |     |_ |   _   ||   _   |  |   |  | |_|   ||       |  |   |   __
    |_______||__| |__||__| |__|  |___|  |_______||_______|  |___|  |__|




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

IAN> Hello! My name is IAN! I'm here to help you with all of your movie-selecting needs! But first I need to hear about the movies you like in order to make recommendations. Can you tell me about movies you like or dislike? Please put the movie title in quotation marks!
> I liked "27 Dresses"
IAN> I understand that you liked "27 Dresses." Thanks!
> I didn't like "Legion"
IAN> Got it, not a huge fan of "Legion." Thanks!
> I hated "The Crazies"!
IAN> Honestly, didn't like "The Crazies" much either. Great minds think alike!
> I really loved "Larry Crowne"!!!
IAN> Wow! "Larry Crowne" must be one of your all-time favorites, huh? Will certainly keep that in mind!
> A lot of people hated "Couples Retreat", but I really liked it!
IAN> Thanks for sharing! Can you tell me a bit more about how you felt about "couples retreat (2009)" so I can make the best recommendation for you?
> it was good
IAN> I understand that you liked "Couples Retreat." Thanks!
I now have enough to recommend a movie!
You should watch: The Wedding Planner.
To get another recommendation, type 'recommend'. You can also tell me about another movie so I can further optimize my recommendations!
To restart the search process, type 'restart'.
You can also type ':quit' if you'd like to exit
> recommend
IAN> You should watch: Little Nicky.
To get another recommendation, type 'recommend'. You can also tell me about another movie so I can further optimize my recommendations!
To restart the search process, type 'restart'.
You can also type ':quit' if you'd like to exit
> recommend
IAN> You should watch: A Knight's Tale.
To get another recommendation, type 'recommend'. You can also tell me about another movie so I can further optimize my recommendations!
To restart the search process, type 'restart'.
You can also type ':quit' if you'd like to exit

More Example Usage:
IAN> Hello! My name is IAN! I'm here to help you with all of your movie-selecting needs! But first I need to hear about the movies you like in order to make recommendations. Can you tell me about movies you like or dislike? Please put the movie title in quotation marks!
> I liked "Star Wars"
IAN> It appears there are several movies with the name Star Wars. Here are your choices:
star wars: episode ii - attack of the clones (2002), star wars: episode vii - the force awakens (2015), star wars: episode v - the empire strikes back (1980), star wars: episode iv - a new hope (1977), star wars: episode vi - return of the jedi (1983), star wars: episode iii - revenge of the sith (2005), empire of dreams: the story of the 'star wars' trilogy (2004), star wars: the clone wars (2008), star wars: episode i - the phantom menace (1999).  Please pick one!
> iii
IAN> I understand that you liked "Star Wars: Episode III - Revenge of the Sith." Thanks!
> I liked "Shi di chu ma"
IAN> I understand that you liked "The Young Master." Thanks!
> I don't get the hype about "27 Dresses". I really didn't like it
IAN> Got it, not a huge fan of "27 Dresses." Thanks!
> I'm very happy!
IAN> Stoked to hear you're feeling that way! Let's use that positive energy and select a great movie for you :)
> I didn't like "Legon"
IAN> Sorry, I am not familiar with Legon.  Did you mean "legion"?[y/n]
> y
IAN> Gotcha, I've already got that you didn't like "Legion." How about a movie that you did like now?
> I thought "Spider-Man" was okay
IAN> I understand that you liked "Spider-Man." Thanks!
I now have enough to recommend a movie!
You should watch: Star Wars: Episode V - The Empire Strikes Back.
To get another recommendation, type 'recommend'. You can also tell me about another movie so I can further optimize my recommendations!
To restart the search process, type 'restart'.
You can also type ':quit' if you'd like to exit
