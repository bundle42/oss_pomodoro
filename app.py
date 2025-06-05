import streamlit as st
import streamlit.components.v1 as components
import time
from datetime import datetime
import base64

# ===== 🎨 타이머 원형 스타일 =====
# CSS
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

# # ===== 🖼 이미지 버튼 관련 함수 =====
# def load_image_base64(file_path):
#     with open(file_path, "rb") as img_file:
#         return base64.b64encode(img_file.read()).decode()

# def image_button(img_base64, key):
#     btn_html = f"""
#     <form action="" method="get">
#         <button type="submit" name="btn" value="{key}" style="border:none;background:none;">
#             <img src="data:image/png;base64,{img_base64}" width="60">
#         </button>
#     </form>
#     """
#     components.html(btn_html, height=80)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

# 상태 관리
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

# === 세션 기록 및 자동 조정용 상태 ===
if 'session_history' not in st.session_state:
    st.session_state.session_history = []

if 'adjusted_focus' not in st.session_state:
    st.session_state.adjusted_focus = None
if 'adjusted_break' not in st.session_state:
    st.session_state.adjusted_break = None

# 동작 함수
def handle_start():
    if st.session_state.phase == 'idle':
        st.session_state.remaining_focus = st.session_state.adjusted_focus or total_focus
        st.session_state.remaining_break = st.session_state.adjusted_break or total_break
        st.session_state.session_count = 0
        st.session_state.phase = 'focus'
    st.session_state.running = True

def handle_pause():
    st.session_state.running = False

    # 다음 세션 시간만 줄이고, 이번 세션은 그대로
    st.session_state.adjusted_focus = max(st.session_state.remaining_focus - 60, 1)
    st.session_state.adjusted_break = total_break

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

base_focus_time = 5

# ===== ⚙️ 타이머 설정 UI (기본값에 조정값 반영) =====
with st.sidebar:
    adjusted_focus_sec = st.session_state.adjusted_focus or base_focus_time
    adj_focus_h, rem = divmod(adjusted_focus_sec, 3600)
    adj_focus_m, adj_focus_s = divmod(rem, 60)

    focus_hour = st.number_input("Hours", 0, 10, int(adj_focus_h), key="focus_hour")
    focus_min = st.number_input("Minutes", 0, 59, int(adj_focus_m), key="focus_min")
    focus_sec = st.number_input("Seconds", 0, 59, int(adj_focus_s), key="focus_sec")

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

# 사용자가 수동으로 조정했을 경우 → 자동 조정값을 무시
if st.session_state.running is False and st.session_state.phase == 'idle':
    st.session_state.adjusted_focus = total_focus
    st.session_state.adjusted_break = total_break

# ===== 🕑 타이머 시각화 =====
st.title("⏳ 뽀모도로 타이머 프로토타입")
st.caption("2025-05-20 필수 기능 구현 by 김민성")

# # 버튼 영역
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
with col_btn1:
    if st.button("▶️ 타이머 시작"):
        handle_start()
with col_btn2:
    if st.button("⏸️ 일시정지"):
        handle_pause()
with col_btn3:
    if st.button("🔄 현재 세션 초기화"):
        handle_reset()
with col_btn4:
    if st.button("⏹️ 타이머 중지"):
        handle_stop()

# ===== 🖱 버튼 이벤트 처리 =====
query_params = st.query_params

if "btn" in query_params:
    btn_val = query_params["btn"][0]
    if btn_val == "start":
        handle_start()
    elif btn_val == "pause":
        handle_pause()
    elif btn_val == "reset":
        handle_reset()
    elif btn_val == "stop":
        handle_stop()

    # 쿼리 파라미터 초기화
    st.query_params.clear()  # 또는 update({})
    st.rerun()

# 타이머 실행
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

        # ✅ 세션 성공 여부 판단
        session_success = st.session_state.remaining_focus <= 5
        st.session_state.session_history.append({
            'success': session_success
        })

        # ✅ 성공이면 다음 세션 시간 +1분
        if session_success:
            st.session_state.adjusted_focus = st.session_state.adjusted_focus + 60

        if st.session_state.session_count >= st.session_state.session_goal:
            st.toast("🎉 모든 세션 완료!", icon="✅")
            time.sleep(1)
            st.session_state.running = False
            st.session_state.phase = 'idle'
        else:
            st.session_state.phase = 'focus'
            st.session_state.remaining_focus = st.session_state.adjusted_focus or total_focus  # 자동 조정 반영
            st.session_state.remaining_break = total_break
            st.session_state.running = True
        st.rerun()
else:
    # 정지 상태에서 타이머 보여주기
    if st.session_state.phase == 'focus':
        components.html(draw_circle(st.session_state.remaining_focus, total_focus), height=260)
    elif st.session_state.phase == 'break':
        components.html(draw_circle(st.session_state.remaining_break, total_break), height=260)
    elif st.session_state.phase == 'idle':
        # 시작 전에도 입력한 "집중시간" 기준 원형 표시
        if total_focus > 0:
            components.html(draw_circle(total_focus, total_focus), height=260)
        else:
            components.html(draw_circle(0, 1), height=260)
