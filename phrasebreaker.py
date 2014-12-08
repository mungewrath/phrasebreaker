"""
Command-line application that translates some text.

Uses a phrase-breaking notation strategy devised by Fumiaki Funahashi.
Source created by Matthew Unrath (harkathmaker@gmail).
"""

DEVELOPER_KEY = 'AIzaSyBsnrbW4QbsFyLi-IVyKfmP60WCS-juOVU'
CLAUSE_OPEN  = '('
CLAUSE_CLOSE = ')'
FRAGMENT_OPEN = 'FRAG__'
FRAGMENT_CLOSE = '__'
DEFAULT_SRCLANG = 'en'
DEFAULT_DESTLANG = 'ja'

__author__ = 'harkathmaker@gmail.com (Matthew Unrath)'

from apiclient.discovery import build
import sys

def generatePlaceholder(chunk,ph):
	ret = FRAGMENT_OPEN+str(generatePlaceholder.placeholderCount)+FRAGMENT_CLOSE
	ph[ret] = chunk
	generatePlaceholder.placeholderCount += 1
	return ret
	
generatePlaceholder.placeholderCount = 0

def recombineSentences(sentences,ph):
	finalSentences = []
	for s in sentences:
		finalSentences.append(removePlaceholders(s,ph))
		
	return finalSentences

def removePlaceholders(sentence,ph):
	while True:
		try:
			# Refactor
			# TODO: Check that content inside is a number
			begin = sentence.index(FRAGMENT_OPEN)
			end = sentence.index(FRAGMENT_CLOSE,begin+len(FRAGMENT_OPEN)) + len(FRAGMENT_CLOSE)
			fragMarker = sentence[begin:end]
			sentence = sentence.replace(fragMarker,ph[fragMarker])
		except ValueError:
			return sentence

def fragmentSentences(sentences):
	ph = {}
	fragments = []
	for s in sentences:
		frag,_ = fragmentSentence(s,ph)
		fragments.append(frag)
	
	return fragments, ph
	
### Fragment helpers ###
def getMatchingDelimiter(openers,closers,frag,start=0):
	count = 0
	for idx, c in enumerate(frag[start:]):
		if c in openers:
			count += 1
		elif c in closers:
			count -= 1
		if count == 0:
			return idx+start
		
def fragmentSentence(s,ph):
	#Loop until encountering a delimiter
	for idx, c in enumerate(s):
		if c == CLAUSE_OPEN:
			end = getMatchingDelimiter([CLAUSE_OPEN],[CLAUSE_CLOSE],s,idx)
			frag,_ = fragmentSentence(s[idx+1:end],ph)
			return fragmentSentence(s[:idx]+generatePlaceholder(frag,ph)+s[end+1:],ph)
			
	return s,ph

def translate(sentences,srcLang,destLang):
	# Build a service object for interacting with the API. Visit
	# the Google APIs Console <http://code.google.com/apis/console>
	# to get an API key for your own application.
	service = build('translate', 'v2',
				developerKey=DEVELOPER_KEY)
			
	#print "Sentences:"
	#print sentences
	result = service.translations().list(source=srcLang,target=destLang,q=[s.decode('utf-8') for s in sentences]).execute()
	translatedSentences = [r['translatedText'] for r in result['translations']]
	
	return translatedSentences
	
def readInput(fname):
	sentences = []
	f = open(fname,'r')
	for line in f:
		sentences.append(line)
	f.close()
	
	return sentences
	
def outputResults(translations,fname):
	#print translations
	f = open(fname,'w')
	for t in translations:
		f.write((t+'\n').encode('utf-8'))
	f.close()
	
def showUsage():
	print "Usage:"
	print "python {0} infile outfile [inlang=en] [outlang=ja]".format(sys.argv[0])
	print "        infile: Input file"
	print "        outfile: Output file"
	print "        inlang: 2-character source language code; defaults to English (en)"
	print "        outlang: 2-character target language code; defaults to Japanese (ja)"

def main():
	if len(sys.argv) < 3:
		showUsage()
		sys.exit()
		
	if len(sys.argv) > 3:
		srcLang = sys.argv[3]
	else:
		srcLang = DEFAULT_SRCLANG
		
	if len(sys.argv) > 4:
		destLang = sys.argv[4]
	else:
		destLang = DEFAULT_DESTLANG

	sentences = readInput(sys.argv[1])
	sentences,ph = fragmentSentences(sentences)
	
	translatedSentences = translate(sentences,srcLang,destLang)
	if len(ph) > 0:
		keys = ph.keys()
		translatedValues = translate(ph.values(),srcLang,destLang)
		translatedPh = dict(zip(keys,translatedValues))
	else:
		translatedPh = ph
	
	finalTranslations = recombineSentences(translatedSentences, translatedPh)
	outputResults(finalTranslations, sys.argv[2])
	print "Translation process completed."

if __name__ == '__main__':
  main()