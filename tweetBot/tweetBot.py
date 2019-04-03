from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep, strftime
from random import randint
import pandas as pd
import schedule

def follow(webDriver, tweet):
    if any(i in tweet.text for i in ['Follow', 'follow', 'FOLLOW']):
        try:
            javaScript = "var evObj = document.createEvent('MouseEvents');evObj.initMouseEvent(\"mouseover\",true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);arguments[0].dispatchEvent(evObj);"
            webDriver.execute_script(javaScript, tweet.find_element_by_css_selector('.username.u-dir.u-textTruncate'))
            sleep(4)
            popup = webDriver.find_element_by_id('profile-hover-container')
            sleep(randint(1,4))
            follow = popup.find_element_by_css_selector('.EdgeButton.EdgeButton--secondary.EdgeButton--small.button-text.follow-text')
            sleep(randint(1,4))
            follow.click()
        except:
            print("Couldn't follow user...")
    sleep(randint(1,4))

#Like tweet
def like(webDriver, tweet):
    if any(i in tweet.text for i in ['like', 'Like', 'LIKE']):
        try:
            like = tweet.find_element_by_css_selector('.ProfileTweet-actionButton.js-actionButton.js-actionFavorite')
            sleep(1)
            like.click()
        except:
            print("Couldn't like tweet...")
    sleep(randint(1,4))

def retweet(webDriver, tweet):
    if any(i in tweet.text for i in ['retweet', 'Retweet', 'RT', 'rt']):
        try:
            retweet = tweet.find_element_by_css_selector('.ProfileTweet-actionButton.js-actionButton.js-actionRetweet')
            sleep(2)
            retweet.click()
            sleep(2)
            retweet = webDriver.find_element_by_css_selector('.EdgeButton.EdgeButton--primary.retweet-action')
            sleep(2)
            retweet.click()
        except:
            print("Couldn't retweet tweet...")
    sleep(randint(1,4))

def login(webDriver):
    #Login to twitter
    userName = webDriver.find_element_by_xpath('//*[@id="doc"]/div/div[1]/div[1]/div[1]/form/div[1]/input')
    sleep(1)
    userName.send_keys('') #Enter your username
    sleep(randint(1,3))
    password = webDriver.find_element_by_xpath('//*[@id="doc"]/div/div[1]/div[1]/div[1]/form/div[2]/input')
    sleep(1)
    password.send_keys('') #Enter your password
    sleep(randint(1,3))
    password.send_keys(Keys.ENTER)

def search(webDriver, searchString):
    #Search bar
    search = webDriver.find_element_by_xpath('//*[@id="search-query"]')
    #Populate page with desirable tweets
    search.clear()
    search.send_keys(searchString)
    search.send_keys(Keys.ENTER)
    sleep(4)

    #Get latest tweets
    latest = webDriver.find_elements_by_css_selector('.AdaptiveFiltersBar-target.AdaptiveFiltersBar-target--link.js-nav.u-textUserColorHover')
    sleep(2)
    latest[1].click()
    sleep(4)

def tweetBot(wD):
    wD.implicitly_wait(10)
    wD.get("https://twitter.com")
    sleep(3)
    login(webDriver=wD)

    #List of used tweets
    try:
        usedTweets = pd.read_csv('usedTweets.csv', header=0)
        tweetCount = len(usedTweets.index)
    except:
        usedTweets = pd.DataFrame(columns = ['Tweets'])
        usedTweets.to_csv("usedTweets.csv")
        tweetCount = 0

    #Words to avoid in tweets
    bannedWords = ['bot', 'b0t', 'fake', 'nothing', 'spam', 'lose', 'followandrt2win', 'spot', 'sp0t', 'botspotterbot', 'lvbroadcasting', 'jflessauSpam', 'bryster125', 'MobileTekReview', 'ilove70315673', 'traunte', 'ericsonabby', '_aekkaphon', 'jcarmela278', 'People', 'Promoted', 'AD', 'Ad']



    for searchStr in ["giveaway rt", "Retweet to win", "RT to win"]:
        search(webDriver=wD, searchString = searchStr);

        #Scroll for more tweets 40 times
        for x in range(0, 20):


            #Select all tweets from current page
            tweets = wD.find_elements_by_class_name('tweet')
            sleep(3)

            #Iterate through tweets
            for t in tweets:

                try:
                    #Scroll to current tweet
                    wD.execute_script("window.scrollTo(0, " + str(tweet.location['y']) + ")")
                except:
                    pass

                #Check if current tweet is used tweet
                try:
                    tweetText = t.find_element_by_class_name('tweet-text').text
                except:
                    continue
                sleep(1)
                if tweetText in usedTweets['Tweets'].values:
                    continue

                sleep(3)
                #Avoid banned words
                if any(i in t.text for i in bannedWords):
                    continue
                sleep(3)

                #Like tweet
                like(webDriver=wD, tweet=t)

                #Retweet
                retweet(webDriver=wD, tweet=t)

                #Add tweet to used tweets data frame
                usedTweets.loc[tweetCount, 'Tweets'] = tweetText
                tweetCount += 1
                usedTweets.to_csv('usedTweets.csv', index = False)

            #Scroll to bottom of page
            wD.execute_script("window.scrollTo(0, document.body.scrollHeight)")

            sleep(2)

    #Create used tweets csv
    usedTweets.to_csv('usedTweets.csv', index = False)
    wD.close()

def main():
    tweetBot(wD = webdriver.Chrome(executable_path = '/usr/local/bin/chromedriver'))
    schedule.every(1).to(2).hours.do(tweetBot)
    while True:
        schedule.run_pending()
        sleep(1)

if __name__ == "__main__":
    main()
