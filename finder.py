#Original Code and Pricing Data from Dane Jensen

#Price Algorithm:
#P = (57.33*Size) + (1201.71*GHz) + (6.8*Ram) + (.43*HDD) - 2656.07

#Example - 15" Apple MacBook Pro Unibody, 2.66GHz Core 2 Duo Processor, 4GB RAM, 500GB HD listed for 1600
# (57.33*15) + (1201.71*2.66) + (6.8*4) + (.43*500) - 2656.07 = 1642.63
#This means if you bought it you could make $42.63 profit. This isn't suitable, we want at least $85 profit per macbook

import urllib2
from BeautifulSoup import BeautifulSoup
import time
import csv
import re

print 'Starting MacFinder'
profwriter = csv.writer(open('profitable.csv', 'w'), delimiter=',')
valwriter = csv.writer(open('complete.csv', 'w'), delimiter=',')
allwriter = csv.writer(open('incomplete.csv', 'w'), delimiter=',')
    
def re2num(rexp,isint,searchspace):
	if isint:
		num=re.search(rexp,searchspace)
		try:
			num=re.search('[0-9]+',num.group(0))
			return int(num.group(0))
		except:
			return ''
	else:
		num=re.search(rexp,searchspace)
		try:
			num=re.search('\d+\.\d+',num.group(0))
			return float(num.group(0))
		except:
			return ''

def getnum(rexp,isint,searchspaces,val,n):
	if val=='':
		if n<2:
			val=re2num(rexp,isint,searchspaces[n])
		else:
			val='NotFound'
		return getnum(rexp,isint,searchspaces,val,n+1)
	else:
		return val

#donec=['atlanta','austin','boston','chicago','dallas','denver','detroit','houston','lasvegas','losangeles','miami','minneapolis','newyork','philadelphia','phoenix','portland','raleigh','sacramento']
cities=['phoenix']
count=0
for c in cities:
    print 'Scanning "' + c + '" Entries, please wait...'
    http='http://%s.craigslist.org/search/sss?query=macbook+pro&minAsk=800&srchType=T&hasPic=1'%c
    request = urllib2.urlopen(http)
    html = request.read()
    soup = BeautifulSoup(html)
    count = 0
    complete = 0
    incomplete = 0
    profitable = 0
    for p in soup.findAll("p"):
        print 'DEBUG:',p.contents[3].attrs[0][1]
        if (p.contents[3].attrs[0][0]=='href'):
            count = count + 1
            linedesc = p.contents[3].contents[0]
            link = p.contents[3].attrs[0][1]
            request = urllib2.urlopen(link)
            html = request.read()
            isoup = BeautifulSoup(html)
            d = isoup.find('div', id="userbody")
            s = d.__str__
            fulldesc = s()
            pricespaces = [str(p.contents[4]),linedesc,fulldesc];
            searchspaces = [linedesc,fulldesc];
            
            price = getnum('\$[0-9]+',True,pricespaces,'',0)      
            size = getnum('\D1[0-9]\.[0-9]\D',True,searchspaces,'',0)
            if (size == 'NotFound'):
                size = getnum('\D1[0-9]\D',True,searchspaces,'',0)
                
            ghz = getnum('\s\d\.\d\d?\s?[Gg][Hh]',False,searchspaces,'',0)
            if (ghz == 'NotFound') and ('i7' in html):
                ghz = '2.53'
            if (ghz == 'NotFound') and ('i5' in html):
                ghz = '2.67'
                
            ram = getnum('\D\d\s?[Gg][Bb]',True,searchspaces,'',0)
            hdd = getnum('\D\d\d\d\s?[Gg][Bb]',True,searchspaces,'',0)
            if (price == 'NotFound') or (size == 'NotFound') or (ghz == 'NotFound') or (ram == 'NotFound') or (hdd == 'NotFound'):
                allwriter.writerow([c,link,linedesc,price,size,ghz,ram,hdd])
                incomplete = incomplete + 1
            else:
                profit = ((57.33*float(size)) + (1201.71*float(ghz)) + (6.8*float(ram)) + (.43*float(hdd)) - 2656.07) - price
                valwriter.writerow([c,link,linedesc,price,size,ghz,ram,hdd,profit])
                complete = complete + 1
                if profit > 85:
                    profwriter.writerow([c,link,linedesc,price,size,ghz,ram,hdd,profit])
                    profitable = profitable + 1
                
    print count,'Macbooks found in scan'
    print complete,'were valid and',incomplete,'were incomplete'
    if profitable > 0:
        print 'Good news! We found',profitable,'MacBooks with a good profit margin!'

print 'Scanning Complete, check the CSV for data'