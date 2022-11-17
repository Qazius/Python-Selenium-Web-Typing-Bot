from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By

import tkinter as tk

import time

import pyautogui

#: TYPE
NEWLINE={"\n"}
SPECIAL_CHARS={'!','@','#','$','%','^','&','*','(',')','_','+','{','}','[',']','/',':',';','"','=','-'}

startDelay=2 #in seconds

# add wait here for keys with unique delay
tabSize=3
typeInterval=0.08 #default 0.08 (about 110wpm)
specialInterval=0.09 #default 0.09
waitTab=0.1 #default 0.1
waitWord=0.08 #changing to word #default 0.08
waitNewline= 0.20 #default 0.2
waitSpecial=0.15 #changing to special #default 0.15
# TODO change typeInterval without restarting

#* write specials
def writeSpecials(specials):
   time.sleep(waitSpecial)
   pyautogui.write(specials, specialInterval)
   specials = ""
   return specials

#* write words
def writeWords(words):
   time.sleep(waitWord)
   pyautogui.write(words, typeInterval)
   words = ""
   return words

def write(text):
   spaces = ""
   specials = ""
   words = ""
   for char in text:
      if char == " ":
         spaces += char
         if len(specials) > 0:
            specials = writeSpecials(specials) #* write specials
      else:
         while len(spaces) >= tabSize:
            if len(words) > 0:
               words = writeWords(words) #* write words
            time.sleep(waitTab)
            pyautogui.press("tab") #* enter tab
            spaces = spaces.replace(" ", '', tabSize)
         if len(spaces) > 0:
            words += spaces
            spaces = ""
         if char in NEWLINE:
            if len(words) > 0:
               words = writeWords(words) #* write words
            if len(specials) > 0:
               specials = writeSpecials(specials) #* write specials
            time.sleep(waitNewline)
            pyautogui.write(char) #* enter newline
         elif char in SPECIAL_CHARS:
            if len(words) > 0:
               words = writeWords(words) #* write words
            specials += char
         else:
            if len(specials) > 0:
               specials = writeSpecials(specials) #* write specials
            words += char

   # write the left over (last)
   if len(spaces) > 0:
      while len(spaces) >= tabSize:
         time.sleep(waitTab)
         pyautogui.press("tab") #* enter tab
         spaces = spaces.replace(" ", '', tabSize)
      if len(spaces) > 0:
         words += spaces
         spaces = ""
   if len(words) > 0: #* write words
      words = writeWords(words)
   elif len(specials) > 0: #* write specials
      specials = writeSpecials(specials)

# to get xpath: inspect, right click element, copy xpath
sites = {
   'typeracer': {
      'name': 'typeracer',
      'url': 'https://play.typeracer.com/',
      'xpath': '//table/tbody/tr[2]/td/table/tbody/tr[1]/td/table/tbody/tr[1]/td',
      'css_selector': 'table > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(1) > td > table > tbody > tr:nth-child(1) > td > div'
   },
   'monkeytype': {
      'name': 'monkeytype',
      'url': 'https://monkeytype.com/',
      'xpath': '//*[@id="words"]',
      'css_selector': '#words'
   }
}


#: INPUTTING THE SITE
# text in input window
site_ask = "'typeracer' or 'monkeytype'?"

# create input window for site using
def inputWindow():
   root = tk.Tk()
   # focus on window
   root.focus_force()
   # put on top
   root.attributes('-topmost', True)
   site_input=tk.StringVar()
   tk.Grid.columnconfigure(root, 0, weight=1)
   root.geometry('')
   root.title('site?')
   site_label = tk.Label(root, text=site_ask)
   site_label.grid(row=0)
   site_entry = tk.Entry(root, textvariable = site_input, width='29')
   site_entry.grid(row=1)
   site_entry.focus()
   tk.Button(root,text = 'ok', command = lambda: submit(None, root, site_input)).grid(row=2)
   root.bind('<Return>', lambda e:submit(e, root, site_input))
   # when press X:
   root.protocol("WM_DELETE_WINDOW", closeInput)
   # open window:
   root.mainloop()

# when press window 'ok'
def submit(e=None, root=None, site_input=None):
   global inputSite,xpath,css_selector,url
   inputSite = site_input.get().strip().lower()
   if inputSite in sites:
      root.destroy()
      xpath = sites[inputSite]['xpath']
      css_selector = sites[inputSite]['css_selector']
      url = sites[inputSite]['url']
   else:
      tk.Label(root, text=site_ask + " no").grid(row=0)

# when press X button
def closeInput():
   # stop code ↓
   raise SystemExit(0)

# use this if you're using single website

# inputSite = "monkeytype"
# inputSite = inputSite.strip().lower()
# if inputSite in sites:
#    xpath = sites[inputSite]['xpath']
#    css_selector = sites[inputSite]['css_selector']
#    url = sites[inputSite]['url']

# use this otherwise
inputWindow()

#: START
def startWindow():
   root = tk.Tk()
   # always on top
   root.attributes('-topmost', True)
   tk.Grid.columnconfigure(root, 0, weight=1)
   root.geometry('')
   root.title('ping')
   tk.Label(root, text=f"enter or press start to begin in {startDelay}s").grid(row=0)
   tk.Button(root,text = 'start', command = lambda: start(None, root)).grid(row=1)
   root.bind('<Return>', lambda e: start(e, root))
   # when press X:
   root.protocol("WM_DELETE_WINDOW", closeInput)
   # open window:
   root.mainloop()
# TODO async to set status (running/stopped/waiting) while typing

# when press 'start'
def start(e=None, root=None, status_label=None):
   # look for text parent element
   element = WebDriverWait(driver, timeout=3).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
   time.sleep(startDelay)
   driver.switch_to.window(original_window_handle) #switch to site tab, warning: might not work if more tabs are open
   root.geometry('')
   conditions(element, root)

#: SPECIAL CONDITIONS
def conditions(element, root):
   text=""
   if inputSite == 'monkeytype':
      activeWord = element.find_elements(By.CLASS_NAME, "active") #get active word before
      while len(activeWord) > 0:
         text += activeWord[0].get_attribute('innerText') + ' '
         for word in element.find_elements(By.CSS_SELECTOR, ".active ~ .word"): #get everything after active word
            word=word.get_attribute('innerText')
            print(word)
            text += word + ' '
         write(text)
         text=''
         activeWord = element.find_elements(By.CLASS_NAME, "active") #get active word during
# BUG single additional space after ending
# BUG continues typing after timer on timed setting since words are already stored; to stop, move mouse to top left/right corner of screen to trigger pyautogui failsafe or just wait
# TODO async to prevent typing from stopping while fetching words (for > 100 words setting)
   elif inputSite == 'typeracer':
      text = element.text
      write(text)

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.set_window_position(0, 0)
driver.get(url)
original_window_handle = driver.current_window_handle
startWindow()