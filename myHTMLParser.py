from HTMLParser import HTMLParser

import re

class ibdParser(HTMLParser): #{

  _DEBUG_ = False

  # state
  STATE_IDLE              = 0
  STATE_SEARCH_CURR_STOCK = 1
  STATE_SEARCH_LEAD_STOCK = 2

  currState = 0
  stockName = ''
  tagSequence = []
  attrSequence = []
  getData = False

  # final variables
  currStockRank = 0
  leadingStock  = ''

  def __init__(self):
    HTMLParser.__init__(self)
    self.reinit()

  def reinit(self):
    self.currState = self.STATE_IDLE
    self.getData = False
    self.currStockRank = 0
    self.leadingStock = ''

  """
  overridden methods
  """
  # Try to find curr stock ranking or leading stock name
  # based on the current state
  def handle_starttag(self, tag, attrs):
    # turn getData off
    self.getData = False
    if self.currState == self.STATE_SEARCH_CURR_STOCK:
      self.search_curr_stock(tag, attrs)
    elif self.currState == self.STATE_SEARCH_LEAD_STOCK:
      self.search_lead_stock(tag, attrs)

  # If the current state is STATE_SEARCH_CURR_STOCK, get the ranking
  # If the ranking is not 1, switch state to STATE_SEARCH_LEAD_STOCK
  # No-data will have "data" be '\n'
  def handle_data(self, data):
    if (self.getData == False) or (data == '\n'):
      return
    
    if self.currState == self.STATE_SEARCH_CURR_STOCK:
      self.currStockRank = data
      if data != 1:
        self.currState = self.STATE_SEARCH_LEAD_STOCK
      else:
        self.currState = self.STATE_IDLE

    elif self.currState == self.STATE_SEARCH_LEAD_STOCK:
      self.leadingStock = data
      self.currState = self.STATE_IDLE

  def handle_endtag(self, tag):
    self.getData = False
  
  """
  custom methods
  """
  def search_curr_stock(self, tag, attrs):
    tagSequence = self.tagSequence
    attrSequence = self.attrSequence
    # if there's nothing left, just return
    if (len(tagSequence) == 0) and (len(attrSequence) == 0):
      return
    # if only one of them is not empty, raise an error
    # "error" function is inherited from HTMLParser
    if len(tagSequence) + len(attrSequence) < 2:
      self.error('InvalidConfig :: non-matching length of tagSequence and attrSequence')

    # "attr" is key-value pair, and the value will be searched via regex
    if (tag == tagSequence[0]):
      for attr in attrs:
        regex = attrSequence[0][1]
        if (attr[0] == attrSequence[0][0]) and re.match(regex, attr[1]):
          if self._DEBUG_:
            print "found matching tag: " + tag + ";   attr: " + str(attrSequence[0])
          del tagSequence[0]
          del attrSequence[0]
          self.getData = True
          break

  def search_lead_stock(self, tag, attrs):
    self.search_curr_stock(tag, attrs)

  def find_rank(self, stockName, txt):
    self.stockName = stockName
    self.tagSequence =  [ 'div',             'span',                    'a' ]
    self.attrSequence = [('id', 'grpLdrs'), ('id', '.+ltlSymbolRank'), ('class', 'stockRoll')]
    self.currState = self.STATE_SEARCH_CURR_STOCK
    self.feed(txt)
    
    if self._DEBUG_:
      print stockName + " ranking is " + str(self.currStockRank)
      if self.currStockRank != '1':
        print "Leading stock is " + self.leadingStock
#}


class bingParser(HTMLParser): #{

  _DEBUG_ = False

  tagSequence = []
  attrSequence = []
  ibdLink = ''

  def __init__(self):
    HTMLParser.__init__(self)
    self.reinit()

  def reinit(self):
    self.ibdLink = ''

  def handle_starttag(self, tag, attrs):
    tagSequence = self.tagSequence
    attrSequence = self.attrSequence
    # if there's nothing left, just return
    if (len(tagSequence) == 0) and (len(attrSequence) == 0):
      return
    # if only one of them is not empty, raise an error
    # "error" function is inherited from HTMLParser
    if len(tagSequence) + len(attrSequence) < 2:
      self.error('InvalidConfig :: non-matching length of tagSequence and attrSequence')

    # "attr" is key-value pair, and the value will be searched via regex
    if (tag == tagSequence[0]):
      for attr in attrs:
        regex = attrSequence[0][1]
        if (attr[0] == attrSequence[0][0]) and re.match(regex, attr[1]):
          if self._DEBUG_:
            print "found matching tag: " + tag + ";   attr: " + str(attrSequence[0])
          del tagSequence[0]
          del attrSequence[0]
          self.ibdLink = attr[1]
          break

  def find_link(self, stockName, txt):
    self.stockName = stockName
    self.tagSequence =  [ 'a']
    self.attrSequence = [('href', '.+research\.investors\.com\/stock-quotes.+' + stockName)]
    self.feed(txt)
#}
