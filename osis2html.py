#!/usr/bin/env python3

from enum import Enum
import jinja2
import os, os.path
import sys
import xml.dom.minidom

Testament = Enum('Testament', 'OT NT')

class Book :
  def __init__(self, shortname, longname, testament) :
    self.shortname = shortname
    self.longname = longname
    self.filename = longname.lower().replace(' ', '-') + '.html'
    self.testament = testament
    self.node = None

Books = [Book('Gen', 'Genesis', Testament.OT),
         Book('Exod', 'Exodus', Testament.OT),
         Book('Lev', 'Leviticus', Testament.OT),
         Book('Num', 'Numbers', Testament.OT),
         Book('Deut', 'Deuteronomy', Testament.OT),
         Book('Josh', 'Joshua', Testament.OT),
         Book('Judg', 'Judges', Testament.OT),
         Book('Ruth', 'Ruth', Testament.OT),
         Book('1Sam', '1 Samuel', Testament.OT),
         Book('2Sam', '2 Samuel', Testament.OT),
         Book('1Kgs', '1 Kings', Testament.OT),
         Book('2Kgs', '2 Kings', Testament.OT),
         Book('1Chr', '1 Chronicles', Testament.OT),
         Book('2Chr', '2 Chronicles', Testament.OT),
         Book('Ezra', 'Ezra', Testament.OT),
         Book('Neh', 'Nehemiah', Testament.OT),
         Book('Esth', 'Esther', Testament.OT),
         Book('Job', 'Job', Testament.OT),
         Book('Ps', 'Psalms', Testament.OT),
         Book('Prov', 'Proverbs', Testament.OT),
         Book('Eccl', 'Ecclesiastes', Testament.OT),
         Book('Song', 'Song of Songs', Testament.OT),
         Book('Isa', 'Isaiah', Testament.OT),
         Book('Jer', 'Jeremiah', Testament.OT),
         Book('Lam', 'Lamentations', Testament.OT),
         Book('Ezek', 'Ezekiel', Testament.OT),
         Book('Dan', 'Daniel', Testament.OT),
         Book('Hos', 'Hosea', Testament.OT),
         Book('Joel', 'Joel', Testament.OT),
         Book('Amos', 'Amos', Testament.OT),
         Book('Obad', 'Obadiah', Testament.OT),
         Book('Jonah', 'Jonah', Testament.OT),
         Book('Mic', 'Micah', Testament.OT),
         Book('Nah', 'Nahum', Testament.OT),
         Book('Hab', 'Habakkuk', Testament.OT),
         Book('Zeph', 'Zephaniah', Testament.OT),
         Book('Hag', 'Haggai', Testament.OT),
         Book('Zech', 'Zechariah', Testament.OT),
         Book('Mal', 'Malachi', Testament.OT),
         Book('Matt', 'Matthew', Testament.NT),
         Book('Mark', 'Mark', Testament.NT),
         Book('Luke', 'Luke', Testament.NT),
         Book('John', 'John', Testament.NT),
         Book('Acts', 'Acts', Testament.NT),
         Book('Rom', 'Romans', Testament.NT),
         Book('1Cor', '1 Corinthians', Testament.NT),
         Book('2Cor', '2 Corinthians', Testament.NT),
         Book('Gal', 'Galatians', Testament.NT),
         Book('Eph', 'Ephesians', Testament.NT),
         Book('Phil', 'Philippians', Testament.NT),
         Book('Col', 'Colossians', Testament.NT),
         Book('1Thess', '1 Thessalonians', Testament.NT),
         Book('2Thess', '2 Thessalonians', Testament.NT),
         Book('1Tim', '1 Timothy', Testament.NT),
         Book('2Tim', '2 Timothy', Testament.NT),
         Book('Titus', 'Titus', Testament.NT),
         Book('Phlm', 'Philemon', Testament.NT),
         Book('Heb', 'Hebrews', Testament.NT),
         Book('Jas', 'James', Testament.NT),
         Book('1Pet', '1 Peter', Testament.NT),
         Book('2Pet', '2 Peter', Testament.NT),
         Book('1John', '1 John', Testament.NT),
         Book('2John', '2 John', Testament.NT),
         Book('3John', '3 John', Testament.NT),
         Book('Jude', 'Jude', Testament.NT),
         Book('Rev', 'Revelation', Testament.NT) ]

Footnote = 0
CarriedVerse = None
InParagraph = False
LastNode = None
QuoteLevel = 0
def doc2html(node) :
  return xml2html(node) + endParaIfNeeded()
def xml2html(node, inTitle = False) :
  global Footnote, CarriedVerse, LastNode

  if CarriedVerse :
    carried_verse = CarriedVerse
    CarriedVerse = None
  else :
    carried_verse = ''

  last_node = LastNode
  LastNode = node.nodeName

  if node.nodeType == node.TEXT_NODE :
    return (beginParaIfNeeded() if not inTitle and (carried_verse or not node.nodeValue.isspace()) else '') + carried_verse + node.nodeValue
  elif node.nodeName == 'title' :
    title_type = node.getAttribute('type')
    if title_type == 'main'      : heading = 1
    elif title_type == 'chapter' : heading = 2
    elif title_type == 'psalm'   : heading = 3
    else                         : heading = 4
    return (endParaIfNeeded() if not inTitle else '') + ('<h%d>' % heading) + ''.join(xml2html(x, True) for x in node.childNodes) + ('</h%d>' % heading) + (beginPara() if not inTitle and carried_verse else '') + carried_verse
  elif node.nodeName == 'verse' :
    # Only emit at the start of a verse.
    # But even then, don't emit the verse number immediately.
    # Sometimes there is a following title or milestone element we want to emit first.
    if node.hasAttribute('sID') :
      CarriedVerse = '<sup>' + node.getAttribute('sID').split('.')[-1] + '</sup>'
    return ''
  elif node.nodeName == 'milestone' :
    if node.getAttribute('type') in ('x-p', 'x-extra-p') : return (endParaIfNeeded() + (beginPara() if carried_verse else '') if not inTitle else '') + carried_verse
    else                                                 : return (beginParaIfNeeded() if not inTitle and carried_verse else '') + carried_verse
  elif node.nodeName == 'transChange' :
    return (beginParaIfNeeded() if not inTitle else '') + carried_verse + '<em>' + ''.join(xml2html(x, inTitle) for x in node.childNodes) + '</em>'
  elif node.nodeName == 'divineName' :
    return (beginParaIfNeeded() if not inTitle else '') + '<span class="divineName">' + ''.join(xml2html(x, inTitle) for x in node.childNodes) + '</span>'
  elif node.nodeName == 'q' :
    quote_type = node.getAttribute('type')
    return (beginParaIfNeeded() if not inTitle else '') + beginQuote(quote_type) + ''.join(xml2html(x, inTitle) for x in node.childNodes) + endQuote(quote_type)
  elif node.nodeName == 'note' :
    sup = chr(ord('a') + Footnote)
    Footnote += 1
    if Footnote == 26 :
      Footnote = 0
    return (beginParaIfNeeded() if not inTitle else '') + (' ' if last_node == 'note' else '') + '<sup title="' + ''.join(xml2text(x) for x in node.childNodes) + '">' + sup + '</sup>'
  else :
    return (beginParaIfNeeded() if not inTitle and carried_verse else '') + carried_verse + ''.join(xml2html(x, inTitle) for x in node.childNodes)
def xml2text(node) :
  if node.nodeType == node.TEXT_NODE :
    return node.nodeValue
  else :
    return ''.join(xml2text(x) for x in node.childNodes)
def beginPara() :
  global InParagraph
  InParagraph = True
  return '<p>'
def beginParaIfNeeded() :
  global InParagraph
  if not InParagraph :
    InParagraph = True
    return '<p>'
  else :
    return ''
def endParaIfNeeded() :
  global InParagraph
  if InParagraph :
    InParagraph = False
    return '</p>'
  else :
    return ''
def beginQuote(qtype) :
  global QuoteLevel
  QuoteLevel += 1
  return '<blockquote>' if qtype == 'block' else ('&ldquo;' if QuoteLevel % 2 == 1 else '&lsquo;')
def endQuote(qtype) :
  global QuoteLevel
  QuoteLevel -= 1
  return '</blockquote>' if qtype == 'block' else ('&rdquo;' if QuoteLevel % 2 == 0 else '&rsquo;')

if len(sys.argv) != 3 :
  print("Usage: osis2html.py bible.xml outfolder")
  sys.exit(0)

try : os.mkdir(sys.argv[2])
except : pass

doc = xml.dom.minidom.parse(sys.argv[1])

jenv = jinja2.Environment(loader = jinja2.PackageLoader('osis2html', 'templates'),
                          autoescape = True)

osis_title = doc.getElementsByTagName('title')[0].firstChild.nodeValue
variables = { 'osis_title' : osis_title,
              'ot'         : [x for x in Books if x.testament == Testament.OT],
              'nt'         : [x for x in Books if x.testament == Testament.NT] }
index = open(os.path.join(sys.argv[2], 'index.html'), mode='w', encoding='utf8')
index.write(jenv.get_template('index.html').render(variables))
index.close()

divNodes = doc.getElementsByTagName('div')
for divNode in divNodes :
  if divNode.getAttribute('type') == 'book' :
    book = [x for x in Books if x.shortname == divNode.getAttribute('osisID')][0]
    book.node = divNode
for book in Books :
  bookFile = open(os.path.join(sys.argv[2], book.filename), mode='w', encoding='utf8')
  book_title = book.node.getElementsByTagName('title')[0].firstChild.nodeValue
  variables = { 'book'       : book,
                'book_title' : book_title,
                'body'       : jinja2.Markup(doc2html(book.node)) }
  bookFile.write(jenv.get_template('book.html').render(variables))
  bookFile.close()

