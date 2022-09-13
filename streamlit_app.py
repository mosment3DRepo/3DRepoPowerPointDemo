import streamlit as st
from pptx import Presentation
import requests
import json
import os
from io import BytesIO

teamspace = st.text_input("Teamspace:")
model = st.text_input("Model:")
apiKey = st.text_input("API Key:")
domain = st.text_input("Domain:")
output = st.text_input("Output File Name:")

def get_3dreporisks(domain,teamspace,model,api_key):
    risk_response = requests.get(domain + "/api/"+teamspace+"/"+model+"/risks?key="+api_key)
    risk_response_object = json.loads(risk_response.text)
    return risk_response_object

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


if st.button("Submit"):
    insert(domain,teamspace,model,apiKey,output)

