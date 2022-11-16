from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from pynput.keyboard import Controller

import tkinter as tk

import time

import pyautogui

import win32gui
import win32con
import win32api

#: TYPE
NEWLINE={"\n"}
SPECIAL_CHARS={'!','@','#','$','%','^','&','*','(',')','_','+','{','}','[',']','/',':',';','"','=','-'}

# add wait here for keys with unique delay
tabSize=3
typeInterval=0.0001 #default 0.08 (about 110wpm)
specialInterval=0.09 #default 0.09
waitTab=0.1 #default 0.1
waitWord=0.08 #changing to word #default 0.08
waitNewline=0.20 #default 0.2
waitSpecial=0.15 #changing to special #default 0.15
startDelay=1 #in seconds

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
   if len(words) > 0: #* write words
      words = writeWords(words)
   elif len(specials) > 0: #* write specials
      specials = writeSpecials(specials)
   elif len(spaces) > 0:
      while len(spaces) >= tabSize:
         time.sleep(waitTab)
         pyautogui.press("tab") #* enter tab
         spaces = spaces.replace(" ", '', tabSize)
      if len(spaces) > 0:
         words += spaces
         spaces = ""

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

#: INPUT SITE
inputSite = None
xpath = None
url = None

# when press X
def closeInput():
   # stop code ↓
   raise SystemExit(0)

site_ask = "'typeracer' or 'monkeytype'?"

# when press 'ok'
def submit(e=None, root=None, site_input=None, site_label=None):
   inputSite = site_input.get().strip().lower()
   if inputSite in sites:
      root.destroy()
      global site
      for site in sites: #see which site
         if site == inputSite:
            # print(sites[site])
            global xpath,url,css_selector
            xpath = sites[site]['xpath']
            css_selector = sites[site]['css_selector']
            url = sites[site]['url']
            return xpath,url,css_selector,site
   else:
      site_label = tk.Label(root, text=site_ask + " no").grid(row=0)

# create input window for site using
def inputWindow():
   root = tk.Tk()
   root.focus_force()
   root.attributes('-topmost', True)
   site_input=tk.StringVar()
   tk.Grid.columnconfigure(root, 0, weight=1)
   root.geometry('260x88')
   root.minsize(260, 88)
   root.maxsize(260, 88)
   root.title('site?')
   site_label = tk.Label(root, text=site_ask)
   site_label.grid(row=0)
   site_entry = tk.Entry(root, textvariable = site_input, width='29')
   site_entry.grid(row=1)
   site_entry.focus()
   tk.Button(root,text = 'ok', command = lambda: submit(None, root, site_input, site_label)).grid(row=2)
   root.bind('<Return>', lambda e:submit(e, root, site_input, site_label))
   # when press X:
   root.protocol("WM_DELETE_WINDOW", closeInput)
   # open window:
   root.mainloop()

inputWindow()


#: SPECIAL CONDITIONS
def getWord(element):
   # if there is active word remaining and is visible
   if EC.visibility_of_element_located((By.CLASS_NAME, "active")):
      activeWord = element.find_element(By.CLASS_NAME, "active")
      print(activeWord.text)
      pyautogui.write(activeWord.text + " ", typeInterval)
      # for letter in activeWord.text:
         # Controller().type(letter)
         # time.sleep(typeInterval)
      getWord(element)
# hwndMain = win32gui.FindWindow("Google Chrome", "Google Chrome")

def conditions(element):
   text = ""
   if site == 'monkeytype':
      for word in element.find_elements(By.CSS_SELECTOR, "word"):
         text += (word.get_attribute('innerText') + " ")
      # driver.execute_script("window.focus();");
      # driver.switch_to.window(window_handle)
      # print(len(element.find_elements(By.CSS_SELECTOR, f"{css_selector} > *")))
      getWord(element)
   elif site == 'typeracer':
      text = element.text
      write(text)
   # print(text)

#: START
# when press 'start'
def start(e=None):
   # look for text element
   element = WebDriverWait(driver, timeout=3).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
   time.sleep(startDelay)
   # for window_handle in driver.window_handles:
   #    print(original_window_handle)
   #    print(window_handle)
   #    print(len(driver.window_handles))
   driver.switch_to.window(original_window_handle) #switch to site tab, warnig: might not work if more tabs are open
   # driver.switch_to.window(window_handle) #switch to site tab, warning: might not work if more tabs are open
   conditions(element)
def startWindow():
   root = tk.Tk()
   # root.focus_force()
   root.attributes('-topmost', True)
   tk.Grid.columnconfigure(root, 0, weight=1)
   root.geometry('240x65')
   root.minsize(240, 65)
   root.maxsize(240, 65)
   root.title('-')
   tk.Label(root, text=f"enter or press start to begin in {startDelay}s").grid(row=0)
   tk.Button(root,text = 'start', command = start).grid(row=1)
   root.bind('<Return>', start)
   # when press X:
   root.protocol("WM_DELETE_WINDOW", closeInput)
   # open window:
   root.mainloop()
   return

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.set_window_position(0, 0)
driver.get(url)
original_window_handle = driver.current_window_handle
startWindow()