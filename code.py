import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi # youtube transcript fetch
import google.generativeai as genai
from dotenv import load_dotenv
from urllib.parse import urlparse,parse_qs #break url in parts
import os

#api
load_dotenv() # file read
api_key=os.getenv("GOOGLE_API_KEY")# read api key

# gemini configure 
genai.configure(api_key=api_key)
model=genai.GenerativeModel("gemini-2.5-flash")

#web design
st.set_page_config(layout='wide')
st.markdown("""
<h1 style='text-align:center;'>
Youtube Video Summarizer </h1>""",unsafe_allow_html=True)

#input
youtube_link=st.text_input("Enter Your Youtube URL")

language=st.selectbox("Transcript Language",['English','Hindi'])
summary_language=st.selectbox("Select Summary Language",['English','Hindi'])

summary_length=st.selectbox("Summay Length",["Short",'Medium','Detailed'])

#transcript

if youtube_link:
    
    parsed_url = urlparse(youtube_link)

    if "youtu.be" in parsed_url.netloc: # this link is youtube shorts or not? check
        
        video_id = parsed_url.path.strip("/") # remove this/
         
    elif "youtube.com" in parsed_url.netloc: # check normal youtube link
        if "/shorts/" in parsed_url.path:
            video_id=parsed_url.path.split('/shorts/')[1].split("?")[0]
        else:
            video_id = parse_qs(parsed_url.query).get("v")
            video_id = video_id[0] if video_id else None
    else:
        video_id = None

    if video_id:
        st.success(f"Video ID: {video_id}")
        st.video(youtube_link)

# transcript video in hindi or english language
        if st.button("Get Transcript"):
            ytt_api=YouTubeTranscriptApi()
            try :
                transscript=ytt_api.fetch(video_id,languages=['en']).to_raw_data()
            except:
                transscript=ytt_api.fetch(video_id,languages=['hi']).to_raw_data()
            text=" ".join([item['text'] for item in transscript])
            st.session_state.text=text
            st.subheader("Transcript")
            st.write(text)
            
#Youtube  video summary
        if st.button("Generate Summary"):
            if "text" in st.session_state:
                prompt=(f""" you are an AII assistant.
                         Read the following youtube transcript and generate a summary in{summary_language}{summary_length}
                         requirements:
                         -Maximum 10 bullet points
                         -use simple language.
                         -Mention important concepts
                        -Ignore greeting and promotions
                    
                        Transcript:
                        {st.session_state.text}""")
                with st.spinner("Generating Summary..."):
                    response=model.generate_content(prompt)
                st.subheader("summary")
                st.write(response.text)
            else:
                st.warning("Please click get transcript first ")

# Generate quiz related to youtube video
        if st.button("Generate Quiz"):
            if "text" in st.session_state:
                quiz_prompt=(f""" 
                            You are an AI quiz generator.
                            Based on the following youtube transcript,generate 5 multiple-choice questions.
                            Return ONLY in the following format:
                            Do NOT use markdown.
                            Do NOT use bullet points
                            Do NOT use Tables.
                            Do NOT use headings(#,##).
                             
                            Q1.Question text here
                            A. option 1
                            B. option 2
                            C. option 3
                            D. option 4
                            Correct Answer B
                            ---------------------------------------
                            Q2. Question text here
                            A. option 1
                            B. option 2
                            C. option 3
                            D. option 4
                            Correct Answer C
                            Rules:
                            -Each questions must be clearly separarted
                            -option must be on separate lines
                            -Always write answer on new line
                             -Do not write everything in one line
            
                
                            Transcript:
                            {st.session_state.text}""")
                quiz_response=model.generate_content(quiz_prompt)
                st.subheader("Quiz")
                quiz = quiz_response.text

                quiz = quiz.replace("A.", "\nA.")
                quiz = quiz.replace("B.", "\nB.")
                quiz = quiz.replace("C.", "\nC.")
                quiz = quiz.replace("D.", "\nD.")
                quiz = quiz.replace("Correct Answer", "\nCorrect Answer")

                st.write(quiz)
            else:
                st.warning("Please click get transcript first")

    else:
        st.error("Invalid YouTube URL")







