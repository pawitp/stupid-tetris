import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

browser = webdriver.Chrome('./chromedriver')
browser.get("http://www.goodoldtetris.com/")

def action(action_name):  
  if action_name == "flip":
    ActionChains(browser).key_down(Keys.ARROW_UP).perform()

  elif action_name == "left":
    ActionChains(browser).key_down(Keys.ARROW_LEFT).perform()

  elif action_name == "right":
    ActionChains(browser).key_down(Keys.ARROW_RIGHT).perform()

  elif action_name == "down":
    ActionChains(browser).key_down(Keys.SPACE).perform()
