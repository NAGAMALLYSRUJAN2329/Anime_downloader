from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import tqdm
import requests
from zipfile import ZipFile
import tempfile
import shutil
from bs4 import BeautifulSoup

def get_download_link(driver, url, resolution = 480):
    resolution_mapping = {
        360:0,
        480:1,
        720:2,
        1080:3,
    }
    driver.get(url)

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    time.sleep(5)

    download_divs = driver.find_elements(By.CLASS_NAME, "dowload")
    if len(download_divs) > 7:
        fourth_download_div = download_divs[resolution_mapping[resolution]]
    else:
        # if resolution_mapping[resolution]!=0: print(f"ALL resolutions not available for this {url}")
        fourth_download_div = download_divs[0]

    download_link = fourth_download_div.find_element(By.TAG_NAME, "a").get_attribute("href")

    # with open('page_content.html', 'w', encoding='utf-8') as file:
    #     file.write(driver.page_source)
    return download_link

def download_url(url, vid_name):
    response = requests.get(url, allow_redirects=True)
    with open(f'{vid_name}.mp4', 'wb') as file:
        file.write(response.content)

def get_link(url):
    # driver = webdriver.Firefox()
    # driver.get('http://selenium.dev/')
    # driver.get(url)
    # WebDriverWait(driver, 20).until(
    #     EC.presence_of_element_located((By.TAG_NAME, "body"))
    # )
    # time.sleep(5)
    # download_li = driver.find_elements(By.CLASS_NAME, "download")
    # download_li = download_li.find_element(By.TAG_NAME, "a").get_attribute("href")
    # driver.quit()

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # with open('temp.html', 'w', encoding='utf-8') as file:
    #     file.write(soup.prettify())
    download_li = soup.find('li', class_='dowloads').find('a')['href']
    return download_li

def main(base_url, resolution, last_ep_num, download_dir):
    driver = webdriver.Firefox()
    # driver.get('http://selenium.dev/')
    base_url = base_url.replace('category/', '')
    episodes_to_download = [i for i in range(1, last_ep_num+1)]
    output_dir = base_url.split('/')[-1]
    output_dir = f'{download_dir}/{output_dir}'
    os.makedirs(output_dir, exist_ok = True)
    for ep in tqdm.tqdm(episodes_to_download):
        ep = str(ep)
        link = get_link(base_url+'-episode-'+ep)
        download_link = get_download_link(driver, link, resolution)
        download_url(download_link, f'{output_dir}/episode_{ep}')
    driver.quit()
    return output_dir

import streamlit as st
def run_app():
    st.title("Anime Episode Downloader")
    st.markdown("### Important Note")
    st.markdown("""
    - When you click on Load Episodes button Firefox window will be opened in the background, don't close it as it will terminate the episode downloading process.
    """)

    base_url = st.text_input("Enter Base URL:", "https://anitaku.pe/category/yozakura-san-chi-no-daisakusen")
    resolution = st.selectbox("Select Resolution:", [360, 480, 720, 1080])
    last_ep_num = st.number_input("Enter Last Episode Number:", min_value=1, value=1, step=1)
    # download_dir = st.text_input("Enter Download Directory:", os.getcwd())

    if st.button("Load Episodes to download"):
        st.write("Download process started...")
        # main(base_url, resolution, last_ep_num, download_dir)
        # with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdirname = 'temp'
        output_dir = main(base_url, resolution, last_ep_num, tmpdirname)
        zip_path = os.path.join(tmpdirname, "anime_episodes.zip")
        with ZipFile(zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), file)
                    os.remove(os.path.join(root, file))
        with open(zip_path, "rb") as f:
            st.download_button(
                label="Download Episodes",
                data=f,
                file_name="anime_episodes.zip",
                mime="application/zip",
                on_click=lambda: shutil.rmtree(tmpdirname),
            )
        # import subprocess;subprocess.Popen(['python', 'delete_folder.py'],close_fds=True)
        st.write("Download process completed!")

    # st.markdown("### Made by")
    # st.markdown("""
    #     - **Nagamally Srujan**
    #     - [**Mail**](mailto:nagamallisrujan@gmail.com)
    #     - [**GitHub**](https://github.com/NAGAMALLYSRUJAN2329)
    #     - [**LinkedIn**](https://www.linkedin.com/in/srujan-nagamally/)
    # """)
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
    .footer {
        width: 100%;
        background-color: black;
        color: white;
        text-align: center;
        padding: 10px;
        position: relative; /* Make it non-fixed */
    }
    .footer p {
        margin: 5px 0; /* Adjust spacing between elements */
    }
    .footer .icons {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .footer .icons a {
        color: white; /* Ensure the icons are white */
        text-decoration: none; /* Remove underline from links */
        margin: 0 10px; /* Space out the icons */
        font-size: 24px; /* Adjust icon size */
    }
    .footer .icons a:hover {
        color: #FFD700; /* Optional: Change icon color on hover */
    }
    </style>
    <div class="footer">
        <p>Made by Nagamally Srujan</p>
        <div class="icons">
            <a href="mailto:nagamallisrujan@gmail.com" title="Mail"><i class="fas fa-envelope"></i></a>
            <a href="https://github.com/NAGAMALLYSRUJAN2329" title="GitHub"><i class="fab fa-github"></i></a>
            <a href="https://www.linkedin.com/in/srujan-nagamally/" title="LinkedIn"><i class="fab fa-linkedin"></i></a>
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    # base_url = "https://anitaku.pe/category/yozakura-san-chi-no-daisakusen"
    # resolution = 480
    # last_ep_num = 2
    # download_dir = 'output'
    # main(base_url, resolution, last_ep_num, download_dir)

    run_app()

# streamlit run main.py