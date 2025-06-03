import streamlit as st
import streamlit.components.v1 as components
import time
from datetime import datetime
import base64

# ===== 🎨 타이머 원형 스타일 및 버튼 스타일 통합 =====
# CSS
GLOBAL_CSS = """
<style>
/* 타이머 원형 스타일 */
.circle{
  width:240px;height:240px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;margin:auto;}
.circle span{font:700 2.2rem monospace;color:#fff}

/* Streamlit 버튼을 위한 커스텀 CSS */
div.stButton > button {
    /* 기본 스타일 */
    font-size: 18px;
    font-weight: bold;
    padding: 12px 28px; /* 패딩 증가 */
    border: 2px solid; /* 테두리 추가 */
    border-radius: 12px; /* 모서리 더 둥글게 */
    margin: 8px;
    cursor: pointer;
    transition: all 0.3s ease-in-out; /* 모든 변화에 부드러운 전환 */
    width: 100%; /* 컬럼 너비에 꽉 차게 */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* 부드러운 그림자 */
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1); /* 텍스트 그림자 */
}

/* 호버 효과 */
div.stButton > button:hover {
    transform: translateY(-4px) scale(1.02); /* 살짝 위로 이동하고 커짐 */
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3); /* 그림자 더 진하게 */
    filter: brightness(1.1); /* 살짝 밝아지게 */
}

/* 클릭 효과 */
div.stButton > button:active {
    transform: translateY(0) scale(1.0); /* 원래 위치로 돌아오며 크기 복원 */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15); /* 그림자 약하게 */
}


/* 각 버튼별 스타일 (그라데이션 및 색상) - nth-of-type으로 순서대로 지정 */

/* 타이머 시작 버튼 */
div.stButton > button:nth-of-type(1) {
    background: linear-gradient(135deg, #007bff, #0056b3); /* 파란색 그라데이션 */
    color: white;
    border-color: #004085;
}

/* 일시정지 버튼 */
div.stButton > button:nth-of-type(2) {
    background: linear-gradient(135deg, #ffc107, #e0a800); /* 노란색 그라데이션 */
    color: #333; /* 어두운 텍스트 색상 */
    border-color: #cc9900;
}

/* 타이머 초기화 버튼 */
div.stButton > button:nth-of-type(3) {
    background: linear-gradient(135deg, #17a2b8, #138496); /* 청록색 그라데이션 */
    color: white;
    border-color: #0f6674;
}

/* 타이머 중지 버튼 */
div.stButton > button:nth-of-type(4) {
    background: linear-gradient(135deg, #dc3545, #c82333); /* 빨간색 그라데이션 */
    color: white;
    border-color: #a71d2a;
}
</style>
"""

# GLOBAL_CSS를 Streamlit 앱에 주입
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def draw_circle(remaining, total):
    pct = remaining / total
    angle = pct * 360
    mm, ss = divmod(remaining, 60)
    timer = f"{mm:02d}:{ss:02d}"

    html = f"""
    <div class="circle"
         style="background:
            conic-gradient(#e74c3c 0deg {angle}deg,
                           #eeeeee {angle}deg 360deg);">
      <span>{mm:02d}:{ss:02d}</span>
    </div>"""
    return html

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

# local_css 함수는 더 이상 필요 없으므로 제거합니다.
# def local_css(file_name):
#     with open(file_name) as f:
#         st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# "style.css" 파일 로드도 더 이상 필요 없으므로 제거합니다.
# local_css("style.css")

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


# 동장 함수
def handle_start():
    if st.session_state.phase == 'idle':
        st.session_state.remaining_focus = st.session_state.adjusted_focus or total_focus
        st.session_state.remaining_break = st.session_state.adjusted_break or total_break
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

def adjust_intervals():
    # 너무 짧은 시간일 경우 자동 조정 제외
    if total_focus < 60 or total_break < 60:
        return

    history = st.session_state.session_history[-3:]
    if not history:
        return

    success_count = sum(1 for h in history if h['success'])

    focus = total_focus
    brk = total_break

    if success_count >= 2:
        focus = min(focus + 60, 50 * 60)
        brk = max(brk - 60, 3 * 60)
    else:
        focus = max(focus - 60, 10 * 60)
        brk = min(brk + 60, 15 * 60)

    st.session_state.adjusted_focus = focus
    st.session_state.adjusted_break = brk

# UI
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

# ===== 🖼 이미지 버튼 표시 (현재 이 부분은 주석 처리되어 사용되지 않습니다.) =====
# start_img = load_image_base64("btn_img/start.png")
# pause_img = load_image_base64("btn_img/pause.png")
# reset_img = load_image_base64("btn_img/reset.png")
# stop_img  = load_image_base64("btn_img/stop.png")

# # 이미지 버튼 영역 (이전 코드에서 주석 처리되어 있었고, 일반 st.button이 스타일링되도록 변경되었습니다.)
# col1, col2, col3, col4 = st.columns(4)
# with col1:
#     image_button(start_img, "start")
# with col2:
#     image_button(pause_img, "pause")
# with col3:
#     image_button(reset_img, "reset")
# with col4:
#     image_button(stop_img, "stop")


# 버튼 영역 (이제 이 st.button()들이 GLOBAL_CSS의 영향을 받습니다.)
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
with col_btn1:
    if st.button("▶️ 타이머 시작"):
        handle_start()
with col_btn2:
    if st.button("⏸️ 일시정지"):
        handle_pause()
with col_btn3:
    if st.button("🔄 타이머 초기화"):
        handle_reset()
with col_btn4:
    if st.button("⏹️ 타이머 중지"):
        handle_stop()

# ===== 🖱 이미지 버튼 이벤트 처리 (이전에 image_button 함수를 사용했을 때만 필요) =====
# 현재 코드에서는 st.button()을 사용하므로, 이 query_params 부분은 제거하거나,
# 만약 여전히 image_button을 사용하고 싶다면 해당 부분과 연동되어야 합니다.
# query_params = st.query_params

# if "btn" in query_params:
#     btn_val = query_params["btn"][0]
#     if btn_val == "start":
#         handle_start()
#     elif btn_val == "pause":
#         handle_pause()
#     elif btn_val == "reset":
#         handle_reset()
#     elif btn_val == "stop":
#         handle_stop()

#     # 쿼리 파라미터 초기화
#     st.query_params.clear()  # 또는 update({})
#     st.rerun()

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

        # ==== ✅ 세션 성공 여부 기록 ====
        session_success = st.session_state.remaining_focus <= 5  # 남은 시간 거의 없으면 성공으로 간주
        st.session_state.session_history.append({
            'success': session_success
        })
        adjust_intervals()


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
else:
    # 정지 상태에서 타이머 보여주기
    if st.session_state.phase == 'focus':
        components.html(draw_circle(st.session_state.remaining_focus, total_focus), height=260)
    elif st.session_state.phase == 'break':
        components.html(draw_circle(st.session_state.remaining_break, total_break), height=260)
    else: # idle 상태일 때 초기 타이머 원형 표시 (옵션)
        # 기본 시간을 0으로 설정하거나, 설정된 집중 시간으로 표시할 수 있습니다.
        components.html(draw_circle(total_focus if total_focus > 0 else 0, total_focus if total_focus > 0 else 1), height=260) # total_focus가 0일 경우 에러 방지

# 자동 시간 조정
if st.session_state.adjusted_focus is not None and st.session_state.adjusted_break is not None:
    focus_min = st.session_state.adjusted_focus // 60
    focus_sec = st.session_state.adjusted_focus % 60
    break_min = st.session_state.adjusted_break // 60
    break_sec = st.session_state.adjusted_break % 60

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⏱ 자동 조정된 시간")
    st.sidebar.markdown(f"▶️ 집중 시간: `{focus_min}분 {focus_sec}초`")
    st.sidebar.markdown(f"💤 휴식 시간: `{break_min}분 {break_sec}초`")