import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap
import datetime
import os
import base64
import pandas as pd

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

# 입력 데이터 → A4 이미지(1장) 생성
def render_a4(entries, dpi=300):
    # 캔버스
    img = Image.new("RGB", (A4_W, A4_H), "white")
    draw = ImageDraw.Draw(img)

    # 폰트 (더 큰 크기)
    title_font = pick_font(120)
    h2_font    = pick_font(70)
    body_font  = pick_font(50)
    meta_font  = pick_font(40)

    # 상단 장식 테두리 그리기
    border_thickness = 8
    # 상단 테두리
    draw.rectangle((0, 0, A4_W, border_thickness), fill=(0, 50, 100))
    # 하단 테두리  
    draw.rectangle((0, A4_H-border_thickness, A4_W, A4_H), fill=(0, 50, 100))
    # 좌측 테두리
    draw.rectangle((0, 0, border_thickness, A4_H), fill=(0, 50, 100))

    # 헤더
    y = MARGIN + 20
    header = "신고 및 단속완료"
    # 중앙 정렬
    w = draw.textlength(header, font=title_font)
    draw.text(((A4_W - w)//2, y), header, font=title_font, fill=(0,0,0))
    y += title_font.size + 30

    # 메타
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    meta = f"생성일시: {now}   총 입력: {len(entries)}건"
    draw.text((MARGIN, y), meta, font=meta_font, fill=(90,90,90))
    y += meta_font.size + 30

    # 구분선
    x = MARGIN
    box_w = A4_W - 2*MARGIN
    draw.rectangle((x, y, x+box_w, y+4), fill=(0,0,0))
    y += 40

    # 본문
    for idx, e in enumerate(entries, start=1):
        # 배경 박스 그리기
        box_y = y - 10
        box_h = 200  # 각 항목의 높이
        draw.rectangle((x-10, box_y, x+box_w+10, box_y+box_h), fill=(248, 249, 250), outline=(200, 200, 200), width=1)
        
        draw.text((x, y), f"[#{idx}]", font=h2_font, fill=(0,0,0))
        y += h2_font.size + 15

        y = draw_text_block(draw, x, y, "이용업체(중도매/직거래)", wrap_text(e.get("using_company")), h2_font, body_font)
        y = draw_text_block(draw, x, y, "업체명", wrap_text(e.get("company_name")), h2_font, body_font)
        y = draw_text_block(draw, x, y, "주문시 사용하는 주문자명", wrap_text(e.get("order_name")), h2_font, body_font)
        y = draw_text_block(draw, x, y, "전화번호", wrap_text(e.get("phone")), h2_font, body_font)
        y = draw_text_block(draw, x, y, "업체 판매처 URL", wrap_text(e.get("store_url")), h2_font, body_font)

        # 카드 구분선
        y += 20
        draw.rectangle((x, y, x+box_w, y+2), fill=(220,220,220))
        y += 30

        # 한 장에 넘칠 것 같으면 중단
        if y > A4_H - (MARGIN + 200):
            break

    # 신고완료업체 섹션 추가
    if st.session_state.reported_companies:
        y += 50
        draw.text((x, y), "신고완료된 업체", font=h2_font, fill=(0,0,0))
        y += h2_font.size + 20
        
        for i, company in enumerate(st.session_state.reported_companies, 1):
            draw.text((x, y), f"{i}. {company}", font=body_font, fill=(0,0,0))
            y += body_font.size + 10

    return img

def pil_to_bytes(img: Image.Image, fmt="PNG"):
    buf = BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf

def pil_to_pdf_bytes(img: Image.Image):
    # 단일 이미지 PDF
    pdf_bytes = BytesIO()
    img_rgb = img.convert("RGB")
    img_rgb.save(pdf_bytes, format="PDF", resolution=300.0)
    pdf_bytes.seek(0)
    return pdf_bytes

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
    reported_company = st.text_input("신고완료된 업체명", placeholder="예: ㈜신고완료업체")
    submitted_reported = st.form_submit_button("신고완료업체 추가")
    
    if submitted_reported and reported_company:
        st.session_state.reported_companies.append(reported_company)
        st.success("신고완료업체 추가 완료!")

# 신고완료업체 리스트 표시
if st.session_state.reported_companies:
    st.subheader(f"신고완료업체 리스트 ({len(st.session_state.reported_companies)}건)")
    for i, company in enumerate(st.session_state.reported_companies, 1):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"{i}. {company}")
        with col2:
            if st.button("삭제", key=f"del_reported_{i}"):
                st.session_state.reported_companies.pop(i-1)
                st.rerun()
    
    if st.button("신고완료업체 모두 삭제"):
        st.session_state.reported_companies.clear()
        st.rerun()

# 이미지 생성
st.markdown("---")
st.subheader("A4 이미지 / PDF 생성")
colA, colB = st.columns(2)
with colA:
    gen_png = st.button("A4 PNG 생성")
with colB:
    gen_pdf = st.button("A4 PDF 생성")

png_bytes = None
pdf_bytes = None
preview = None

if (gen_png or gen_pdf):
    if not st.session_state.entries:
        st.warning("먼저 항목을 하나 이상 추가해 주세요.")
    else:
        img = render_a4(st.session_state.entries)
        preview = img.copy().resize((int(A4_W/2), int(A4_H/2)))  # 미리보기용 확대
        if gen_png:
            png_bytes = pil_to_bytes(img, "PNG")
        if gen_pdf:
            pdf_bytes = pil_to_pdf_bytes(img)

# 미리보기 & 다운로드 버튼
if preview:
    st.image(preview, caption="미리보기 (축소)", use_container_width=False)

    colD, colE = st.columns(2)
    if png_bytes:
        st.download_button(
            label="PNG 다운로드",
            data=png_bytes,
            file_name=f"신고_및_단속완료_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.png",
            mime="image/png",
            use_container_width=True
        )
    if pdf_bytes:
        st.download_button(
            label="PDF 다운로드",
            data=pdf_bytes,
            file_name=f"신고_및_단속완료_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

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
        for i, company in enumerate(st.session_state.reported_companies, 1):
            lines.append(f"{i}. {company}")
    msg = "\n".join(lines)
    st.code(msg, language="text")
else:
    st.info("항목을 추가하면 자동으로 요약 메시지를 만들어 드려요.")
