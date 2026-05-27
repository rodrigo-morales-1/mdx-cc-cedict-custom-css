import bs4
from mdict_utils.base.readmdict import MDX
import tqdm
import logging
import datetime
import os

log_basename = datetime.datetime.now().astimezone().strftime('%Y-%m-%dT%H-%M-%S%z') + '.log'
log_absolute_path = os.path.join(os.path.dirname(__file__), log_basename)

logging.basicConfig(filename=log_absolute_path,
                    filemode='a',
                    format='[%(asctime)s][%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S%z',
                    level=logging.DEBUG)

item_limit = 100
my_mdx = MDX('cc-cedict_enlarged_characters.mdx')
output_file = open('output.txt', 'w')

def build_html(mdx_value):
    has_zh_hant = False
    soup = bs4.BeautifulSoup(mdx_value, 'html.parser')
    parts = soup.select('div div div')
    # Some definitions don't show traditional characters.
    if len(parts) == 2:
        zh_hans_element = parts[0]
        pinyin_element = parts[1]
    elif len(parts) == 3:
        zh_hans_element = parts[0]
        zh_hant_element = parts[1]
        pinyin_element = parts[2]
        has_zh_hant = True
    else:
        print("This shouldn't happen.")
    # ------------------------------
    # Store data in lists
    # ------------------------------
    zh_hans_list = []
    pinyin_list = []
    senses_list = []
    for item in zh_hans_element.select('span'):
        zh_hans_list.append(item.text.strip())
    for item in pinyin_element.select('span'):
        pinyin_list.append(item.text.strip())
    if has_zh_hant:
        zh_hant_list = []
        for item in zh_hant_element.select('span'):
            zh_hant_list.append(item.text.strip())
    senses = soup.select('div div ul li')
    for sense in senses:
        senses_list.append(sense.text.strip())
    # ------------------------------
    # Create HTML
    # ------------------------------
    single_definition_soup = bs4.BeautifulSoup("""
    <head>
        <link rel="stylesheet" href="cc-cedict-enlarged-characters.css">
    </head>
    <body>
        <div class="lexeme-container">
            <div class="zh-hans-container">
            </div>
            <div class="zh-hant-container">
            </div>
            <div class="pinyin-container">
            </div>
            <ul class="senses-container">
            </ul>
        </div>
    </body>
    """, 'html.parser')
    zh_hans_container = single_definition_soup.select_one(".zh-hans-container")
    zh_hant_container = single_definition_soup.select_one(".zh-hant-container")
    pinyin_container = single_definition_soup.select_one(".pinyin-container")
    senses_container = single_definition_soup.select_one(".senses-container")
    for index, item in enumerate(zh_hans_list):
        new_div = soup.new_tag('div')
        new_div['class'] = f'zh-hans-syllable syllable-{index+1}'
        new_div.string = item
        zh_hans_container.append(new_div)
    for index, item in enumerate(pinyin_list):
        new_div = soup.new_tag('div')
        new_div['class'] = f'pinyin-syllable syllable-{index+1}'
        new_div.string = item
        pinyin_container.append(new_div)
    for item in senses_list:
        new_div = soup.new_tag('li')
        new_div.string = item
        senses_container.append(new_div)
    if has_zh_hant:
        for index, item in enumerate(zh_hant_list):
            new_div = soup.new_tag('div')
            new_div['class'] = f'zh-hant-syllable syllable-{index+1}'
            new_div.string = item
            zh_hant_container.append(new_div)
    return str(single_definition_soup)

for key, value in tqdm.tqdm(my_mdx.items(), total=my_mdx.__len__()):
    key_decoded = key.decode('utf-8')
    value_decoded = value.decode('utf-8')
    logging.debug(key_decoded)
    # ------------------------------
    # Write entries
    # ------------------------------
    output_file.write(key_decoded)
    output_file.write('\n')
    if value_decoded.startswith('@@@LINK='):
        output_file.write(value_decoded.rstrip())
    elif value_decoded.startswith('<div'):
        value_decoded = build_html(value_decoded)
        output_file.write("".join(line.strip() for line in value_decoded.splitlines()))
    elif value_decoded.startswith('#VALUE!'):
        # The word "几号" has a definition called "几号".
        continue
    else:
        raise Exception("This shouldn't happen.")
    output_file.write('\n')
    output_file.write('</>')
    output_file.write('\n')
    # For testing purposes
    # item_limit -= 1
    # if item_limit == 0:
    #   break



