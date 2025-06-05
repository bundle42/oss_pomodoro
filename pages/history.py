import streamlit as st
import json
import os
from datetime import datetime

# 기록 파일 경로
DATA_PATH = "user_sessions.json"

st.title("📅 나의 뽀모도로 기록 보기")

# 데이터 불러오기 함수
def load_session_data():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

data = load_session_data()

if not data:
    st.info("아직 저장된 기록이 없습니다.")
else:
    # 날짜 기준 내림차순 정렬
    data_sorted = sorted(data, key=lambda x: x["date"], reverse=True)

    for entry in data_sorted:
        with st.expander(f"📌 {entry['date']} 기록", expanded=False):
            sessions = entry.get("sessions", [])
            if sessions:
                for s in sessions:
                    st.markdown(f"- 세션 {s['session_number']} : **{s['duration_minutes']}분**")
            else:
                st.markdown("⛔ 세션 기록 없음")

            review = entry.get("daily_review", "")
            if review:
                st.markdown(f"📝 **리뷰**: {review}")
            else:
                st.markdown("📝 리뷰 없음")

            additional = entry.get("addition_time", None)
            if additional is not None:
                st.markdown(f"⏱️ **추가 집중 가능 시간**: {additional}분")
            else:
                st.markdown("⏱️ 추가 집중 시간 미입력")
