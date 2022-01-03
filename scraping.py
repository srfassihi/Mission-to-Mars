# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    hemi_list = hemispheres(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemi_list
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

# ## JPL Space Images Featured Image

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)
    
    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None
    
    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

# ## Mars Facts
def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None
    # Assign columns to dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format
    return df.to_html(classes="table table-striped")

## Hemisphere data 
def hemispheres(browser):
    
    # Visit site
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    # Scrape page
    html = browser.html
    img = soup(html,'html.parser')
    # hemisphere list
    hemisphere_image_urls = []
    # Search names for hemispheres
    results = img.find_all('div', class_="collapsible results")
    hemispheres = results[0].find_all('h3')
    # Get names and add to the list
    for name in hemispheres:
        hemisphere_image_urls.append(name.text)
    # Search for thumbnail links
    thumbnail_results = results[0].find_all('a')
    # thumbnail list
    thumbnail_links = []
    # Loop through thumbnail links for full image
    for thumbnail in thumbnail_results:
        if (thumbnail.img):
            thumbnail_url = 'https://marshemispheres.com/' + thumbnail['href']
            thumbnail_links.append(thumbnail_url)
    
    # Full image list
    jpg_img = []

    # Loop to find full image link
    for url in thumbnail_links:
        browser.visit(url)
        html = browser.html
        img = soup(html,'html.parser')
        
        results = img.find_all('img', class_='wide-image')
        relative_img = results[0]['src']
        
        jpg_link = 'https://marshemispheres.com/' + relative_img
        
        jpg_img.append(jpg_link)

    # ### Store image titles and urls as list of dictionaries
    mars_zip = zip(hemisphere_image_urls, jpg_img)

    hemi_list = []

    # Loop through mars_zip 
    for title, img in mars_zip:
        hemi_dict = {}
        # image title
        hemi_dict['title'] = title
        # image url
        hemi_dict['url'] = img
        # add to list of dictionaries
        hemi_list.append(hemi_dict)
    
    return hemi_list

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())



