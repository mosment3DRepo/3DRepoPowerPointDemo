import streamlit as st
from pptx import Presentation
import requests
import json
import os
from io import BytesIO
from streamlit_cookies_manager import EncryptedCookieManager

st.write("v1.07")

global cookies

cookies = EncryptedCookieManager(
    # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
    password=os.environ.get("COOKIES_PASSWORD", "My secret password"),
)

def get_3dreporisks(domain,teamspace,model,api_key):
    url = domain + "/api/"+teamspace+"/"+model+"/risks?key="+api_key
    headers = {
    'Cookie': 'connect.sid=' + cookies['connect.sid']
    }
    risk_response = requests.get(url, headers=headers)
    risk_response_object = json.loads(risk_response.text)
    return risk_response_object

def get_3drepologin(domain,teamspace,model):
    url = domain + "/api/me"
    headers = {
    'Cookie': 'connect.sid=' + cookies['connect.sid']
    }
    login_response = requests.get(url, headers=headers)
    return login_response.status_code

def insert(domain,teamspace,model,apiKey,output):

    SLD_LAYOUT_TITLE_AND_CONTENT = 0

    prs = Presentation('Template.pptx')
    slide_layout = prs.slide_layouts[SLD_LAYOUT_TITLE_AND_CONTENT]

    risks = get_3dreporisks(domain,teamspace,model,apiKey)

    for risk in risks:
        slide = prs.slides.add_slide(slide_layout)
        name = slide.placeholders[0]
        name.text = risk['name']
        url = slide.placeholders[15]
        urlText = domain + "/viewer/" + teamspace + "/" + model + "?risk=" + risk['_id']
        url.text = urlText
        try:
            desc = slide.placeholders[13]
            desc.text = risk['desc']
            image = slide.placeholders[14]
        except:
            continue
        try:
            imageLocation = domain + "/api/" + risk['viewpoint']['screenshot'] + "?key=" + apiKey
            imageGet = requests.get(imageLocation)
            file = open("temp.png", "wb")
            file.write(imageGet.content)
            file.close()
            image.insert_picture("temp.png")
        except:
            continue
        try:
            os.remove("temp.png")
        except:
            continue
    fileName = output + '.pptx'
    outputFile = BytesIO()
    prs.save(outputFile)
    outputFile.seek(0)

    st.download_button(
        label="Download data as Powerpoint",
        data=outputFile,
        file_name=fileName
    )

if not cookies.ready():
    # Wait for the component to load and send us current cookies.
    st.stop()

st.write("Current cookies:", cookies['connect.sid'])

login_response = get_3drepologin
login_response_success = login_response == 200


st.header("3D Repo Safetibase PowerPoint App")
st.text("Insert your Model/Federation details below to generate a Powerpoint file of all the Risks")

teamspace = st.text_input("Teamspace:")
model = st.text_input("Model:")

if not login_response_success:
    apiKey = st.text_input("API Key:")
else:
    apiKey = ''

domain = st.text_input("Domain:", value="https://www.3drepo.io")
output = st.text_input("Output File Name:", value = "3D Repo Safetibase Export")

if st.button("Submit"):
    insert(domain,teamspace,model,apiKey,output)

