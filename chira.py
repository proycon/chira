#! /usr/bin/env python
# -*- coding: utf8 -*-

# CHINESE READING ASSISTANT (chira)
#  by Maarten van Gompel
#    proycon@anaproy.nl
#    http://proycon.anaproy.nl
#
# Open-source, licensed under GNU Public License v3


import pynotify
import codecs
import sys
import time
import os

#this function makes the pinyin nicer, it strips the tone numbers and instead inserts proper diacritic marks (unicode). It converts for example "zhong1" into "zhōng". I go by the following rules (source: wikipedia):
# 	 The rules for determining on which vowel the tone mark appears when there are multiple vowels are as follows:
# 		  1. First, look for an "a" or an "e". If either vowel appears, it takes the tone mark. There are no possible pinyin syllables that contain both an "a" and an "e".
#   		  2. If there is no "a" or "e", look for an "ou". If "ou" appears, then the "o" takes the tone mark.
#   		  3. If none of the above cases hold, then the last vowel in the syllable takes the tone mark.
def pinyin_diacritics(pinyin):
    if ' ' in pinyin:
        return " ".join(  [ pinyin_diacritics(x) for x in pinyin.split(' ') if x.strip() ] )
    
    pinyin = pinyin.lower();
    pinyin = pinyin.replace('u:',u"ü")
    
    if pinyin[-1].isdigit():
        tone = int(pinyin[-1])
        pinyin = pinyin[:-1]
        if tone == 5: #toneless tone, no diacritic, nothing to do
            return pinyin
    else:      
        #no tone, nothing to do
        return pinyin


    #set diacritic
    if pinyin.find('a') != -1:
        if tone == 1:
            return pinyin.replace('a',u"ā")
        elif tone == 2:
            return pinyin.replace('a',u"á")
        elif tone == 3:
            return pinyin.replace('a',u"ǎ")
        elif tone == 4:
            return pinyin.replace('a',u"à")
    elif pinyin.find('e') != -1:
        if tone == 1:
            return pinyin.replace('e',u"ē")
        elif tone == 2:
            return pinyin.replace('e',u"é")
        elif tone == 3:
            return pinyin.replace('e',u"ě")
        elif tone == 4:
            return pinyin.replace('e',u"è")
    elif pinyin.find('ou') != -1:
        if tone == 1:
            return pinyin.replace('ou',u"ōu")
        elif tone == 2:
            return pinyin.replace('ou',u"óu")
        elif tone == 3:
            return pinyin.replace('ou',u"ǒu")
        elif tone == 4:
            return pinyin.replace('ou',u"òu")
    else:
        #grab the last vowel and change it
        for i, c in enumerate(reversed(pinyin)):
            pre = pinyin[:-i-1]
            if -i < 0:
                post = pinyin[-i:]
            else:
                post = ""
            if c == 'a':
                if tone == 1: return pre + u"ā" + post
                elif tone == 2: return pre + u"á" + post
                elif tone == 3: return pre + u"ǎ" + post
                elif tone == 4: return pre + u"à" + post
            elif c == 'e':
                if tone == 1: return pre + u"ē" + post
                elif tone == 2: return pre + u"é" + post
                elif tone == 3: return pre + u"ě" + post
                elif tone == 4: return pre + u"è" + post
            elif c == 'u':
                if tone == 1: return pre + u"ū" + post
                elif tone == 2: return pre + u"ú" + post
                elif tone == 3: return pre + u"ǔ" + post
                elif tone == 4: return pre + u"ù" + post
            elif c == 'o':
                if tone == 1: return pre + u"ō" + post
                elif tone == 2: return pre + u"ó" + post
                elif tone == 3: return pre + u"ǒ" + post
                elif tone == 4: return pre + u"ò" + post
            elif c == 'i':
                if tone == 1: return pre + u"ī" + post
                elif tone == 2: return pre + u"í" + post
                elif tone == 3: return pre + u"ǐ" + post
                elif tone == 4: return pre + u"ì" + post
            elif c == 'ü':
                if tone == 1: return pre + u"ǖ" + post
                elif tone == 2: return pre + u"ǘ" + post
                elif tone == 3: return pre + u"ǚ" + post
                elif tone == 4: return pre + u"ǜ" + post
        return pinyin #nothing found

class Cedict(object):
    
    def __init__(self,filename):
        self.dict = {}
        
        f = codecs.open(filename,'r','utf-8')
        for line in f:        
            if line[0] != '#':
                zht,zhs,other = line.split(' ',2)
                assert other[0] == '['
                end = other.find(']')
                pinyin = pinyin_diacritics(other[1:end - 1])
                translations = [ x.strip() for x in other[end+1:].split('/') if x.strip() ]
                self.dict[zhs] = (pinyin, translations) 
                                                            
                if zhs != zht:
                    self.dict[zht] = (pinyin, translations)
                    #add traditional chinese if different from simplified
        f.close()
       
    def __getitem__(self, key):
        return self.dict[key]
    
    def __contains__(self, key):
        return key in self.dict
    

def findwords(s, cedict):
    begin = 0
    while begin < len(s):
        for end in reversed(range(begin,len(s))):
            if s[begin:end+1] in cedict:
                pinyin, translations = cedict[s[begin:end+1]]
                yield (begin,end+1, pinyin, translations)  
                begin = end
                break
        begin += 1
 
                                    

if __name__ == "__main__":
    lastclipboard = None
    
    popup = True
    try:
        if sys.argv[1] == '-i':
            stdinmode = True
        if sys.argv[1] == '-n':
            popup = False
        elif sys.argv[1] == '-h':
            print >>sys.stderr,"chira.py [-i]\n-i\tInteractive mode (reads from stdin)"
    except:
        stdinmode = False
    
    if not stdinmode:
        if not pynotify.init("chira"):
            print "there was a problem initializing the pynotify module"

        
    print >>sys.stderr, "Loading CEDICT dictionary"
    cedict = Cedict('cedict_ts.u8')
        
           
    
    print >>sys.stderr, "Ready for input"
    while True:
        if stdinmode:        
            line = unicode(sys.stdin.readline(),'utf-8')
        else:
            time.sleep(1)
            try:
                line = unicode(os.popen('xsel').read().strip(),'utf-8')
                if line == lastclipboard:
                    continue
                lastclipboard = line
            except UnicodeError:
                continue
            out = "\n".join([ line[begin:end] + "\t" + pinyin + "\t" + " / ".join(translations) for begin,end, pinyin, translations in findwords(line, cedict) ])
            out = out.strip()
            if out: 
                print out.encode('utf-8')
                print "----------------------------------------"
                n = pynotify.Notification("Chira", out)
                n.show()
            


