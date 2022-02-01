import discord
import os
import sys
import requests
import json
from bs4 import BeautifulSoup

url_anssi_alert = "https://www.cert.ssi.gouv.fr/alerte/"
url_anssi_threats = "https://www.cert.ssi.gouv.fr/cti/"
url_anssi_threats_pdf = "https://www.cert.ssi.gouv.fr/uploads/"
url_anssi_opinions = "https://www.cert.ssi.gouv.fr/avis/"
url_anssi_ioc = "https://www.cert.ssi.gouv.fr/ioc/"
url_anssi_dur = "https://www.cert.ssi.gouv.fr/dur/"
url_anssi_actu = "https://www.cert.ssi.gouv.fr/actualite/"


async def darknetdiaries():
	###Avec BS, on vient parcourir la page pour obtenir le lien du dernier
	###episode/podcast
	url = "https://darknetdiaries.com/episode"
	page = requests.get(url)
	soup = BeautifulSoup(page.content, "html.parser")

	listing = soup.find_all("section", class_='listing')
	wrap = listing[0].find_all("div", class_="wrap")
	articles = wrap[0].find_all("article", class_="post")
	link = articles[0].find_all("a", class_="button")
	lien = link[0]['href']

	episodeurl = "https://darknetdiaries.com" + lien

	###On vient vérifier si le fichier existe
	###Si oui, on vérifie le lien qu'on vient de récupérer avec celui du fichier
	###S'ils sont identiques on ne fait rien et on retourne une chaine vide
	###Sinon on remplace le lien dans le fichier et on retourne le lien
	###Le retour sert pour le bot discord

	if os.path.isfile('darknet.txt'):
		f = open('darknet.txt', 'r')
		ancien = f.read()
		f.close()

		if episodeurl == ancien:
			return ""
		else:
			f = open('darknet.txt', 'w')
			f.write(episodeurl)
			f.close()
			return episodeurl
	else:
		f = open('darknet.txt', 'w')
		f.write(episodeurl)
		f.close()
		return episodeurl


async def zataz():
	liste = []
	mydict = {}
	dictToReturn = {}
	url = "https://www.zataz.com/cybersecurite/"
	page = requests.get(url)
	soup = BeautifulSoup(page.content, "html.parser")
	blog = soup.find_all("div", class_="blog-item-holder")
	articles = blog[0].find_all("div", class_="gdl-blog-medium")
	for article in articles:
		title = article.find("h2")
		link = title.find("a")
		content = article.find("div", class_="blog-content")
		liste.append(link["href"])
		mydict[link["href"]] = content.text.replace("\xa0", " ")

	if os.path.isfile("zataz.txt"):
		f = open("zataz.txt", "r")
		old = f.read()
		f.close()
		j = -1
		for i in range(len(liste)):
			if liste[i] == old:
				j = i
		if j == -1:
			j = len(liste)
		for i in range(0,j):
			dictToReturn[liste[i]] = mydict[liste[i]]
		f = open("zataz.txt", "w")
		f.write(liste[0])
		f.close()
	else:
		f = open("zataz.txt", "w")
		f.write(liste[0])
		f.close()
		dictToReturn[liste[0]] = mydict[liste[0]]
	
	return dictToReturn


async def it_guru_news():
	liste = []
	mydict = {}
	dictToReturn = {}
	url = "https://www.itsecurityguru.org/news/"
	page = requests.get(url)
	soup = BeautifulSoup(page.content, "html.parser")
	blog = soup.find_all("div", class_="jeg_posts")
	articles = blog[0].find_all("article", class_="jeg_post")

	for article in articles:
		title = article.find("h3", class_="jeg_post_title")
		thumb = article.find("div", class_="jeg_thumb")
		pre_link = thumb.find_all("a")
		link = pre_link[0]
		date = article.find("div", class_="jeg_meta_date")

		liste.append(link["href"])
		mydict[link["href"]] = []
		mydict[link["href"]].append(title.text.replace("\n",""))
		mydict[link["href"]].append(date.text)

	if os.path.isfile("guru.txt"):
		f = open("guru.txt", "r")
		old = f.read()
		f.close()
		j = -1
		for i in range(len(liste)):
			if liste[i] == old:
				j = i
		if j == -1:
			j = len(liste)
		for i in range(0,j):
			dictToReturn[liste[i]] = mydict[liste[i]]
		f = open("guru.txt", "w")
		f.write(liste[0])
		f.close()
	else:
		f = open("guru.txt", "w")
		f.write(liste[0])
		f.close()
		dictToReturn[liste[0]] = mydict[liste[0]]
	
	return dictToReturn


async def anssi_alerts():
	toReturn = {}
	infos_liste = {}
	line_in_file = []
	item_to_del = []
	###cle -> item-ref, value -> date, title, status, pdf
	url = "https://www.cert.ssi.gouv.fr"
	page = requests.get(url)
	soup = BeautifulSoup(page.content, "html.parser")
	cert_alert = soup.find_all("div", class_="cert-alert")
	###cert_alert[0] est le titre de la section
	for i in range(1,len(cert_alert)):
		date = cert_alert[i].find("span", class_="item-date")
		link = cert_alert[i].find("span", class_="item-ref")
		title = cert_alert[i].find("span", class_="item-title")
		status = cert_alert[i].find("span", class_="item-status")
		pdf = cert_alert[i].find("a", class_="item-link")
		
		infos_liste[link.text] = []
		infos_liste[link.text].append(date.text)
		infos_liste[link.text].append(title.text)
		infos_liste[link.text].append(status.text)
		if pdf is not None:
			infos_liste[link.text].append(url+pdf['href'])
		else:
			infos_liste[link.text].append("")

	###Si le fichier n'existe pas on ajoute tout au fichier et au channel
	###Sinon
	###Si l'entrée est dans la liste et pas dans le fichier on l'ajoute au fichier
	###et au channel
	###Si l'entrée est dans la liste et dans le fichier, on ne fait rien
	###Si l'entrée est dans le fichier mais pas dans la liste
	###on le retire du fichier
	if not os.path.isfile("cert/alerts.txt"):
		f = open("cert/alerts.txt", "w")
		for key, value in infos_liste.items():
			f.write(key+"\n")
		f.close()
		toReturn = infos_liste
	else:
		with open("cert/alerts.txt") as f:
			for line in f:
				line_in_file.append(line.rstrip("\n"))
		for key, value in infos_liste.items():
			if key not in line_in_file:
				line_in_file.append(key)
				toReturn[key] = infos_liste[key]
		for line in line_in_file:
			if line not in infos_liste.keys():
				item_to_del.append(line)
		for item in item_to_del:
			line_in_file.remove(item)
		f = open("cert/alerts.txt", "w")
		for line in line_in_file:
			f.write(line+"\n")
		f.close()

	return toReturn


async def anssi_threats():
	toReturn = {}
	infos_liste = {}
	line_in_file = []
	item_to_del = []
	###cle -> item-ref, value -> date, title
	url = "https://www.cert.ssi.gouv.fr"
	page = requests.get(url)
	soup = BeautifulSoup(page.content, "html.parser")
	cert_cti = soup.find_all("div", class_="cert-cti")
	###cert_cti[0] est le titre de la section
	for i in range(1,len(cert_cti)):
		date = cert_cti[i].find("span", class_="item-date")
		link = cert_cti[i].find("span", class_="item-ref")
		title = cert_cti[i].find("span", class_="item-title")
		
		infos_liste[link.text] = []
		infos_liste[link.text].append(date.text)
		infos_liste[link.text].append(title.text)


	###Si le fichier n'existe pas on ajoute tout au fichier et au channel
	###Sinon
	###Si l'entrée est dans la liste et pas dans le fichier on l'ajoute au fichier
	###et au channel
	###Si l'entrée est dans la liste et dans le fichier, on ne fait rien
	###Si l'entrée est dans le fichier mais pas dans la liste
	###on le retire du fichier
	if not os.path.isfile("cert/threats.txt"):
		f = open("cert/threats.txt", "w")
		for key, value in infos_liste.items():
			f.write(key+"\n")
		f.close()
		toReturn = infos_liste
	else:
		with open("cert/threats.txt") as f:
			for line in f:
				line_in_file.append(line.rstrip("\n"))
		for key, value in infos_liste.items():
			if key not in line_in_file:
				line_in_file.append(key)
				toReturn[key] = infos_liste[key]
		for line in line_in_file:
			if line not in infos_liste.keys():
				item_to_del.append(line)
		for item in item_to_del:
			line_in_file.remove(item)
		f = open("cert/threats.txt", "w")
		for line in line_in_file:
			f.write(line+"\n")
		f.close()

	return toReturn


async def anssi_opinions():
	toReturn = {}
	infos_liste = {}
	line_in_file = []
	item_to_del = []
	###cle -> item-ref, value -> date, title, pdf
	url = "https://www.cert.ssi.gouv.fr"
	page = requests.get(url)
	soup = BeautifulSoup(page.content, "html.parser")
	cert_avis = soup.find_all("div", class_="cert-avis")
	###cert_avis[0] est le titre de la section
	for i in range(1,len(cert_avis)):
		date = cert_avis[i].find("span", class_="item-date")
		link = cert_avis[i].find("span", class_="item-ref")
		title = cert_avis[i].find("span", class_="item-title")
		pdf = cert_avis[i].find("a", class_="item-link")
		
		infos_liste[link.text] = []
		infos_liste[link.text].append(date.text)
		infos_liste[link.text].append(title.text)
		if pdf is not None:
			infos_liste[link.text].append(url+pdf['href'])
		else:
			infos_liste[link.text].append("")


	###Si le fichier n'existe pas on ajoute tout au fichier et au channel
	###Sinon
	###Si l'entrée est dans la liste et pas dans le fichier on l'ajoute au fichier
	###et au channel
	###Si l'entrée est dans la liste et dans le fichier, on ne fait rien
	###Si l'entrée est dans le fichier mais pas dans la liste
	###on le retire du fichier
	if not os.path.isfile("cert/opinions.txt"):
		f = open("cert/opinions.txt", "w")
		for key, value in infos_liste.items():
			f.write(key+"\n")
		f.close()
		toReturn = infos_liste
	else:
		with open("cert/opinions.txt") as f:
			for line in f:
				line_in_file.append(line.rstrip("\n"))
		for key, value in infos_liste.items():
			if key not in line_in_file:
				line_in_file.append(key)
				toReturn[key] = infos_liste[key]
		for line in line_in_file:
			if line not in infos_liste.keys():
				item_to_del.append(line)
		for item in item_to_del:
			line_in_file.remove(item)
		f = open("cert/opinions.txt", "w")
		for line in line_in_file:
			f.write(line+"\n")
		f.close()

	return toReturn


async def anssi_ioc():
	toReturn = {}
	infos_liste = {}
	line_in_file = []
	item_to_del = []
	###cle -> item-ref, value -> date, title, pdf
	url = "https://www.cert.ssi.gouv.fr"
	page = requests.get(url)
	soup = BeautifulSoup(page.content, "html.parser")
	cert_ioc = soup.find_all("div", class_="cert-ioc")
	###cert_ioc[0] est le titre de la section
	for i in range(1,len(cert_ioc)):
		date = cert_ioc[i].find("span", class_="item-date")
		link = cert_ioc[i].find("span", class_="item-ref")
		title = cert_ioc[i].find("span", class_="item-title")
		pdf = cert_ioc[i].find("a", class_="item-link")
		
		infos_liste[link.text] = []
		infos_liste[link.text].append(date.text)
		infos_liste[link.text].append(title.text)
		if pdf is not None:
			infos_liste[link.text].append(url+pdf['href'])
		else:
			infos_liste[link.text].append("")


	###Si le fichier n'existe pas on ajoute tout au fichier et au channel
	###Sinon
	###Si l'entrée est dans la liste et pas dans le fichier on l'ajoute au fichier
	###et au channel
	###Si l'entrée est dans la liste et dans le fichier, on ne fait rien
	###Si l'entrée est dans le fichier mais pas dans la liste
	###on le retire du fichier
	if not os.path.isfile("cert/ioc.txt"):
		f = open("cert/ioc.txt", "w")
		for key, value in infos_liste.items():
			f.write(key+"\n")
		f.close()
		toReturn = infos_liste
	else:
		with open("cert/ioc.txt") as f:
			for line in f:
				line_in_file.append(line.rstrip("\n"))
		for key, value in infos_liste.items():
			if key not in line_in_file:
				line_in_file.append(key)
				toReturn[key] = infos_liste[key]
		for line in line_in_file:
			if line not in infos_liste.keys():
				item_to_del.append(line)
		for item in item_to_del:
			line_in_file.remove(item)
		f = open("cert/ioc.txt", "w")
		for line in line_in_file:
			f.write(line+"\n")
		f.close()

	return toReturn


async def anssi_hardening():
	toReturn = {}
	infos_liste = {}
	line_in_file = []
	item_to_del = []
	###cle -> item-ref, value -> date, title, pdf
	url = "https://www.cert.ssi.gouv.fr"
	page = requests.get(url)
	soup = BeautifulSoup(page.content, "html.parser")
	cert_dur = soup.find_all("div", class_="cert-dur")
	###cert_dur[0] est le titre de la section
	for i in range(1,len(cert_dur)):
		date = cert_dur[i].find("span", class_="item-date")
		link = cert_dur[i].find("span", class_="item-ref")
		title = cert_dur[i].find("span", class_="item-title")
		pdf = cert_dur[i].find("a", class_="item-link")
		
		infos_liste[link.text] = []
		infos_liste[link.text].append(date.text)
		infos_liste[link.text].append(title.text)
		if pdf is not None:
			infos_liste[link.text].append(url+pdf['href'])
		else:
			infos_liste[link.text].append("")


	###Si le fichier n'existe pas on ajoute tout au fichier et au channel
	###Sinon
	###Si l'entrée est dans la liste et pas dans le fichier on l'ajoute au fichier
	###et au channel
	###Si l'entrée est dans la liste et dans le fichier, on ne fait rien
	###Si l'entrée est dans le fichier mais pas dans la liste
	###on le retire du fichier
	if not os.path.isfile("cert/dur.txt"):
		f = open("cert/dur.txt", "w")
		for key, value in infos_liste.items():
			f.write(key+"\n")
		f.close()
		toReturn = infos_liste
	else:
		with open("cert/dur.txt") as f:
			for line in f:
				line_in_file.append(line.rstrip("\n"))
		for key, value in infos_liste.items():
			if key not in line_in_file:
				line_in_file.append(key)
				toReturn[key] = infos_liste[key]
		for line in line_in_file:
			if line not in infos_liste.keys():
				item_to_del.append(line)
		for item in item_to_del:
			line_in_file.remove(item)
		f = open("cert/dur.txt", "w")
		for line in line_in_file:
			f.write(line+"\n")
		f.close()

	return toReturn


async def anssi_news():
	toReturn = {}
	infos_liste = {}
	line_in_file = []
	item_to_del = []
	###cle -> item-ref, value -> date, title, pdf, excerpt
	url = "https://www.cert.ssi.gouv.fr"
	page = requests.get(url)
	soup = BeautifulSoup(page.content, "html.parser")
	cert_news = soup.find_all("article", class_="cert-news")
	
	date = cert_news[0].find("span", class_="item-date")
	link = cert_news[0].find("span", class_="item-ref")
	title = cert_news[0].find("div", class_="item-title")
	pdf = cert_news[0].find("a", class_="item-link")
	excerpt = cert_news[0].find("section", class_="item-excerpt")
		
	infos_liste[link.text] = []
	infos_liste[link.text].append(date.text)
	infos_liste[link.text].append(title.text)
	infos_liste[link.text].append(url+pdf['href'])
	infos_liste[link.text].append(excerpt.text)

	###Si le fichier n'existe pas on ajoute tout au fichier et au channel
	###Sinon
	###Si l'entrée est dans la liste et pas dans le fichier on l'ajoute au fichier
	###et au channel
	###Si l'entrée est dans la liste et dans le fichier, on ne fait rien
	###Si l'entrée est dans le fichier mais pas dans la liste
	###on le retire du fichier
	if not os.path.isfile("cert/news.txt"):
		f = open("cert/news.txt", "w")
		for key, value in infos_liste.items():
			f.write(key+"\n")
		f.close()
		toReturn = infos_liste
	else:
		with open("cert/news.txt") as f:
			for line in f:
				line_in_file.append(line.rstrip("\n"))
		for key, value in infos_liste.items():
			if key not in line_in_file:
				line_in_file.append(key)
				toReturn[key] = infos_liste[key]
		for line in line_in_file:
			if line not in infos_liste.keys():
				item_to_del.append(line)
		for item in item_to_del:
			line_in_file.remove(item)
		f = open("cert/news.txt", "w")
		for line in line_in_file:
			f.write(line+"\n")
		f.close()

	return toReturn


class Client(discord.Client):
	async def on_ready(self):
		await self.wait_until_ready()
		###DarknetDiaries
		channel = self.get_channel(914100076358533130)
		darknet = await darknetdiaries()
		if darknet != "":
			await channel.send(darknet)
		###Zataz
		channel = self.get_channel(914100172206784552)
		zataz_news = await zataz()
		if zataz_news:
			for key, value in zataz_news.items():
				await channel.send(value + "\n" + key)
		###IT Guru
		channel = self.get_channel(915938351218049035)
		guru = await it_guru_news()
		if guru:
			for key, value in guru.items():
				await channel.send(value[0] + " - " + value[1] + "\n" + key)
		###Anssi alerts
		channel = self.get_channel(914100339823755265)
		anssi = await anssi_alerts()
		if anssi:
			for key, value in anssi.items():
				link = url_anssi_alert + key
				await channel.send(key + ": " + value[0] + " - " + value[1] + " - " + value[2] + "\n" + link + "\n" + value[3])
		###Anssi threats
		channel = self.get_channel(915241453800792094)
		anssi = await anssi_threats()
		if anssi:
			for key, value in anssi.items():
				link = url_anssi_threats + key
				pdf_link = url_anssi_threats_pdf + key + ".pdf"
				await channel.send(key + ": " + value[0] + " - " + value[1] + "\n" + link + "\n" + pdf_link)
		###Anssi opinions
		channel = self.get_channel(915241622793502771)
		anssi = await anssi_opinions()
		if anssi:
			for key, value in anssi.items():
				link = url_anssi_opinions + key
				await channel.send(key + ": " + value[0] + " - " + value[1] + "\n" + link + "\n" + value[2])
		###Anssi IOC
		channel = self.get_channel(915241769866756107)
		anssi = await anssi_ioc()
		if anssi:
			for key, value in anssi.items():
				link = url_anssi_ioc + key
				await channel.send(key + ": " + value[0] + " - " + value[1] + "\n" + link + "\n" + value[2])
		###Anssi hardening
		channel = self.get_channel(915241911441293342)
		anssi = await anssi_hardening()
		if anssi:
			for key, value in anssi.items():
				link = url_anssi_dur + key
				await channel.send(key + ": " + value[0] + " - " + value[1] + "\n" + link + "\n" + value[2])
		###Anssi News
		channel = self.get_channel(915256286747197500)
		anssi = await anssi_news()
		if anssi:
			for key, value in anssi.items():
				link = url_anssi_actu + key
				await channel.send(key + ": " + value[0] + " - " + value[1] + "\n" + value[3] + "\n" + link + "\n" + value[2])
		await self.close()

client = Client()
client.run(os.getenv('TOKENV'))
