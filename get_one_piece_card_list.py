import time

import unicodedata
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By


def get_link_list():
    html = """
            <select name="series" class="selectModal" id="series" style="display: none;">
                <option value="">Recording</option>
                <option value="">ALL</option>
                <option value="569201">EXTRA BOOSTER &lt;br class="spInline"&gt;-MEMORIAL COLLECTION- [EB-01]</option>
                <option value="569106" selected="">BOOSTER PACK &lt;br class="spInline"&gt;-WINGS OF THE CAPTAIN- [OP-06]</option>
                <option value="569105">BOOSTER PACK &lt;br class="spInline"&gt;-AWAKENING OF THE NEW ERA- [OP-05]</option>
                <option value="569104">BOOSTER PACK &lt;br class="spInline"&gt;-KINGDOMS OF INTRIGUE- [OP-04]</option>
                <option value="569103">BOOSTER PACK &lt;br class="spInline"&gt;-PILLARS OF STRENGTH- [OP-03]</option>
                <option value="569102">BOOSTER PACK &lt;br class="spInline"&gt;-PARAMOUNT WAR- [OP-02]</option>
                <option value="569101">BOOSTER PACK &lt;br class="spInline"&gt;-ROMANCE DAWN- [OP-01]</option>
                <option value="569013">ULTRA DECK &lt;br class="spInline"&gt;-The Three Brothers- [ST-13]</option>
                <option value="569012">STARTER DECK &lt;br class="spInline"&gt;-Zoro and Sanji- [ST-12]</option>
                <option value="569011">STARTER DECK &lt;br class="spInline"&gt;-Uta- [ST-11]</option>
                <option value="569010">ULTRA DECK &lt;br class="spInline"&gt;-The Three Captains- [ST-10]</option>
                <option value="569009">STARTER DECK &lt;br class="spInline"&gt;-Yamato- [ST-09]</option>
                <option value="569008">STARTER DECK &lt;br class="spInline"&gt;-Monkey D. Luffy- [ST-08]</option>
                <option value="569007">STARTER DECK &lt;br class="spInline"&gt;-Big Mom Pirates- [ST-07]</option>
                <option value="569006">STARTER DECK &lt;br class="spInline"&gt;-Absolute Justice- [ST-06]</option>
                <option value="569005">STARTER DECK &lt;br class="spInline"&gt;-ONE PIECE FILM edition- [ST-05]</option>
                <option value="569004">STARTER DECK &lt;br class="spInline"&gt;-Animal Kingdom Pirates- [ST-04]</option>
                <option value="569003">STARTER DECK &lt;br class="spInline"&gt;-The Seven Warlords of the Sea- [ST-03]</option>
                <option value="569002">STARTER DECK &lt;br class="spInline"&gt;-Worst Generation- [ST-02]</option>
                <option value="569001">STARTER DECK &lt;br class="spInline"&gt;-Straw Hat Crew- [ST-01]</option>
                <option value="569901">Promotion card</option>
                <option value="569801">Limited Product Card</option>
            </select>
            """

    booster_list = []

    soup = BeautifulSoup(html, "html.parser")
    options = soup.find_all("option")
    for option in options:
        if not option["value"]:
            continue
        model = {"link": f"https://en.onepiece-cardgame.com/cardlist/?series={option['value']}",
                 "series": option.text.replace("<br class=\"spInline\">", "")}
        # clean html text
        model["slug"] = slugify(model["series"])
        booster_list.append(model)

    return booster_list


def download_html(booster_list):
    import requests

    count = 1
    for model in booster_list if count < 2 else []:
        link = model["link"]
        series = model["series"]
        slug = model["slug"]
        response = requests.get(link)
        print(response.text)
        with open(f"htmls/{slug}.html", "w", encoding="utf-8") as f:
            f.write(str(response.text))
        count += 1


def slugify(name):
    normalized = unicodedata.normalize("NFKD", name)
    slug = "".join([c for c in normalized if not unicodedata.combining(c)])
    slug = slug.lower().strip()
    slug = "".join([c if c.isalnum() or c == "-" else " " for c in slug])
    slug = "-".join(slug.split())
    return slug


def download_with_selenium(model_list):
    ilustration_types = [
        {
            "checkbox_id": "illustration_Comic",
            "slug": "comic"
        },
        {
            "checkbox_id": "illustration_Animation",
            "slug": "animation"
        },
        {
            "checkbox_id": "illustration_Original Illustrations",
            "slug": "original_illustrations"
        },
        {
            "checkbox_id": "illustration_Other",
            "slug": "other"
        },
    ]

    submit_button_value = "SEARCH"

    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)

    # ed_options = webdriver.EdgeOptions()
    # edprefs = {"profile.managed_default_content_settings.images": 2}
    # ed_options.add_experimental_option("prefs", edprefs)
    # driver = webdriver.Edge(options=ed_options)

    driver.set_window_size(1920, 1080)
    for illustration_type in ilustration_types:
        for model in model_list:
            print(f"downloading {model['series']} {illustration_type['slug']}")
            link = model["link"]
            slug = model["slug"]
            driver.get(link)
            driver.implicitly_wait(1)

            print("clicking on illustration type")
            id_a = driver.find_element(By.ID, illustration_type["checkbox_id"])
            label = id_a.find_element(By.XPATH, "./following-sibling::label")
            driver.execute_script("arguments[0].click();", label)
            time.sleep(1)

            print("clicking on submit button")
            div_element = driver.find_element(By.CLASS_NAME, "commonBtn.submitBtn")
            submit_button = div_element.find_element(By.XPATH, f".//input[@value='{submit_button_value}']")
            submit_button.click()

            # screen = submit_button.screenshot_as_png
            # with open("screen.png", "wb") as f:
            #     f.write(screen)

            time.sleep(1)
            print("downloading html")
            with open(f"htmls/{slug}_{illustration_type['slug']}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)


if __name__ == "__main__":
    model_list = get_link_list()
    with open("boosters.json", "w") as f:
        f.write(str(model_list))
    download_with_selenium(model_list)
