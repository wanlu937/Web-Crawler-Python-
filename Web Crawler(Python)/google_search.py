from bs4 import BeautifulSoup
from selenium import webdriver
from itertools import zip_longest
import pandas as pd
import pymysql
import schedule
import time

def run_crawler():
    # 啟動瀏覽器
    driver = webdriver.Chrome() 

    # 載入網頁
    driver.get("https://trends.google.com.tw/trends/trendingsearches/daily?geo=TW&hl=zh-TW")

    # 等待網頁完全載入
    driver.implicitly_wait(10)

    # 獲取網頁內容
    html = driver.page_source

    # 關閉瀏覽器
    driver.quit()

    soup = BeautifulSoup(html, "lxml")

    tag_div = soup.find("div", class_="feed-list-wrapper").find_next_sibling()
    tag_class = soup.find("div", class_="content-header not-first")
    tag_text = tag_class.find("div", class_="content-header-title")
    print(tag_text.text)

    # tag_nums = tag_div.find_all("div", class_="index")
    tag_index = tag_div.find_all("div", class_="index")
    tag_titles = tag_div.find_all("div", class_="details-top")
    tag_vols = tag_div.find_all("div", class_="search-count-title")

    # 印出每個符合條件的元素的文本內容
    data = []

    for tag_title, tag_vol in zip_longest(tag_titles, tag_vols):
        row = {}
        # if tag_num:
        #     row["Tag_Num"] = tag_num.text.strip()
        if tag_title:
            row["搜尋名稱"] = tag_title.text.strip()
        if tag_vol:
            row["搜尋熱度"] = tag_vol.text.strip()
        data.append(row)

    df = pd.DataFrame(data, index=range(1, len(data) + 1))

    # 將 DataFrame 輸出為表格
    print(df)

    # 建立連接至 MySQL 資料庫
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='', database='top20')
    cursor = conn.cursor()

    # 將爬取到的數據插入到 MySQL 表格中
    for tag_title, tag_vol in zip_longest(tag_titles, tag_vols):
        if tag_title and tag_vol:
            搜尋名稱 = tag_title.text.strip()
            搜尋熱度 = tag_vol.text.strip()
            sql = "INSERT INTO daily (tag_title, tag_vol) VALUES (%s, %s)"
            cursor.execute(sql, (搜尋名稱, 搜尋熱度))

    # 提交變更並關閉連接
    conn.commit()
    conn.close()

schedule.every().day.at("09:00").do(run_crawler)
