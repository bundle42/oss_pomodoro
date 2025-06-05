import streamlit as st
import streamlit.components.v1 as components
import time
import json
import os
from datetime import datetime, timedelta
import numpy as np

# ===== 🎨 타이머 원형 스타일 =====
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
    html = TIMER_CSS+f"""
    <div class="circle"
         style="background:
            conic-gradient(#e74c3c 0deg {angle}deg,
                           #eeeeee {angle}deg 360deg);">
      <span>{mm:02d}:{ss:02d}</span>
    </div>"""
    return html

# ===== JSON 저장 관련 =====
DATA_PATH = "user_sessions.json"

# 세션 결과 저장
def save_session_result(duration_minutes):
    today_str = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []

    today_entry = next((d for d in data if d["date"] == today_str), None)
    if not today_entry:
        today_entry = {
            "date": today_str,
            "sessions": [],
            "daily_review": "",
            "addition_time": None
        }
        data.append(today_entry)

    session_number = len(today_entry["sessions"]) + 1
    today_entry["sessions"].append({
        "session_number": session_number,
        "duration_minutes": duration_minutes
    })

    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 리뷰 업데이트
def update_review(date_str, review, add_time):
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
    else:
        return

    for entry in data:
        if entry["date"] == date_str:
            entry["daily_review"] = review
            entry["addition_time"] = add_time
            break

    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 자동 추천시간 설정
def calculate_adjusted_focus():
    if not os.path.exists(DATA_PATH):
        return None

    with open(DATA_PATH, "r") as f:
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
    return int((mean + std) * 60)  # 초로 반환

# ===== Streamlit 상태 초기화 =====
if 'phase' not in st.session_state:
    st.session_state.phase = 'idle'
if 'running' not in st.session_state:
    st.session_state.running = False
if 'remaining_focus' not in st.session_state:
    st.session_state.remaining_focus = 0
if 'remaining_break' not in st.session_state:
    st.session_state.remaining_break = 0
if 'session_count' not in st.session_state:
    st.session_state.session_count = 0
if 'session_goal' not in st.session_state:
    st.session_state.session_goal = 3
if 'adjusted_focus' not in st.session_state:
    st.session_state.adjusted_focus = calculate_adjusted_focus() or 1500

# ===== ⚙️ 타이머 설정 UI (기본값에 조정값 반영) =====
with st.sidebar:
    adjusted_focus_sec = st.session_state.adjusted_focus or 1500
    adj_focus_h, rem = divmod(adjusted_focus_sec, 3600)
    adj_focus_m, adj_focus_s = divmod(rem, 60)

    st.markdown("## ♣ 집중 시간 설정")
    focus_hour = st.number_input("Hours", 0, 10, int(adj_focus_h), key="focus_hour")
    focus_min = st.number_input("Minutes", 0, 59, int(adj_focus_m), key="focus_min")
    focus_sec = st.number_input("Seconds", 0, 59, int(adj_focus_s), key="focus_sec")

    if st.session_state.adjusted_focus:
        st.sidebar.markdown(f"📊 추천 집중시간: {st.session_state.adjusted_focus // 60}분")

    st.markdown("## 🛌 휴식 시간 설정")
    break_hour = st.number_input("Hours ", 0, 5, 0)
    break_min = st.number_input("Minutes ", 0, 59, 0)
    break_sec = st.number_input("Seconds ", 0, 59, 3)

    st.markdown("## 🔁 세션 반복 설정")
    st.session_state.session_goal = st.number_input("반복할 세션 수", 1, 20, 3)

    st.markdown("## 📝 기록")
    st.markdown(f"🍅 완료된 세션: **{st.session_state.session_count} / {st.session_state.session_goal}**")

# ===== 🔢 시간 계산 =====
total_focus = focus_hour * 3600 + focus_min * 60 + focus_sec
total_break = break_hour * 3600 + break_min * 60 + break_sec

if st.session_state.running is False and st.session_state.phase == 'idle':
    st.session_state.adjusted_focus = total_focus

st.title("⏳ 뽀모도로 타이머")
st.caption("2025-06-05 추천 집중시간 기능 구현 by 김민성")

col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
with col_btn1:
    if st.button("▶️ 타이머 시작"):
        if st.session_state.phase == 'idle':
            st.session_state.remaining_focus = st.session_state.adjusted_focus
            st.session_state.remaining_break = total_break
            st.session_state.session_count = 0
            st.session_state.phase = 'focus'
        st.session_state.running = True
with col_btn2:
    if st.button("⏸️ 일시정지"):
        st.session_state.running = False
        used = st.session_state.adjusted_focus - st.session_state.remaining_focus
        save_session_result(used // 60)
with col_btn3:
    if st.button("🔄 현재 세션 초기화"):
        st.session_state.running = False
        st.session_state.remaining_focus = st.session_state.adjusted_focus
with col_btn4:
    if st.button("⏹️ 타이머 중지"):
        st.session_state.running = False
        st.session_state.phase = 'idle'
        st.session_state.remaining_focus = 0
        st.session_state.remaining_break = 0
        st.session_state.session_count = 0

# ===== 타이머 실행 =====
if st.session_state.running:
    if st.session_state.phase == 'focus' and st.session_state.remaining_focus > 0:
        st.session_state.remaining_focus -= 1
        components.html(draw_circle(st.session_state.remaining_focus, total_focus), height=260)
        time.sleep(1)
        st.rerun()
    elif st.session_state.phase == 'focus' and st.session_state.remaining_focus == 0:
        st.toast("집중 완료! 쉬는 시간입니다. 🍅")
        st.session_state.phase = 'break'
        st.rerun()
    elif st.session_state.phase == 'break' and st.session_state.remaining_break > 0:
        st.session_state.remaining_break -= 1
        components.html(draw_circle(st.session_state.remaining_break, total_break), height=260)
        time.sleep(1)
        st.rerun()
    elif st.session_state.phase == 'break' and st.session_state.remaining_break == 0:
        st.toast("쉬는 시간이 끝났습니다! ⏰")
        st.session_state.session_count += 1
        used = st.session_state.adjusted_focus - st.session_state.remaining_focus
        save_session_result(used // 60)

        if st.session_state.session_count >= st.session_state.session_goal:
            st.toast("🎉 모든 세션 완료!", icon="✅")
            st.session_state.running = False
            st.session_state.phase = 'idle'
        else:
            st.session_state.phase = 'focus'
            st.session_state.remaining_focus = st.session_state.adjusted_focus
            st.session_state.remaining_break = total_break
            st.session_state.running = True
        st.rerun()
else:
    if st.session_state.phase == 'focus':
        components.html(draw_circle(st.session_state.remaining_focus, total_focus), height=260)
    elif st.session_state.phase == 'break':
        components.html(draw_circle(st.session_state.remaining_break, total_break), height=260)
    elif st.session_state.phase == 'idle':
        components.html(draw_circle(total_focus, total_focus), height=260)

# ===== 📝 리뷰 입력 =====
today_str = datetime.now().strftime("%Y-%m-%d")
if st.session_state.phase == 'idle' and st.session_state.session_count >= st.session_state.session_goal:
    with st.form("daily_review_form", clear_on_submit=True):
        st.markdown("### 오늘 집중은 어땠나요?")
        review_text = st.text_area("📝 리뷰 작성")
        addition_time = st.number_input("오늘 추가로 집중할 수 있는 시간 (분)", min_value=0, step=1)
        submitted = st.form_submit_button("등록")
        if submitted:
            update_review(today_str, review_text, addition_time)
            st.success("등록 완료!")

