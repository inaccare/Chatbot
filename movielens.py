#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PA 6, CS124, Stanford, Winter 2018
# v.1.0.2
######################################################################

import csv
import numpy as np
import re

def ratings(src_filename='data/ratings.txt', delimiter='%', header=False, quoting=csv.QUOTE_MINIMAL):
	title_list = titles()
	user_id_set = set()
	with open(src_filename, 'rt', encoding="utf-8") as f:
	    content = f.readlines()
	    for line in content:
	        user_id = int(line.split(delimiter)[0])
	        if user_id not in user_id_set:
	            user_id_set.add(user_id)
	num_users = len(user_id_set)
	num_movies = len(title_list)
	mat = np.zeros((num_movies, num_users))

	reader = csv.reader(open(src_filename, "rt", encoding="utf-8"), delimiter=delimiter, quoting=quoting)
	for line in reader:
		mat[int(line[1])][int(line[0])] = float(line[2])
	return title_list, mat

def titles(src_filename='data/movies.txt', delimiter='%', header=False, quoting=csv.QUOTE_MINIMAL):
	reader = csv.reader(open(src_filename, "rt", encoding="utf-8"), delimiter=delimiter, quoting=quoting)
	title_list = []
	for line in reader:
		movieID, title, genres = int(line[0]), line[1], line[2]
		if title[0] == '"' and title[-1] == '"':
			title = title[1:-1]
		title_list.append([title, genres])
	return title_list

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

