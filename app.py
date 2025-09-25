import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap
import datetime
import os
import base64
import pandas as pd
import json
import pickle

# =========================
# 기본 설정
# =========================
st.set_page_config(page_title="신고 및 단속완료 - 자동 이미지 생성", page_icon="✅", layout="centered")

A4_W, A4_H = 3508, 4961   # 300DPI 기준 A4 px (더 큰 해상도)
MARGIN = 150
MAX_ITEMS = 20

# 폰트 탐색(우선순위: assets -> OS 공용 경로 -> 기본)
FONT_CANDIDATES = [
    "assets/NanumGothic.ttf",
    "C:/Windows/Fonts/malgun.ttf",  # Windows 맑은 고딕
    "C:/Windows/Fonts/gulim.ttc",   # Windows 굴림
    "C:/Windows/Fonts/batang.ttc",  # Windows 바탕
    "C:/Windows/Fonts/dotum.ttc",  # Windows 돋움
    "C:/Windows/Fonts/NanumGothic.ttf",  # Windows 나눔고딕
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",  # macOS
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"  # Linux(일반)
]
def pick_font(size: int):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
    # 폰트가 없어도 죽지 않도록 기본 로드
    return ImageFont.load_default()

# 텍스트 블록 그리기
def draw_text_block(draw, x, y, title, lines, title_font, body_font, line_gap=8):
    draw.text((x, y), f"■ {title}", font=title_font, fill=(0,0,0))
    y += title_font.size + 20
    for line in lines:
        draw.text((x, y), line, font=body_font, fill=(0,0,0))
        y += body_font.size + line_gap
    return y + 20

def wrap_text(s: str, width: int = 60):
    s = (s or "").strip()
    return textwrap.wrap(s, width=width) if s else ["-"]

# 이미지 생성 함수들은 제거됨 (메시지 텍스트만 사용)

# =========================
# UI
# =========================
st.markdown("<h1 style='text-align:center;'>신고 및 단속완료</h1>", unsafe_allow_html=True)
st.caption("입력 → A4 이미지(PNG/PDF) 생성 → 카톡으로 끌어다놓기/공유")

# 세션 스토리지
if "entries" not in st.session_state:
    st.session_state.entries = []
if "reported_companies" not in st.session_state:
    st.session_state.reported_companies = []
if "saved_data" not in st.session_state:
    st.session_state.saved_data = {}

# 날짜별 저장 함수
def save_daily_data():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    data = {
        "entries": st.session_state.entries.copy(),
        "reported_companies": st.session_state.reported_companies.copy(),
        "timestamp": datetime.datetime.now().isoformat()
    }
    st.session_state.saved_data[today] = data
    return today

# 날짜별 데이터 로드 함수
def load_daily_data(date):
    if date in st.session_state.saved_data:
        data = st.session_state.saved_data[date]
        st.session_state.entries = data["entries"]
        st.session_state.reported_companies = data["reported_companies"]
        return True
    return False

# 입력 폼
with st.form("entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    using_company = col1.text_input("이용업체(중도매/직거래)", placeholder="예: 기린컴퍼니")
    company_name = col2.text_input("업체명", placeholder="예: ㈜예시상사")

    order_name = col1.text_input("주문시 사용하는 주문자명", placeholder="예: 홍길동")
    phone = col2.text_input("전화번호", placeholder="010-0000-0000")
    
    store_url = st.text_input("업체 판매처 URL", placeholder="https://...")

    submitted = st.form_submit_button("추가 (최대 20건)")
    if submitted:
        if len(st.session_state.entries) >= MAX_ITEMS:
            st.warning("최대 20건까지 입력 가능합니다.")
        else:
            st.session_state.entries.append({
                "using_company": using_company,
                "company_name": company_name,
                "order_name": order_name,
                "phone": phone,
                "store_url": store_url,
            })
            st.success("추가 완료!")

# 리스트 표시/관리
st.subheader(f"입력 리스트 ({len(st.session_state.entries)}/{MAX_ITEMS})")
if st.session_state.entries:
    df = pd.DataFrame(st.session_state.entries, columns=[
        "using_company","company_name","order_name","phone","store_url"
    ])
    st.dataframe(df, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("마지막 항목 삭제"):
            st.session_state.entries.pop()
            st.rerun()
    with c2:
        if st.button("모두 비우기"):
            st.session_state.entries.clear()
            st.rerun()

# 신고완료업체 별도 입력 섹션
st.markdown("---")
st.subheader("신고완료된 업체명 입력")

with st.form("reported_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    reported_company = col1.text_input("신고완료된 업체명", placeholder="예: ㈜신고완료업체")
    reported_url = col2.text_input("업체 URL", placeholder="https://...")
    
    submitted_reported = st.form_submit_button("신고완료업체 추가")
    
    if submitted_reported and reported_company:
        st.session_state.reported_companies.append({
            "company": reported_company,
            "url": reported_url
        })
        st.success("신고완료업체 추가 완료!")

# 신고완료업체 리스트 표시
if st.session_state.reported_companies:
    st.subheader(f"신고완료업체 리스트 ({len(st.session_state.reported_companies)}건)")
    for i, company_data in enumerate(st.session_state.reported_companies, 1):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"{i}. {company_data['company']}")
            if company_data.get('url'):
                st.write(f"   URL: {company_data['url']}")
        with col2:
            if st.button("삭제", key=f"del_reported_{i}"):
                st.session_state.reported_companies.pop(i-1)
                st.rerun()
    
    if st.button("신고완료업체 모두 삭제"):
        st.session_state.reported_companies.clear()
        st.rerun()

# 저장 버튼
st.markdown("---")
st.subheader("데이터 저장")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("오늘 데이터 저장"):
        save_date = save_daily_data()
        st.success(f"데이터가 {save_date}에 저장되었습니다!")
with col2:
    if st.button("현재 데이터 초기화"):
        st.session_state.entries.clear()
        st.session_state.reported_companies.clear()
        st.rerun()
with col3:
    if st.button("모든 저장된 데이터 삭제"):
        st.session_state.saved_data.clear()
        st.success("모든 저장된 데이터가 삭제되었습니다!")

# 캘린더 및 저장된 데이터 확인
st.markdown("---")
st.subheader("저장된 데이터 확인")

# 저장된 날짜 목록 표시
if st.session_state.saved_data:
    st.write("저장된 날짜 목록:")
    saved_dates = sorted(st.session_state.saved_data.keys(), reverse=True)
    
    # 날짜 선택 드롭다운
    selected_date = st.selectbox("확인할 날짜를 선택하세요:", saved_dates)
    
    if selected_date:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("선택한 날짜 데이터 로드"):
                if load_daily_data(selected_date):
                    st.success(f"{selected_date} 데이터를 로드했습니다!")
                    st.rerun()
                else:
                    st.error("데이터를 로드할 수 없습니다.")
        
        with col2:
            if st.button("선택한 날짜 데이터 삭제"):
                del st.session_state.saved_data[selected_date]
                st.success(f"{selected_date} 데이터가 삭제되었습니다!")
                st.rerun()
        
        # 선택한 날짜의 데이터 미리보기
        if selected_date in st.session_state.saved_data:
            data = st.session_state.saved_data[selected_date]
            st.write(f"**{selected_date} 저장된 데이터:**")
            
            if data["entries"]:
                st.write("**일반 업체 정보:**")
                df = pd.DataFrame(data["entries"], columns=[
                    "using_company","company_name","order_name","phone","store_url"
                ])
                st.dataframe(df, use_container_width=True)
            
            if data["reported_companies"]:
                st.write("**신고완료업체:**")
                for i, company_data in enumerate(data["reported_companies"], 1):
                    st.write(f"{i}. {company_data['company']}")
                    if company_data.get('url'):
                        st.write(f"   URL: {company_data['url']}")
else:
    st.info("저장된 데이터가 없습니다. 먼저 데이터를 입력하고 저장해주세요.")

# 메시지 텍스트 생성 및 전송
st.markdown("---")
st.subheader("메시지 텍스트 생성")

# 전송 가이드
st.markdown("---")
st.subheader("카카오톡 전송 방법 (가장 간단, 무료)")
st.markdown("""
**PC에서**  
1) 위에서 **PNG 또는 PDF**를 다운로드  
2) **카카오톡 PC** 대화창에 마우스로 **끌어다 놓기** → 보내기

**모바일에서**  
1) 다운로드한 **이미지/문서 저장**  
2) 카카오톡에서 **+ → 사진/파일** 선택 후 **전송**
""")

# 추가 옵션(선택): 메시지 텍스트 자동 생성/복사
st.markdown("#### 메시지 텍스트(선택, 복사해서 함께 전송)")
if st.session_state.entries:
    # 간단 메시지 빌드
    lines = ["[신고 및 단속완료 요약]"]
    for i, e in enumerate(st.session_state.entries, start=1):
        lines.append(f"#{i} [{e.get('company_name','-')}]")
        lines.append(f" - 이용업체: {e.get('using_company','-')}")
        lines.append(f" - 주문자명: {e.get('order_name','-')}, 연락처: {e.get('phone','-')}")
        lines.append(f" - URL: {e.get('store_url','-')}")
    
    # 신고완료업체 추가
    if st.session_state.reported_companies:
        lines.append("\n[신고완료된 업체]")
        for i, company_data in enumerate(st.session_state.reported_companies, 1):
            lines.append(f"{i}. {company_data['company']}")
            if company_data.get('url'):
                lines.append(f"   URL: {company_data['url']}")
    msg = "\n".join(lines)
    st.code(msg, language="text")
else:
    st.info("항목을 추가하면 자동으로 요약 메시지를 만들어 드려요.")
