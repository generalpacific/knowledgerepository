from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from botocore.exceptions import ClientError
import time
import requests
import os
import json
import traceback
import boto3
import uuid
import dateutil.tz
import datetime

RETRY_EXCEPTIONS = ('ProvisionedThroughputExceededException',
                    'ThrottlingException')
AMAZON_USERNAME = os.environ['AMAZON_USERNAME']
AMAZON_PASSWORD = os.environ['AMAZON_PASSWORD']

def GetLatestHighlight(title):
    dyndb = boto3.resource('dynamodb')
    table = dyndb.Table('latest-book-quote-per-title')
    try:
        response = table.get_item(Key={
            'title': title,
            })
                
    except ClientError as e:
        print("ERROR while getting latest quote. Returning empty. Error: " + 
            e.response['Error']['Message'])
        return ""
    else:
        if 'Item' in response:
            item = response['Item']
            return item['latest_highlight']
        return ""

def UpdateLatestHighlight(title, highlight):
    dyndb = boto3.resource('dynamodb')
    table = dyndb.Table('latest-book-quote-per-title')
    
    print("Updating latest highlight for " + title + " Highlight: " + highlight)
    
    retries = 0
    while True:
        try:
            response = table.put_item(
                    Item={
                    'title': title,
                    'latest_highlight': highlight
                    }
                )
            break
        except ClientError as err:
            if err.response['Error']['Code'] not in RETRY_EXCEPTIONS:
                raise
            sleep(2 ** retries)
            retries += 1
    

def PutInDB(title, author, highlight):
    dyndb = boto3.resource('dynamodb')
    table = dyndb.Table('kindle-highlights')
    highlight_entity_id = str(uuid.uuid1())
    pacific_tz = dateutil.tz.gettz('US/Pacific')
    date_str = datetime.datetime.now(tz=pacific_tz)

    retries = 0
    while True:
        try:
            response = table.put_item(
                    Item={
                    'id' : highlight_entity_id,
                    'tite': title,
                    'author': author,
                    'highlight': highlight,
                    'create_time': str(date_str)
                    }
                )
            break
        except ClientError as err:
            if err.response['Error']['Code'] not in RETRY_EXCEPTIONS:
                raise
            sleep(2 ** retries)
            retries += 1

    table = dyndb.Table('ankientities')
    entity_id = str(uuid.uuid1())
    retries = 0
    while True:
        try:
            response = table.put_item(
                    Item={
                    'entityid' : entity_id,
                    'foreign_id': highlight_entity_id,
                    'source' : 'KINDLE',
                    'recallweight' : 0,
                    'create_time': str(date_str)
                    }
                )
            break
        except ClientError as err:
            if err.response['Error']['Code'] not in RETRY_EXCEPTIONS:
                raise
            sleep(1. ** retries)
            retries += 1
    print("Added highlight id: " + highlight_entity_id + " new entity_id: " + entity_id)

def get_highlights(email, password):

    num_of_books = 10

    print("Starting webdriver for chrome")
    chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument("--log-level=1")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36")

    chrome_options.add_argument("--no-sandbox")
    
    chrome_options.binary_location = os.getcwd() + "/bin/headless-chromium"
    driver = webdriver.Chrome(chrome_options=chrome_options,  service_log_path='/tmp/chromedriver.log')

    driver.get('https://read.amazon.com/kp/notebook')
    print("Reading " + driver.title)


    email_input = driver.find_element(By.XPATH, '//*[@id="ap_email"]')
    pass_input = driver.find_element(By.XPATH, '//*[@id="ap_password"]')
    email_input.send_keys(email)
    pass_input.send_keys(password)


    pass_input.send_keys(Keys.ENTER)

    print("Logging in...")

    # wait for page to load
    try:
        elem = WebDriverWait(driver, 120).until(
        EC.presence_of_element_located((By.ID, "library-section"))
        )
    except Exception as e:
        traceback.print_exc()
        print(driver.page_source)
        raise e

    print("Logged in.")

    def get_book_list():
        books = []
        books = driver.find_elements(By.XPATH, "//div[contains(@class, 'kp-notebook-library-each-book')]")
        return books

    print("Retrieving books...")

    books = get_book_list()
    i = 0
    while True:
        if i == num_of_books:
            break
        if i >= len(books): break
        book = books[i]
        title = book.text.splitlines()[0]
        author = book.text.splitlines()[1][4:]
        print("Getting highlights for: " + title)
        i += 1
        book.click()

        # wait for page to load
        elem = WebDriverWait(driver, 45).until(
        EC.presence_of_element_located((By.XPATH, "//span[contains(@id, 'highlight')]"))
        )

        highlights = []
        highlights = driver.find_elements(
            By.XPATH,
            "//span[@id='highlight']"
        )

        # skip the first one since it's just a number
        highlight_text = []
        for highlight in highlights:
            if highlight.text != "":
                highlight_text.append(highlight.text)

        # Add to the dynamodb table.
        latest_highlight = GetLatestHighlight(title)
        passed_latest_highlight = False 
        if latest_highlight == "":
            passed_latest_highlight = True
        for highlight in highlight_text:
            if passed_latest_highlight == False:
                if highlight == latest_highlight:
                    passed_latest_highlight = True
                continue;
            PutInDB(title, author, highlight)
        
        # Add to latest quote per book.
        UpdateLatestHighlight(title, highlight_text[-1])

        books = get_book_list()


def lambda_handler(event, context):
    try:
        get_highlights(AMAZON_USERNAME, AMAZON_PASSWORD)
    except Exception as e:
        traceback.print_exc()
        with open('/tmp/chromedriver.log', 'rb') as logfile:
            print(logfile.readlines())
        raise e

    return {
        'statusCode': 200,
        'body': json.dumps('Successfully ingested kindle highlights!')
    }
