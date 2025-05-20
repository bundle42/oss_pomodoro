import streamlit as st
import streamlit.components.v1 as components
import time

# style 및 div는 디자인 부분
TIMER_CSS = """
<style>
.circle{
  width:240px;height:240px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;margin:auto;}
.circle span{font:700 2.2rem monospace;color:#fff}
</style>"""

def draw_circle(remaining, total):
    pct = remaining / total                 
    angle = pct * 360                       
    mm, ss = divmod(remaining, 60)
    timer = f"{mm:02d}:{ss:02d}"

    html = TIMER_CSS+f"""
    <div class="circle"
         style="background:
            conic-gradient(#e74c3c 0deg {angle}deg,
                           #eeeeee {angle}deg 360deg);">
      <span>{mm:02d}:{ss:02d}</span>
    </div>"""
    return html

# style 설정
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

#---------------------------------#

# 좌측 사이드바()
st.sidebar.title("타이머 기록")

# 메인
st.write("""
# 뽀모도로 프로토타입(앱이름)

2025-05-20 뽀모도로 타이머 필수 기능 구현
         
1. 시, 분, 초 설정
1.1 타이머 시작, 타이머 중지, 타이머 초기화 설정
2. 반복 설정
3. 좌측 사이드바에 집중 성공시 기록 됨

Developed by: [Data Professor](http://youtube.com/dataprofessor)

Modified by: 김민성, 김민수, 박재락, 이관훈 

""")

# 필수 기능 부분
st.subheader("🕒 Focus Time 설정")
col1, col2, col3 = st.columns(3)
with col1:
    focus_hour = st.number_input("Hours", 0, 10, 0)
with col2:
    focus_min = st.number_input("Minutes", 0, 59, 1)
with col3:
    focus_sec = st.number_input("Seconds", 0, 59, 0)

st.subheader("🛌 Break Time 설정")
col4, col5, col6 = st.columns(3)
with col4:
    break_hour = st.number_input("Hours ", 0, 5, 0)
with col5:
    break_min = st.number_input("Minutes ", 0, 59, 0)
with col6:
    break_sec = st.number_input("Seconds ", 0, 59, 10)

st.write("") # 여백

# 타이머 버튼
col1, col2, col3 = st.columns(3)
with col1:
    btn_start = st.button("타이머 시작")
with col2:
    btn_stop = st.button("타이머 중지")
with col3:
    btn_reset = st.button("타이머 초기화")


# 초 단위로 변환
t1 = focus_hour * 3600 + focus_min * 60 + focus_sec
t2 = break_hour * 3600 + break_min * 60 + break_sec

if btn_start:
    container=st.empty()
    for t in range(t1, -1,-1):
        with container:
            components.html(draw_circle(t, t1), height=260, scrolling=False)
        time.sleep(1)
    st.toast("🔔 Focus complete! Time for a break.", icon="🍅") # 우측 상단에 알림

    for t in range(t2, -1, -1):
        with container:
            components.html(draw_circle(t, t2), height=260, scrolling=False)
        time.sleep(1)
    st.toast("⏰ Break is over!", icon="⏰") # 알림 후 타이머 종료됨

# 추가 기능 부분(이관훈)