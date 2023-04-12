
import os
from time import sleep

import requests
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


def get_products_links(driver, url):
    driver.get(url)
    sleep(1)
    elements = driver.find_elements(by=By.XPATH, value="//div[@class='productName']/a")

    links = []
    for element in elements:
        links.append(element.get_attribute('href'))
    
    return links


def get_comments_links(driver, url):
    driver.get(url)
    try:
        ul_element = driver.find_element(by=By.CSS_SELECTOR, value='ul.list-comments')
    except Exception as e:
        return []
    
    links = []
    li_elements = ul_element.find_elements(by=By.TAG_NAME, value='li')
    for li in li_elements:
        a_element = li.find_element(by=By.CSS_SELECTOR, value='div.reviewTextSnippet a')
        link = a_element.get_attribute('href')
        links.append(link)
    
    return links


def get_main_image(driver, url):
    driver.get(url)
    element = driver.find_element(by=By.CSS_SELECTOR, value='div.mainpic span a img')
    link = element.get_attribute('data-original')
    return link


def get_comment_images(driver, url):
    driver.get(url)
    elements = driver.find_elements(by=By.CSS_SELECTOR, value='div.inline-image span a img')
    
    links = []
    for element in elements:
        link = element.get_attribute('data-original')
        links.append(link)

    return links


def download_images(path, main_image_link, comment_images, p_link):
    with open(f'{path}/url.txt', 'w') as f:
        f.write(p_link)
    
    response = requests.get(main_image_link)
    with open(f'{path}/main_image.jpg', 'wb') as f:
        f.write(response.content)
        
    for i, link in enumerate(comment_images):
        response = requests.get(link)
        with open(f'{path}/comment_image_{i}.jpg', 'wb') as f:
            f.write(response.content)


def main():
    options = Options()
    options.page_load_strategy = 'eager'
    options.headless = True
    with webdriver.Chrome(executable_path='./chromedriver', options=options) as driver:
        data = [
            ('https://irecommend.ru/catalog/reviews/938-332121', 98),
            ('https://irecommend.ru/catalog/reviews/938-437691', 59),
            ('https://irecommend.ru/catalog/reviews/938-776346', 41)
        ]
        for url, page_num in data:
            for page in range(page_num):
                product_links = get_products_links(driver, f'{url}?page={page}')
                
                for p_link in product_links:
                    path = p_link.split('/')[-1]
                    if os.path.exists(path):
                        continue
                    else:
                        os.mkdir(path)
                    
                    comment_links = get_comments_links(driver, p_link)
                    main_image_link = get_main_image(driver, p_link)
                    
                    logger.info(p_link)
                    comments_images = []
                    for c_link in comment_links:
                        logger.info(c_link)
                        images = get_comment_images(driver, c_link)
                        comments_images.extend(images)
                        
                    logger.info(f'Comment images len {len(comments_images)}')
                    
                    download_images(path, main_image_link, comments_images, p_link)
    

if __name__ == '__main__':
    main()