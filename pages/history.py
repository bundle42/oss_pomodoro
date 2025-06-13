import streamlit as st
import json
import os
import pandas as pd
import altair as alt

# 기록 파일 경로
DATA_PATH = "user_sessions.json"

st.title("나의 뽀모도로 기록 보기")

# 기록 데이터 불러오기
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

    st.subheader("기록 목록")

    total_summary = []

    for entry in data_sorted:
        with st.expander(f"{entry['date']} 기록", expanded=False):
            sessions = entry.get("sessions", [])

            if sessions:
                for s in sessions:
                    st.markdown(f"- 세션 {s['session_number']} : **{s['duration_minutes']}분**")
            else:
                st.markdown("세션 기록 없음")

            review = entry.get("daily_review", "")
            if review:
                st.markdown(f"**리뷰**: {review}")
            else:
                st.markdown("리뷰 없음")

            additional = entry.get("addition_time", None)
            if additional is not None:
                st.markdown(f"**추가 집중 가능 시간**: {additional}분")
            else:
                st.markdown("추가 집중 시간 미입력")

            # 세션별 그래프
            if sessions:
                df = pd.DataFrame(sessions)
                df = df.sort_values("session_number")

                line_chart = alt.Chart(df).mark_line(point=True).encode(
                    x=alt.X("session_number:O", title="세션 번호", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("duration_minutes", title="집중 시간 (분)"),
                    tooltip=["session_number", "duration_minutes"]
                ).properties(
                    width=500,
                    height=300,
                    title="세션별 집중 시간 추이"
                )
                st.altair_chart(line_chart, use_container_width=True)

            total_focus_time = sum(s["duration_minutes"] for s in sessions)
            total_summary.append({"date": entry["date"], "total_focus": total_focus_time})

    # 날짜별 전체 그래프
    if total_summary:
        st.subheader("")

        summary_df = pd.DataFrame(total_summary)
        summary_df = summary_df.sort_values("date")
        summary_df["formatted_date"] = pd.to_datetime(summary_df["date"]).dt.strftime("%m/%d")

        total_chart = alt.Chart(summary_df).mark_line(point=True).encode(
            x=alt.X("formatted_date", title="날짜", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("total_focus", title="총 집중 시간 (분)"),
            tooltip=["formatted_date", "total_focus"]
        ).properties(
            width=700,
            height=350,
            title="전체 날짜별 집중 시간 변화"
        )

        st.altair_chart(total_chart, use_container_width=True)




