# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals
from github3.repos.repo import Repository
import os
import re
import pymongo


class StarredDB(object):

	def __init__(self, mode):
		client = pymongo.MongoClient()
		db = client['oh-my-stars']
		collection = db.stars
		latest = db.latest
		self._db = db
		self.mode = mode
		self._col = collection
		self._latest = latest

	def __enter__(self):
		return self
	def __exit__(self, type, value, traceback):
		return
	def _calculate_ngrams(self, word, n):
	  return [ u''.join(gram) for gram in zip(*[word[i:] for i in range(n)])]

	def _update_inverted_index(self, index_name, key, eid):

		index = self._idx.get(index_name)

		id_list = index.get(key, [])
		if eid not in id_list:
			id_list.append(eid)

		index[key] = id_list

	def _build_index(self):
		self._col.ensure_index([('name', pymongo.TEXT), ('language', pymongo.TEXT), ('description', pymongo.TEXT)], name='search_index_name', default_language="en", language_override="en")

	def update(self, repo_list):

		if self.mode == 't':
			self._col.drop()

		if repo_list:
			self._latest.drop()
			self._latest.insert(repo_list[0])

		for repo in repo_list:

			# save repo data
			self._col.insert(repo)

	def get_latest_repo_full_name(self):
		latest_repo = self._latest.find_one()
		if latest_repo and latest_repo.full_name:
			return latest_repo.full_name
		else:
			return ''


	def search(self, languages, keywords):

		self._build_index()

		language_results = []
		if languages:
			for search in languages:
				res = self._col.find({'language': re.compile(search, re.IGNORECASE)})
				for doc in res:
					language_results.append(doc)

		keywords_results = []
		if keywords:
			for word in keywords:
				results = self._col.find({'description': re.compile(word, re.IGNORECASE)})
				for result in results:
					keywords_results.append(result)

		if languages and keywords:
			# python > 2.6
			search_results = list(set(
				language_results).intersection(*keywords_results))
		else:
			search_results = language_results + keywords_results
		return search_results
