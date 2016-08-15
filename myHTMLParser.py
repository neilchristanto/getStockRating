from HTMLParser import HTMLParser

import re

class ibdParser(HTMLParser): #{

  _DEBUG_ = False

  # state -- the order needs to be in conformant with the ibdResp data list
  STATE_IDLE                  = 0
  STATE_SEARCH_CURR_STOCK     = 1
  STATE_SEARCH_LEAD_STOCK     = 2
  STATE_SEARCH_NEXT_ER        = 3
  STATE_SEARCH_INDUSTRY_GROUP = 4
  STATE_SEARCH_INDUSTRY_RANK  = 5
  STATE_STOP                  = 6

  currState = 0
  stockName = ''
  tagSequence = []
  attrSequence = []
  getData = False
  getNextData = False

  # final variables
  currStockRank = '0'
  leadingStock  = ''
  # final variables -- from table
  industryGroup = []
  industryRank  = []
  nextErDate    = []

  def __init__(self):
    HTMLParser.__init__(self)
    self.reinit()

  def reinit(self):
    self.currState = self.STATE_IDLE
    self.getData = False
    self.currStockRank = 0
    self.leadingStock = ''
    self.industryGroup = []
    self.industryRank  = []
    self.nextErDate    = []

  def is_active(self):
    return (self.currState > self.STATE_IDLE) and (self.currState < self.STATE_STOP)

  """
  overridden methods
  """
  # Try to find curr stock ranking or leading stock name
  # based on the current state
  def handle_starttag(self, tag, attrs):
    # turn getData off
    self.getData = False
    if self.is_active() == False:
      return
    
    elif self.currState == self.STATE_SEARCH_CURR_STOCK:
      self.search_curr_stock(tag, attrs)
    
    elif self.currState == self.STATE_SEARCH_LEAD_STOCK:
      self.search_lead_stock(tag, attrs)
    
    elif self.currState == self.STATE_SEARCH_INDUSTRY_GROUP:
      if tag == 'li':
        self.getData = True

    elif self.currState == self.STATE_SEARCH_INDUSTRY_RANK:
      if tag == 'li':
        self.getData = True

    elif self.currState == self.STATE_SEARCH_NEXT_ER:
      if tag == 'li':
        self.getData = True

  # No-data will have "data" be '\n'
  # Immediately return if getData is False or data is empty (\n)
  def handle_data(self, data):
    if (self.getData == False) or (data == '\n'):
      return
 
    if self.currState == self.STATE_SEARCH_CURR_STOCK:
      self.currStockRank = str(data)
      if data != '1':
        self.currState += 1 # next state
      else:
        self.currState += 2 # jump 2 states

    elif self.currState == self.STATE_SEARCH_LEAD_STOCK:
      self.leadingStock = str(data)
      self.currState += 1

    elif self.currState == self.STATE_SEARCH_NEXT_ER:
      self.get_table_data(self.nextErDate, '.*EPS Due Date.*', data)

    elif self.currState == self.STATE_SEARCH_INDUSTRY_GROUP:
      self.get_table_data(self.industryGroup, '.*Industry Group.*', data)

    elif self.currState == self.STATE_SEARCH_INDUSTRY_RANK:
      self.get_table_data(self.industryRank, '.*Industry Group Rank.*', data)

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
            print self.__class__.__name__ + " found matching tag: " + tag + ";   attr: " + str(attrSequence[0])
          del tagSequence[0]
          del attrSequence[0]
          self.getData = True
          break

  # Currently similar to search_curr_stock as it utilizes same data structure
  def search_lead_stock(self, tag, attrs):
    self.search_curr_stock(tag, attrs)


  # Get data from HTML table/list format
  # in1: class variable to be updated
  # in2: regular expression for matching
  # in3: data from the HTML
  def get_table_data(self, var, regex, data):
    if self.getNextData:
      var.append(str(data))
      self.getNextData = False
      self.currState += 1
    if re.match(regex, data):
      self.getNextData = True


  # Entry point of the IBD stock result webpage parsing
  # in1: name of the stock
  # in2: HTML of the webpage
  def find_rank(self, stockName, txt):
    if self._DEBUG_:
      fn = open('ibdLink_ctn.html', 'w')
      fn.write(txt)
      fn.close()
    
    self.stockName = stockName
    self.tagSequence =  [ 'span',                    'a' ]
    self.attrSequence = [('id', '.+ltlSymbolRank'), ('class', 'stockRoll')]
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
            print self.__class__.__name__ + " found matching tag: " + tag + ";   attr: " + str(attrSequence[0])
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
