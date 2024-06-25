import glob
import json
from copy import deepcopy

from bs4 import BeautifulSoup

ONE_PIECE_BASE_URL = "https://en.onepiece-cardgame.com"


def get_id(string):
    string = string.split("_")
    if len(string) == 2:
        return string[0], string[1]
    return string[0], None


def get_illustration_type(string):
    string = string.lower()
    if string.endswith("original_illustrations"):
        return "Original Illustrations"
    return string.split("_")[-1].title()


def make_url(string):
    if string.startswith(".."):
        string = string.replace("..", "")
    return f"{ONE_PIECE_BASE_URL}{string}"


def get_cost(string):
    string = string.lower()
    string = string.replace("life", "").replace("cost", "").strip()
    if string == "-":
        return None
    return string


def get_power(string):
    string = string.lower()
    string = string.replace("power", "").strip()
    if string == "-":
        return None
    return string


def get_counter(string):
    string = string.lower()
    string = string.replace("counter", "").strip()
    if string == "-":
        return None
    return string


def get_color(string):
    string = string.lower()
    return string.replace("color", "").strip()


def get_crew(string):
    string = string.lower()
    return string.replace("type", "").strip().title().split("/")


def get_effect(string):
    string = string.lower()
    if string.startswith("effect"):
        return string[6:]
    return string


def get_card_set(string):
    if string.startswith("Card Set(s)"):
        string = string[11:]

    if string.startswith("-"):
        string = string[1:].replace("-", "", 1)

    return string.title()


def get_attribute(string):
    string = string.lower()
    if string.contains("attribute"):
        return None
    return string.split("\n")[-2]


def extractor(file_list):
    # open card_data.json read and write
    with open("data/card_data.json", "r", encoding="utf-8") as f:
        card_data_file = f.read()
        card_data_file = json.loads(card_data_file)

    div_example = """
                    <dl class="modalCol" id="OP07-001">
                        <dt>
                            <button class="scrollBtn">ボタン</button>
                            <div class="infoCol">
                                <span>OP07-001</span> | <span>L</span> | <span>LEADER</span>
                            </div>
                            <div class="cardName">Monkey.D.Dragon</div>
                        </dt>
                        <dd>
                            <div class="frontCol">
                                <img src="../images/cardlist/card/OP07-001.png?240619" alt="Monkey.D.Dragon">
                                <a href="javascript:void(0);" class="commonBtn textViewBtn"><span>TEXT VIEW</span></a>
                            </div>
                            <div class="backCol">
                                <div class="col2">
                                    <div class="cost"><h3>Life</h3>5</div>
                                    <div class="attribute">
                                        <h3>Attribute</h3>
                                        <img src="/images/cardlist/attribute/ico_type03.png" alt="Special"><i>Special</i>
                                    </div>
                                </div>
                                <div class="col2">
                                    <div class="power"><h3>Power</h3>5000</div>
                                    <div class="counter"><h3>Counter</h3>-</div>
                                </div>
                                <div class="color"><h3>Color</h3>Red</div>
                                <div class="feature"><h3>Type</h3>Revolutionary Army</div>
                                <div class="text"><h3>Effect</h3>[Activate: Main] [Once Per Turn] Give up to 2 total of your currently
                                    given DON!! cards to 1 of your Characters.
                                </div>
                                <div class="getInfo"><h3>Card Set(s)</h3>-500 YEARS IN THE FUTURE- [OP-07]</div>
                                <a href="javascript:void(0);" class="commonBtn cardViewBtn"><span>CARD VIEW</span></a>
                            </div>
                        </dd>
                    </dl>
    """

    pack_data_example = {
        "pack_name": None,  # (500 Years In The Future) Op-07
        "pack_code": None,  # OP-07
    }

    card_data_example = {
        "id": None,  # OP07-001
        "illustration_url": None,  # https://en.onepiece-cardgame.com/images/cardlist/card/OP07-001.png?240619
        "illustration_type": None,  # comic, animation, original_illustrations, other
        "illustration_alternative_id": None,  # p_2
        "name": None,  # Monkey.D.Dragon
        "rare": None,  # L
        "cost": None,  # 5
        "attribute": None,  # Special
        "attribute_image_url": None,  # https://en.onepiece-cardgame.com/images/cardlist/attribute/ico_type03.png
        "power": None,  # 5000
        "counter": None,  # None
        "color": [],  # Red
        "crew": [],  # Revolutionary Army
        "effect": None,
        # [Activate: Main] [Once Per Turn] Give up to 2 total of your currently given DON!! cards to 1 of your Characters.  # noqa
        "card_set": None,  # 500 YEARS IN THE FUTURE- [OP-07]
        "pack_data": pack_data_example,
    }

    for file in file_list:
        with open(file, "r", encoding="utf-8") as f:
            html_content = f.read()

        pack = deepcopy(pack_data_example)

        file_name = file.split("/")[-1]
        try:
            pack["pack_name"] = (
                f"({file_name.split("--")[0].replace("-", " ")}) {file_name.split('--')[1].replace('-', ' ')}".title()
            )

            pack["pack_code"] = file_name.split("--")[2].split("_")[0]
        except IndexError:
            pass

        soup = BeautifulSoup(html_content, "html.parser")
        card_dl_elements_list = soup.find_all("dl", class_="modalCol")

        for element in card_dl_elements_list:
            card = deepcopy(card_data_example)
            card["id"], card["illustration_alternative_id"] = get_id(element["id"])
            card["illustration_url"] = make_url(element.find("img")["src"])
            card["illustration_type"] = get_illustration_type(
                file.split("--")[-1].split(".")[0]
            )
            card["name"] = element.find("div", class_="cardName").text
            card["rare"] = (
                element.find("div", class_="infoCol").find_all("span")[1].text
            )
            card["cost"] = get_cost(element.find("div", class_="cost").text)
            attribute = element.find("div", class_="attribute").text
            if card["name"] == "Bad Manners Kick Course":
                print(attribute, get_attribute(attribute))
            card["attribute"] = get_attribute(attribute)
            try:
                card["attribute_image_url"] = make_url(
                    element.find("div", class_="attribute").find("img")["src"]
                )
            except TypeError:
                card["attribute_image_url"] = None
            card["power"] = get_power(element.find("div", class_="power").text)
            card["counter"] = get_counter(element.find("div", class_="counter").text)
            card["color"] = get_color(element.find("div", class_="color").text)
            card["crew"] = get_crew(element.find("div", class_="feature").text)
            card["effect"] = get_effect(element.find("div", class_="text").text)
            card["card_set"] = get_card_set(element.find("div", class_="getInfo").text)
            card["pack_data"] = pack
            card_data_file.append(card)

    with open("data/card_data.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(card_data_file, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    html_file_list = glob.glob("data/htmls/*.html")
    extractor(html_file_list)
