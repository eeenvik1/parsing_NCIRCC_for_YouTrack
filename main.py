import json
import PyPDF2
import re
import os.path
import os
import time
import jinja2
import requests
from bs4 import BeautifulSoup
import urllib3
from cpe import CPE
import nvdlib
import ast
config = dotenv_values(".env")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
PATH = config.get("PATH")
YOU_TRACK_TOKEN = config.get("YOU_TRACK_TOKEN")

#parse bulletine NKCKI--------------------------------------------------------------------------------------------------
def get_cve_list(name_list):
    cve_list = []
    cve_list_repeat = []
    for name in name_list:
        pdf_file = open(f'{PATH}{name}', 'rb')
        read_pdf = PyPDF2.PdfFileReader(pdf_file)
        number_of_pages = read_pdf.getNumPages()
        data = ''
        for i in range(number_of_pages):
            page = read_pdf.getPage(i)
            page_content = page.extractText()
            data1 = json.dumps(page_content)
            data += data1

        rez = ''
        for n, item in enumerate(data, start=0):
            if item != '\\':
                rez += data[n]

        result = ''
        for n, item in enumerate(rez, start=0):
            if item != 'n':
                result += rez[n]
        rez1 = result.replace(" ", "")

        regex = re.findall(r'CVE-\d{4}-\d{4,6}', rez1)
        for cve in regex:
            cve_list_repeat.append(cve)
    for item in cve_list_repeat:
        if item not in cve_list:
            cve_list.append(item)
    return cve_list


def get_links_for_bulletine():
    links = []
    for page in range(3):
        r = requests.get("https://safe-surf.ru/specialists/bulletins-nkcki/?PAGEN_1={}".format(page))
        soup = BeautifulSoup(r.text, "html.parser")
        for vuln in soup.find_all("div", "blockBase blockBulletine"):
            bulletin_pdf_url = "https://safe-surf.ru{}".format(vuln.find('h4').find('a')['href'])
            links.append(bulletin_pdf_url)
    return links


def create_pdf_file(links):
    for str in links:
        get = requests.get(str)
        name = str.replace("https://safe-surf.ru/upload/VULN/", "")
        check_file = os.path.exists(f'{PATH}{name}')
        if check_file == 0:
            with open(f'{PATH}{name}', 'wb') as f:
                f.write(get.content)
        else:
            print(f'file {name} already exists')


def get_name_list(path):
    name_list = os.listdir(path)
    return name_list

def remove_pdf_file(path):
    for item in path:
        os.remove(item)

#-----------------------------------------------------------------------------------------------------------------------

def get_cve_data(cve):
    template = """
### Описание

{{d.cve}}

### Дата публикации

{{d.lastModifiedDate}}

### Дата выявления

{{d.publishedDate}}

### Продукт, вендор

{% for vendor in d.product_vendor_list %}{{vendor}}
{% endfor %}


### CVSSv3 Score

{{d.score}}

### CVSSv3 Vector

{{d.vector}}

### CPE

{% if d.configurations.nodes %}
{% for conf in d.configurations.nodes %}

#### Configuration {{ loop.index }}
{% if conf.operator == 'AND'%}{% set children = conf.children %}{% else %}{% set children = [conf] %}{% endif %}{% if children|length > 1 %}
**AND:**{% endif %}{% for child in children %}{% if child.cpe_match|length > 1 %}**OR:**{% endif %}{% for cpe in child.cpe_match %}
{{ cpe.cpe23Uri | replace("*", "\*") }}{% endfor %}{% endfor %}{% endfor %}
{% endif %}
### Links

{% for link in d.links %}{{ link }}
{% endfor %}

{% if d.exploit_links %}
### Exploit
{% for exploit in d.exploit_links %}{{exploit}}
{% endfor %}
{% endif %}
    """

    YOU_TRACK_PROJECT_ID = config.get("YOU_TRACK_PROJECT_ID")
    YOU_TRACK_BASE_URL = config.get("YOU_TRACK_BASE_URL")
    URL = YOU_TRACK_BASE_URL + "/issues"
    pattern = ['Stack-based buffer overflow', 'Arbitrary command execution', 'Obtain sensitive information',
               'Local privilege escalation', 'Security Feature Bypass', 'Out-of-bounds read', 'Out of bounds read',
               'Denial of service', 'Denial-of-service', 'Execute arbitrary code', 'Expose the credentials',
               'Cross-site scripting (XSS)', 'Privilege escalation', 'Reflective XSS Vulnerability',
               'Execution of arbitrary programs', 'Server-side request forgery (SSRF)', 'Stack overflow',
               'Execute arbitrary commands', 'Obtain highly sensitive information', 'Bypass security',
               'Remote Code Execution', 'Memory Corruption', 'Arbitrary code execution', 'CSV Injection',
               'Heap corruption', 'Out of bounds memory access', 'Sandbox escape', 'NULL pointer dereference',
               'Remote Code Execution']
    try:
        r = nvdlib.getCVE(cve, cpe_dict=False)
        cve_cpe_nodes = r.configurations.nodes
        cpe_nodes = ast.literal_eval(str(r.configurations))
        score = r.v3score
        links = []
        exploit_links = []
        links.append(r.url)
        for t in r.cve.references.reference_data:
            links.append(t.url)
            if 'Exploit' in t.tags:
                exploit_links.append(t.url)
        cpe_for_product_vendors = []
        if cpe_nodes:
            for conf in cve_cpe_nodes:
                if conf.operator == 'AND':
                    children = [conf.children[0]]
                else:
                    children = [conf]
                for child in children:
                    for cpe in child.cpe_match:
                        cpe_for_product_vendors.append(cpe.cpe23Uri)

    #parse CPE--------------------------------------------------------------------------------------------------------------
        product_vendor_list = []
        product_image_list = []
        version_list = []
        for cpe in cpe_for_product_vendors:
            cpe_parsed = CPE(cpe)
            product = cpe_parsed.get_product()
            vendor = cpe_parsed.get_vendor()
            product_vendor = vendor[0] + " " + product[0] if product != vendor else product
            product_vendor_list.append(product_vendor)
            product_image_list.append(product[0])
            version = cpe_parsed.get_version()
            if (version[0] != '-' and version[0] != '*'):
                version_list.append(f'{product[0]} - {version[0]}')

        temp1 = []
        for item in version_list:
            if item not in temp1:
                temp1.append(item)
        versions = []
        for item in temp1:
            ver = {"name": item}
            versions.append(ver)

        prod = []
        for item in product_image_list:
            if item not in prod:
                prod.append(item)

        content = []
        for item in product_vendor_list:
            con = {"name": item}
            content.append(con)

        value = "Да"
        if not exploit_links:
            value = "Нет"

    #check regex in cve-----------------------------------------------------------------------------------------------------
        cve_name = ''
        cve_info = r.cve.description.description_data[0].value
        for item in pattern:
            if item.upper() in cve_info.upper():
                cve_name = cve + " - " + item
                break
            else:
                cve_name = cve
    #message----------------------------------------------------------------------------------------------------------------
        data = {
            'cve': cve_info,
            'lastModifiedDate': r.lastModifiedDate[:-7],
            'publishedDate': r.publishedDate[:-7],
            'configurations': cpe_nodes,
            'score': score,
            'vector': r.v3vector,
            'links': links,
            'product_vendor_list': prod,
            'exploit_links': exploit_links
        }
        message = jinja2.Template(template).render(d=data)

    #check for product_vendor-----------------------------------------------------------------------------------------------
        URL_get_products = config.get("URL_GET_PRODUCTS")
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer {}".format(YOU_TRACK_TOKEN),
            "Content-Type": "application/json"
        }
        data_prod = requests.get(URL_get_products, headers=headers).json()

        upload_prod = []
        for buff in product_vendor_list:
            upload_prod.append(buff)

        prod_vend = []
        for i in data_prod:
            prod_vend.append(i['name'])

        temp = []
        for iter in upload_prod:
            if iter not in prod_vend:
                temp.append(iter)

        for upload in temp:
            payload = {
                "id": "0",
                "&type": "FieldStyle",
                "name": upload
            }
            requests.post(URL_get_products, headers=headers, json=payload)

    # check for versions----------------------------------------------------------------------------------------------------
        URL_get_vetsions = config.get("URL_GET_VERSIONS")
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer {}".format(YOU_TRACK_TOKEN),
            "Content-Type": "application/json"
        }
        data_ver = requests.get(URL_get_vetsions, headers=headers).json()

        ver_list = []
        for i in data_ver:
            ver_list.append(i['name'])

        temp2 = []
        for iter in temp1:
            if iter not in ver_list:
                temp2.append(iter)

        for upload in temp2:
            payload = {
                "id": "0",
                "&type": "FieldStyle",
                "name": upload
            }
            requests.post(URL_get_vetsions, headers=headers, json=payload)

    # upload information on cve---------------------------------------------------------------------------------------------
        request_payload = {
            "project": {
                "id": YOU_TRACK_PROJECT_ID
            },
            "summary": cve_name,
            "description": message,
            "tags": [
                {
                    "name": "Бюллетени НКЦКИ",
                    "id": "6-4",
                    "$type": "IssueTag"
                }
            ],
            "customFields": [
                {
                    "name": "Продукт (пакет)",
                    "$type": "MultiEnumIssueCustomField",
                    "value": content
                },
                {
                    "name": "Есть эксплоит",
                    "$type": "SingleEnumIssueCustomField",
                    "value": {"name": value}
                },
                {
                    "name": "Affected versions",
                    "$type": "MultiEnumIssueCustomField",
                    "value": versions
                },
                {
                    "name": "CVSS Score",
                    "$type": "SimpleIssueCustomField",
                    "value": score

                }
            ]
        }
        #print(request_payload) #Debug
        print(requests.post(URL, headers=headers, json=request_payload).json()) # Выгрузка инфы о cve в YouTrack
    except:
        print(f'no information for {cve}')


if __name__ == "__main__":
    links = get_links_for_bulletine()
    create_pdf_file(links)
    name_list = get_name_list(PATH) # Получение имен скаченных файлов для парсинга
    cve_line = get_cve_list(name_list) # Получение списка cve из биллютеня НКЦКИ

    URL = config.get("URL")
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer {}".format(YOU_TRACK_TOKEN),
        "Content-Type": "application/json"
    }
    list_summary = requests.get(URL, headers=headers).json()  # Получение последних 500 задач с YouTrack
    # Удаление cve, информация о которых уже есть в YouTrack
    sum_list = []
    for n in range(len(list_summary)):
        sum_list.append(list_summary[n]['summary'])

    repeat_list = []
    for item in cve_line:
        for n in sum_list:
            index = n.find(item)
            if index != -1:
                repeat_list.append(item)
    vuln_list = []
    for item in cve_line:
        if item not in repeat_list:
            vuln_list.append(item)

    for cve in vuln_list:
        get_cve_data(cve)

# remove pdf buffer-----------------------------------------------------------------------------------------------------
    time.sleep(5)
    path_to_remove_pdf = []
    for item in name_list:
        path_to_remove_pdf.append(f'{PATH}{item}')
    remove_pdf_file(path_to_remove_pdf)
