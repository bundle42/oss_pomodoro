import streamlit as st
import streamlit.components.v1 as components
import time
import json
import os
from datetime import datetime, timedelta
import numpy as np



# 🔧 CSS 연결 함수
def load_local_css(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

# 페이지 설정
st.set_page_config(page_title="Pomodoro Timer", layout="centered")
load_local_css("원형타이머.css")  

# 타이틀
st.markdown("""
<div style='position: absolute; top: 10px; left: 50px; font-size: 35px; 
            font-weight: bold; line-height: 1.4;'>
    Statistically Adaptive Pomodoro Timer
</div>
""", unsafe_allow_html=True)
st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)



#원형 타이머
def draw_circle(remaining, total):
    hh, rem = divmod(remaining, 3600)
    mm, ss = divmod(rem, 60)
    pct = remaining / total if total > 0 else 0
    radius = 108 * 1.2
    size = int(240 * 1.2)
    cx = cy = size // 2
    circumference = 2 * 3.1416 * radius

    is_break = st.session_state.phase == "break"
    gradient_id = "grad_break" if is_break else "grad_focus"
    text_color = "#1a661a" if is_break else "#003366"

    html = f"""
    <div style="position: relative; width: {size}px; height: {size}px; margin: 0 auto;">
      <svg width="{size}" height="{size}" style="position: absolute; top: 0; left: 0; z-index: 1;">
        <circle
          r="{radius}" cx="{cx}" cy="{cy}"
          fill="transparent"
          stroke="#ddd"
          stroke-width="8"
        />
        <circle
          r="{radius}" cx="{cx}" cy="{cy}"
          fill="transparent"
          stroke="url(#{gradient_id})"
          stroke-width="8"
          stroke-linecap="round"
          stroke-dasharray="{circumference}"
          stroke-dashoffset="{circumference * (1 - pct)}"
          transform="rotate(-90 {cx} {cy})"
          style="transition: stroke-dashoffset 0.5s linear;"
        />
        <defs>
          <linearGradient id="grad_focus" x1="1" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#3399ff"/>
            <stop offset="50%" stop-color="#003366"/>
            <stop offset="100%" stop-color="#001a33"/>
          </linearGradient>
          <linearGradient id="grad_break" x1="1" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#66cc66"/>
            <stop offset="50%" stop-color="#339933"/>
            <stop offset="100%" stop-color="#1a661a"/>
          </linearGradient>
        </defs>
      </svg>
      <div style="
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          font-size: 42px;
          font-weight: 300;
          color: {text_color};
          z-index: 2;
          user-select: none;
          text-align: center;
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          ">
          {hh:02d} : {mm:02d} : {ss:02d}
      </div>
    </div>
    """
    return html

# 🔐 JSON 저장 위치
DATA_PATH = "user_sessions.json"

def save_session_result(duration_minutes):
    if duration_minutes < 1:
        return
    today_str = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    today_entry = next((d for d in data if d["date"] == today_str), None)
    if not today_entry:
        today_entry = {"date": today_str, "sessions": [], "daily_review": "", "addition_time": None}
        data.append(today_entry)

    session_number = len(today_entry["sessions"]) + 1
    today_entry["sessions"].append({"session_number": session_number, "duration_minutes": duration_minutes})

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_review(date_str, review, add_time):
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    for entry in data:
        if entry["date"] == date_str:
            entry["daily_review"] = review
            entry["addition_time"] = add_time
            break
    else:
        data.append({"date": date_str, "sessions": [], "daily_review": review, "addition_time": add_time})

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def calculate_adjusted_focus():
    if not os.path.exists(DATA_PATH):
        return None

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    two_weeks_ago = datetime.now() - timedelta(days=14)
    durations = []
    for entry in data:
        entry_date = datetime.strptime(entry["date"], "%Y-%m-%d")
        if two_weeks_ago <= entry_date < datetime.now():
            durations.extend([s["duration_minutes"] for s in entry["sessions"] if s["duration_minutes"] > 0])

    if not durations:
        return None

    mean = np.mean(durations)
    std = np.std(durations)
    return int((mean + std) * 60)

# 세션 상태 초기화
if 'phase' not in st.session_state: st.session_state.phase = 'idle'
if 'running' not in st.session_state: st.session_state.running = False
if 'remaining_focus' not in st.session_state: st.session_state.remaining_focus = 0
if 'remaining_break' not in st.session_state: st.session_state.remaining_break = 0
if 'session_count' not in st.session_state: st.session_state.session_count = 0
if 'session_goal' not in st.session_state: st.session_state.session_goal = 3
if 'adjusted_focus' not in st.session_state:
    st.session_state.adjusted_focus = calculate_adjusted_focus() or 1500

# 타이머 설정 UI
with st.sidebar:
    adjusted_focus_sec = st.session_state.adjusted_focus
    adj_focus_h, rem = divmod(adjusted_focus_sec, 3600)
    adj_focus_m, adj_focus_s = divmod(rem, 60)

    st.markdown("##  집중 시간 설정")
    focus_hour = st.number_input("Hours", 0, 10, int(adj_focus_h), key="focus_hour")
    focus_min = st.number_input("Minutes", 0, 59, int(adj_focus_m), key="focus_min")
    focus_sec = st.number_input("Seconds", 0, 59, int(adj_focus_s), key="focus_sec")

    if st.session_state.adjusted_focus:
        st.markdown(f" 추천 집중시간: {st.session_state.adjusted_focus // 60}분")

    st.markdown("## 휴식 시간 설정")
    break_hour = st.number_input("Hours ", 0, 5, 0)
    break_min = st.number_input("Minutes ", 0, 59, 0)
    break_sec = st.number_input("Seconds ", 0, 59, 3)

    st.markdown("## 세션 반복 설정")
    st.session_state.session_goal = st.number_input("반복할 세션 수", 1, 20, 3)

    st.markdown("## 기록")
    st.markdown(f" 완료된 세션: **{st.session_state.session_count} / {st.session_state.session_goal}**")

# 시간 계산
total_focus = focus_hour * 3600 + focus_min * 60 + focus_sec
total_break = break_hour * 3600 + break_min * 60 + break_sec
if not st.session_state.running and st.session_state.phase == 'idle':
    st.session_state.adjusted_focus = total_focus

# 타이머 표시
if st.session_state.phase == 'focus':
    components.html(draw_circle(st.session_state.remaining_focus, total_focus), height=310)
elif st.session_state.phase == 'break':
    components.html(draw_circle(st.session_state.remaining_break, total_break), height=310)
else:
    components.html(draw_circle(total_focus, total_focus), height=310)

# 버튼 
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([1, 1, 1, 1])

with col_btn1:
    if st.button("START"):
        if st.session_state.phase == 'idle':
            st.session_state.remaining_focus = st.session_state.adjusted_focus
            st.session_state.remaining_break = total_break
            st.session_state.session_count = 0
            st.session_state.phase = 'focus'
        st.session_state.running = True

with col_btn2:
    if st.button("PAUSE"):
        st.session_state.running = False
        used = st.session_state.adjusted_focus - st.session_state.remaining_focus
        save_session_result(used // 60)

with col_btn3:
    if st.button("RESET"):
        st.session_state.running = False
        st.session_state.remaining_focus = st.session_state.adjusted_focus

with col_btn4:
    if st.button("STOP"):
        st.session_state.running = False
        st.session_state.phase = 'idle'
        st.session_state.remaining_focus = 0
        st.session_state.remaining_break = 0
        st.session_state.session_count = 0

if st.session_state.running:
    if st.session_state.phase == 'focus':
        if st.session_state.remaining_focus > 0:
            st.session_state.remaining_focus -= 1
            time.sleep(1)
            st.rerun()
        else:
            st.toast("집중 완료! 쉬는 시간입니다.")
            st.session_state.phase = 'break'
            st.rerun()

    elif st.session_state.phase == 'break':
        if st.session_state.remaining_break > 0:
            st.session_state.remaining_break -= 1
            time.sleep(1)
            st.rerun()
        else:
            st.toast("쉬는 시간이 끝났습니다!")
            st.session_state.session_count += 1

            used = st.session_state.adjusted_focus - st.session_state.remaining_focus
            save_session_result(used // 60)

            if st.session_state.session_count >= st.session_state.session_goal:
                st.toast(" 모든 세션 완료!", icon="✅")
                st.session_state.running = False
                st.session_state.phase = 'idle'
            else:
                st.session_state.phase = 'focus'
                st.session_state.remaining_focus = st.session_state.adjusted_focus
                st.session_state.remaining_break = total_break
                st.session_state.running = True

            st.rerun()

# 리뷰 입력
if st.session_state.phase == 'idle' and st.session_state.session_count >= st.session_state.session_goal:
    with st.form("daily_review_form", clear_on_submit=True):
        st.markdown("### 오늘 집중은 어땠나요?")
        review_text = st.text_area("리뷰 작성")
        addition_time = st.number_input("오늘 추가로 집중할 수 있는 시간 (분)", min_value=0, step=1)
        submitted = st.form_submit_button("저장")

        if submitted:
            today_str = datetime.now().strftime("%Y-%m-%d")
            update_review(today_str, review_text, addition_time)
            st.success("리뷰가 저장되었습니다.")
