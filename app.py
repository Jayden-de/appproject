import streamlit as st
import pandas as pd
import pydeck as pdk

# 페이지 설정
st.set_page_config(page_title="주말 인기 따릉이 대여소 대시보드", layout="wide")

st.title("🚲 주말 인기 따릉이 대여소 시각화")
st.markdown("`weekendpopular.csv` 데이터를 기반으로 주말 이용량이 많은 대여소를 지도에 표시합니다.")

# 데이터 로드
@st.cache_data
def load_data():
    file_path = 'weekendpopular.csv'
    # CSV 파일 읽기 (한글 깨짐 방지를 위해 cp949 혹은 utf-8-sig 확인 필요)
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='cp949')
    
    # 지도 표시를 위해 위도/경도 컬럼명 변경 (선택사항이나 pydeck/st.map 호환성 위해)
    df = df.rename(columns={
        '대여점위도': 'lat',
        '대여점경도': 'lon',
        '대여 대여소명': 'name',
        '주말': 'count'
    })
    return df

try:
    data = load_data()

    # 사이드바 설정
    st.sidebar.header("설정")
    top_n = st.sidebar.slider("표시할 상위 대여소 개수", min_value=5, max_value=50, value=20)

    # 데이터 정렬 및 추출
    top_df = data.sort_values(by='count', ascending=False).head(top_n)

    # 대시보드 레이아웃 (2컬럼)
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"Top {top_n} 대여소 위치")
        
        # Pydeck을 이용한 지도 시각화 (이용량에 따른 크기 조절)
        layer = pdk.Layer(
            "ScatterplotLayer",
            top_df,
            get_position="[lon, lat]",
            get_color="[200, 30, 0, 160]",
            get_radius="count * 0.5",  # 이용량에 비례하여 반지름 설정
            pickable=True,
        )

        view_state = pdk.ViewState(
            latitude=top_df['lat'].mean(),
            longitude=top_df['lon'].mean(),
            zoom=11,
            pitch=0,
        )

        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{name}\n주말 이용건수: {count}"}
        ))

    with col2:
        st.subheader("상세 순위")
        st.dataframe(
            top_df[['name', 'count']].reset_index(drop=True),
            use_container_width=True
        )

    # 통계 요약
    st.divider()
    st.subheader("데이터 통계")
    s_col1, s_col2, s_col3 = st.columns(3)
    s_col1.metric("총 대여소 수", f"{len(data)}개")
    s_col2.metric("최고 이용 건수", f"{data['count'].max():,}건")
    s_col3.metric("평균 주말 이용 건수", f"{int(data['count'].mean()):,}건")

except FileNotFoundError:
    st.error(f"파일을 찾을 수 없습니다: weekendpopular.csv")
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
