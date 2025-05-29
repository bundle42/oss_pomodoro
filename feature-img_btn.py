import streamlit as st
import streamlit.components.v1 as components
import time
from datetime import datetime
import base64

# ===== 🎨 타이머 원형 스타일 =====
TIMER_CSS = """
<style>
.circle{
  width:240px;height:240px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;margin:auto;}
.circle span{font:700 2.2rem monospace;color:#fff}
</style>"""

def draw_circle(remaining, total):
    pct = remaining / total if total > 0 else 0
    angle = pct * 360
    mm, ss = divmod(remaining, 60)

    html = TIMER_CSS + f"""
    <div class="circle"
         style="background:
            conic-gradient(#e74c3c 0deg {angle}deg,
                           #eeeeee {angle}deg 360deg);">
      <span>{mm:02d}:{ss:02d}</span>
    </div>"""
    return html

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ===== 🖼 이미지 버튼 관련 함수 =====
def load_image_base64(file_path):
    with open(file_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def image_button(img_base64, key):
    btn_html = f"""
    <form action="" method="get">
        <button type="submit" name="btn" value="{key}" style="border:none;background:none;">
            <img src="data:image/png;base64,{img_base64}" width="60">
        </button>
    </form>
    """
    components.html(btn_html, height=80)

# ===== 🎨 외부 CSS 적용 =====
local_css("style.css")

# ===== ⏱ 상태 초기화 =====
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
    st.session_state.session_goal = 1

# ===== 🎮 버튼 동작 함수 =====
def handle_start():
    if st.session_state.phase == 'idle':
        st.session_state.remaining_focus = total_focus
        st.session_state.remaining_break = total_break
        st.session_state.session_count = 0
        st.session_state.phase = 'focus'
    st.session_state.running = True

def handle_pause():
    st.session_state.running = False

def handle_reset():
    st.session_state.running = False
    if st.session_state.phase == 'focus':
        st.session_state.remaining_focus = total_focus
    elif st.session_state.phase == 'break':
        st.session_state.remaining_break = total_break

def handle_stop():
    st.session_state.running = False
    st.session_state.phase = 'idle'
    st.session_state.remaining_focus = 0
    st.session_state.remaining_break = 0
    st.session_state.session_count = 0

# ===== ⚙️ 타이머 설정 UI =====
with st.sidebar:
    st.markdown("## 🕒 집중 시간 설정")
    focus_hour = st.number_input("Hours", 0, 10, 0)
    focus_min = st.number_input("Minutes", 0, 59, 0)
    focus_sec = st.number_input("Seconds", 0, 59, 5)

    st.markdown("## 🛌 휴식 시간 설정")
    break_hour = st.number_input("Hours ", 0, 5, 0)
    break_min = st.number_input("Minutes ", 0, 59, 0)
    break_sec = st.number_input("Seconds ", 0, 59, 5)

    st.markdown("## 🔁 세션 반복 설정")
    st.session_state.session_goal = st.number_input("반복할 세션 수", 1, 20, 1)

    st.markdown("## 📝 기록")
    st.markdown(f"🍅 완료된 세션: **{st.session_state.session_count} / {st.session_state.session_goal}**")

# ===== 🔢 시간 계산 =====
total_focus = focus_hour * 3600 + focus_min * 60 + focus_sec
total_break = break_hour * 3600 + break_min * 60 + break_sec

# ===== 🕑 타이머 시각화 =====
st.title("⏳ 뽀모도로 타이머 프로토타입")
st.caption("2025-05-20 필수 기능 구현 by 김민성")

if st.session_state.phase == 'focus':
    components.html(draw_circle(st.session_state.remaining_focus, total_focus), height=260)
elif st.session_state.phase == 'break':
    components.html(draw_circle(st.session_state.remaining_break, total_break), height=260)
else:
    components.html(draw_circle(0, 1), height=260)

# ===== 🖼 이미지 버튼 표시 =====
start_img = load_image_base64("start.png")
pause_img = load_image_base64("pause.png")
reset_img = load_image_base64("reset.png")
stop_img  = load_image_base64("stop.png")

col1, col2, col3, col4 = st.columns(4)
with col1:
    image_button(start_img, "start")
with col2:
    image_button(pause_img, "pause")
with col3:
    image_button(reset_img, "reset")
with col4:
    image_button(stop_img, "stop")

# ===== 🖱 버튼 이벤트 처리 =====
if "btn" in st.query_params:
    btn_val = st.query_params["btn"][0]
    if btn_val == "start":
        handle_start()
    elif btn_val == "pause":
        handle_pause()
    elif btn_val == "reset":
        handle_reset()
    elif btn_val == "stop":
        handle_stop()
    # 이벤트 후 파라미터 초기화
    st.query_params()

# ===== ⏱ 타이머 실행 로직 =====
if st.session_state.running:
    if st.session_state.phase == 'focus' and st.session_state.remaining_focus > 0:
        st.session_state.remaining_focus -= 1
        time.sleep(1)
        st.rerun()

    elif st.session_state.phase == 'focus' and st.session_state.remaining_focus == 0:
        st.toast("집중 완료! 쉬는 시간입니다. 🍅")
        st.session_state.phase = 'break'
        st.rerun()

    elif st.session_state.phase == 'break' and st.session_state.remaining_break > 0:
        st.session_state.remaining_break -= 1
        time.sleep(1)
        st.rerun()

    elif st.session_state.phase == 'break' and st.session_state.remaining_break == 0:
        st.toast("쉬는 시간이 끝났습니다! ⏰")
        st.session_state.session_count += 1

        if st.session_state.session_count >= st.session_state.session_goal:
            st.toast("🎉 모든 세션 완료!", icon="✅")
            time.sleep(1)
            st.session_state.running = False
            st.session_state.phase = 'idle'
        else:
            st.session_state.phase = 'focus'
            st.session_state.remaining_focus = total_focus
            st.session_state.remaining_break = total_break
            st.session_state.running = True
        st.rerun()