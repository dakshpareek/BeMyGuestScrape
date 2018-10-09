import os
import re
import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import json,time,random,string
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pathlib import Path
from slugify import slugify
import geocoder
from datapackage import Package

def login():
	link="https://agents.bemyguest.com.sg/en"
	driver.get(link)
	time.sleep(2)
	email="kim@tripzeeker.com"
	password="TripZ88ker#1"
	driver.find_element_by_name('email').send_keys(email)
	driver.find_element_by_name('password').send_keys(password)
	time.sleep(1)
	driver.find_element_by_xpath('//*[@id="homeWrap"]/div[2]/div/div/div[2]/div/form/div[4]/div/button').click()
	time.sleep(2)
	driver.get('https://agents.bemyguest.com.sg/en/tours?query=a')
	time.sleep(1)
	driver.find_element_by_xpath('//*[@id="sidebar-wrapper"]/ul[2]/li[3]/ul/li[1]/div/select').click()
	time.sleep(0.5)
	driver.find_element_by_xpath('//*[@id="sidebar-wrapper"]/ul[2]/li[3]/ul/li[1]/div/select/option[19]').click()
	
def search():
	#time.sleep(2)
	srch=driver.find_element_by_xpath('//*[@id="bmg-app"]/div[3]/div/div[1]/div[1]/div/div/div/input')
	srch.clear()
	srch.send_keys(destination)
	time.sleep(5)
	driver.find_elements_by_class_name('name')[0].click()
	time.sleep(1)

def save():
	if not os.path.exists("BeMyGuest/"+destination):
		os.makedirs("BeMyGuest/"+destination)
	with open("BeMyGuest/"+destination+"/"+destination+'.json', 'w') as outfile:
		json.dump(arr, outfile,  indent=4)

def make_json(title,images,duration,gsize,highlights,final_additional,final_description,price):
	try:
		slug=slugify(title)
		idd=''.join(random.choices(string.ascii_letters + string.digits, k=13))
		k={"_index": "tripzeeker","_type": "tour","_id":idd,"_score": 1,"_source":None}
		k["_source"]={"slug":slug,"title":title,"country":{"code":c_code,"name":destination},"description":final_description.replace('\n', ''),"group_size":gsize.replace('\n', ''),"highlights":highlights.replace('\n', ''),"additional_info":final_additional.replace('\n', ''),"price":{"currency":"USD","amount":price},"images":images}
		arr.append(k)
	except Exception as e:
		print(e)



def pagination():
	for i in range(1,16):
		st='//*[@id="bmg-app"]/div[3]/div/div[2]/div[2]/div/div[{}]/div/div/div[2]/div[1]/div[2]/p[1]/span'.format(i)
		try:
			price=driver.find_element_by_xpath(st).text
			ele='//*[@id="bmg-app"]/div[3]/div/div[2]/div[2]/div/div[{}]/div/div/div[2]/div[2]/div/div[2]/a'.format(i)
			driver.find_element_by_xpath(ele).click()
			get_data(price)
			driver.execute_script("window.history.go(-1)")
			time.sleep(2)
		except Exception as e:
			driver.execute_script("window.history.go(-1)")
			break
			
def page():
	pagination()
	last=None
	chk=True
	while chk==True:
		time.sleep(1)
		html=driver.page_source
		soup = BeautifulSoup(html,"lxml")
		try:
			nxt=soup.find('a',{'rel':'next'}).attrs['href']
			if nxt != last:
				print(".....Next Page.....")
				last=nxt
				driver.get(nxt)
				time.sleep(1.5)
				pagination()
			else:
				chk=False
		except:
			chk=False


def get_data(price):
	#driver.get(link)
	html=driver.page_source
	soup = BeautifulSoup(html,"lxml")
	try:
		title=soup.find('h4',{'itemprop':'name'}).text.strip().replace('\n', '')
	except:
		title=""
	images_data=soup.findAll('a',{'class':'fancybox-thumb'})
	try:
		images=[i.attrs['href'] for i in images_data]
	except:
		images=[]
	sub_soup1=soup.find('div',{'class':'boxFlex scheduleWrap'})
	#getting time suration of trip
	try:
		lis=sub_soup1.findAll('li')
		duration=lis[0].text.strip()
	except:
		duration=""
	#print(title)
	#group size
	try:
		gsize=lis[-1].text.strip()
	except:
		gsize=""
	#print(gsize)
	#getting highlights
	high=soup.find('div',{'class':'fullWidth ipadHide'})
	highlights=""
	try:
		lis=high.findAll('li')
		for i in lis:
			highlights += i.text.strip()
	except:
		pass
	#getting additional info
	price_include=soup.find('div',{'class':'col-xs-6 noPaddingLeft price_inclusions'})
	p_in="Price Includes:"
	try:
		price_include_list=price_include.findAll('li')
		for i in price_include_list:
			p_in+= ","+ i.text.strip()
	except:
		p_in=""
	price_exclude=soup.find('div',{'class':'col-xs-6 noPaddingLeft price_exclusions'})
	p_ex="Price Excludes:"
	try:
		price_exclude_list=price_exclude.findAll('li')
		for i in price_exclude_list:
			p_ex+=','+ i.text.strip()
	except:
		p_ex=""
	#getting more additional info
	try:
		additional=soup.find('div',{'id':'additionalInfoWrap'}).text.strip()
	except:
		additional=""
	#getting description
	final_additional=p_in+p_ex+additional
	try:
		description=soup.find('div',{'id':'descriptionWrap'})
		try:
			desc1=description.find('div').text.strip()
		except:
			desc1=""
		try:
			desc2=description.find('p').text.strip()
		except:
			desc2=""
		final_description=desc1+desc2
	except Exception as e:
		print(e)
	#print(price)
	#print(duration,gsize)
	make_json(title,images,duration,gsize,highlights,final_additional,final_description,price)


if not os.path.exists("BeMyGuest"):
	os.makedirs("BeMyGuest")	
	
path="c:\chromedriver.exe"
driver = webdriver.Chrome(path)
driver.set_window_size(1024, 600)
driver.maximize_window()
login()


#searching country deatails and getting data
package = Package('https://datahub.io/core/country-list/datapackage.json')
for resource in package.resources:
	if resource.descriptor['datahub']['type'] == 'derived/csv':
		c_list=resource.read()

arr=[]		
		
for inn,j in enumerate(c_list):
	if(inn < 9):
		continue
	destination=j[0]
	c_code=j[1]
	print(inn)
	arr=[]
	search()
	page()
	if len(arr)!=0:
		save()
	#break
#destination='dubai'
#c_code=""

