import re
import urllib2
import sys

from myHTMLParser import ibdParser, bingParser 

if sys.argv[1] == 'DBG':
  _DEBUG_ = True
  startList = 2
else:
  _DEBUG_ = False
  startList = 1

finalResult = []

#br = mechanize.Browser()
#br.set_handle_robots(False)

stockList = sys.argv[startList:]
print "Searching rankings for stock(s):\n -- " + str(stockList)

u_ibdParser = ibdParser()
u_ibdParser._DEBUG_ = _DEBUG_
u_bingParser = bingParser()
u_bingParser._DEBUG_ = _DEBUG_

for stock in stockList: #{

  """
  # open bing and search for amba ibd
  br.open("http://www.bing.com")
  br.select_form(nr=0)
  br["q"] = stock + ' ibd'
  br.submit()
  
  # get the link that contains amba stock quote result
  ibdLink = ''
  for link in br.links():
    if re.match('.+research\.investors\.com\/stock-quotes.+' + stock, link.absolute_url):
      ibdLink = link.absolute_url
      break
  
  if _DEBUG_:
    print "ibdLink: " + ibdLink
  """
  
  print "...Looking for stock " + stock

  url = 'http://www.bing.com/search?q=' + stock + '+ibd'
  try:
    bingRsp = urllib2.urlopen('http://www.bing.com/search?q=' + stock + '+ibd')
  except:
    print "Error on url: " + url
    quit()

  u_bingParser.__init__()
  u_bingParser.find_link(stock, bingRsp.read())
  ibdLink = u_bingParser.ibdLink
 
  if ibdLink == '':
    print "Empty bing search.. Can't find stock: " + stock
    continue

  # open the IBD web result
  try:
    ibdRsp = urllib2.urlopen(ibdLink)
  except:
    print "Error on url: " + ibdLink
    quit()

  # use html parser
  u_ibdParser.__init__()
  u_ibdParser.find_rank(stock, ibdRsp.read())
  
  # append result to list of tuples
  finalResult.append((stock.upper(), u_ibdParser.currStockRank, u_ibdParser.leadingStock))

#}

# build html table for the stocks ranking
fn = open('result.html', 'w')
fn.write('<!DOCTYPE html>\n')
fn.write('<html>\n')
fn.write('<body>\n')
fn.write('<table border="1">\n')
fn.write('<tr>\n')
fn.write('<th>Stock</th> <th>Rank</th> <th>Leader</th>\n')
fn.write('</tr>\n')
for res in finalResult:
  fn.write('<tr>\n')
  fn.write('<td>'+str(res[0])+'</td>' + '<td>'+str(res[1])+'</td>' + '<td>'+str(res[2])+'</td>\n')
  fn.write('</tr>\n')
fn.write('</table>\n')
fn.write('</body>\n')
fn.write('</html>\n')
fn.close()

