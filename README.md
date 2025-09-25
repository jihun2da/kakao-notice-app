# 신고 및 단속완료 자동 이미지 생성기

카카오톡 신고 및 단속완료 보고서를 자동으로 A4 이미지(PNG/PDF)로 생성하는 Streamlit 웹 애플리케이션입니다.

## 기능

- 📝 신고 및 단속완료 정보 입력 (최대 20건)
- 🖼️ A4 크기 이미지 자동 생성 (PNG/PDF)
- 📱 카카오톡 전송을 위한 최적화된 형식
- 📋 자동 생성된 요약 메시지 텍스트 제공

## 사용법

1. 웹 애플리케이션에 접속
2. 신고 및 단속완료 정보 입력:
   - 이용중인 업체 확인된곳
   - 이용업체
   - 업체명
   - 업체 판매처 URL
   - 주문자명
   - 연락처
3. "추가" 버튼으로 항목 추가 (최대 20건)
4. "A4 PNG 생성" 또는 "A4 PDF 생성" 버튼 클릭
5. 생성된 이미지/PDF 다운로드
6. 카카오톡으로 전송

## 카카오톡 전송 방법

### PC에서
1. 생성된 PNG 또는 PDF 파일 다운로드
2. 카카오톡 PC 대화창에 마우스로 끌어다 놓기 → 보내기

### 모바일에서
1. 다운로드한 이미지/문서 저장
2. 카카오톡에서 + → 사진/파일 선택 후 전송

## 기술 스택

- **Frontend**: Streamlit
- **Image Processing**: Pillow (PIL)
- **Data Processing**: Pandas
- **Deployment**: Streamlit Cloud

## 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 애플리케이션 실행
streamlit run app.py
```

## 배포

이 애플리케이션은 Streamlit Cloud를 통해 배포됩니다.

## 라이선스

MIT License
