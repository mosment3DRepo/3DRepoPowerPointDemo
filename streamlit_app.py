import os
import requests
import json
from io import BytesIO

import streamlit as st
from streamlit.web.server import Server

from pptx import Presentation
import extra_streamlit_components as stx

if "DEPLOY_TAG" in os.environ:
    st.write(os.environ["DEPLOY_TAG"])

@st.cache(allow_output_mutation=True)
def get_manager():
    return stx.CookieManager()

def get_3dreporisks(domain,teamspace,model,api_key):
    if connectsid:
        url = domain + "/api/"+teamspace+"/"+model+"/risks"
        cookie = {
            'connect.sid' : connectsid,
        }
        curSession = requests.Session() 
        risk_response = curSession.get(url, cookies=cookie)
    else:
        url = domain + "/api/"+teamspace+"/"+model+"/risks?" + needKey()
        curSession = requests.Session() 
        risk_response = curSession.get(url)

    risk_response_object = json.loads(risk_response.text)
    return risk_response_object

def get_3drepologin(domain, connectsid):
    url = domain + "/api/me"
    cookie = {
        'connect.sid' : connectsid,
    }
    curSession = requests.Session() 
    login_response = curSession.get(url, cookies=cookie)
    return login_response

def insert(domain,teamspace,model,apiKey,output):

    if not teamspace and model:
        return False
        
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
            imageLocation = domain + "/api/" + risk['viewpoint']['screenshot'] + needKey()
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

connectsid = ''
domain = st.text_input("Domain:", value="https://staging.dev.3drepo.io")
output = st.text_input("Output File Name:", value = "3D Repo Safetibase Export")

def needKey():
    if not login_response_success:
        return "?key=" + apiKey
    else:
        return ""

if not st.experimental_user.email == 'test@localhost.com':
    connectsid = st.experimental_user.email
    login_response = get_3drepologin(domain,connectsid)
    # results = json.load(login_response.json())
    login_response_success = login_response.status_code == 200

if not login_response_success:
    apiKey = st.text_input("API Key:")
else:
    st.text("Logged in as : " + login_response.json()['username'])
    apiKey = ''

st.header("3D Repo Safetibase PowerPoint App")
st.text("Insert your Model/Federation details below to generate a Powerpoint file of all the Risks")

teamspace = st.text_input("Teamspace:")
model = st.text_input("Model:")

if st.button("Submit"):
    insert(domain,teamspace,model,apiKey,output)

