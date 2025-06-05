# pomodoro-app(K Team)

# Watch the tutorial video

[Let's Build a Pomodoro Web App for Data Science | Streamlit #15](https://youtu.be/9a234-OvbIQ)

<a href="https://youtu.be/9a234-OvbIQ"><img src="http://img.youtube.com/vi/9a234-OvbIQ/0.jpg" alt="Let's Build a Pomodoro Web App for Data Science | Streamlit #15" title="Let's Build a Pomodoro Web App for Data Science | Streamlit #15" width="400" /></a>

:star:

# 자동 시간 추천
user_sessions.json이 없으면?	기본값 1500초 (25분)이 사용됨 ? 의도된 동작임
JSON에 오늘 날짜만 있으면?	표본이 너무 적어서 추천값이 부정확할 수 있음
너무 짧거나 긴 시간만 저장돼 있으면?	표준편차에 따라 추천시간이 왜곡될 수 있음 (극단값 보정이 없음)
집중 시간 0분은 계산에서 제외하였음

# Demo

Launch the web app:

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/dataprofessor/pomodoro-app/main/app.py)

# Reproducing this web app
To recreate this web app on your own computer, do the following.

### Create conda environment
Firstly, we will create a conda environment called *pomodoro*
```
conda create -n pomodoro python=3.7.9
```
Secondly, we will login to the *pomodoro* environement
```
conda activate pomodoro
```
### Install prerequisite libraries

Download requirements.txt file

```
wget https://raw.githubusercontent.com/dataprofessor/pomodoro-app/main/requirements.txt

```

Pip install libraries
```
pip install -r requirements.txt
```
###  Download and unzip contents from GitHub repo

Download and unzip contents from https://github.com/dataprofessor/pomodoro-app/archive/main.zip

###  Launch the app

```
streamlit run app.py
```
