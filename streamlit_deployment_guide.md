# Streamlit Cloud 배포 가이드

## 1. Streamlit Cloud 접속
- https://share.streamlit.io/ 에 접속
- GitHub 계정으로 로그인

## 2. 새 앱 배포
1. "New app" 버튼 클릭
2. 다음 정보 입력:
   - **Repository**: `YOUR_USERNAME/kakao-notice-app` (GitHub 저장소명)
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: 원하는 URL 설정 (예: `kakao-notice-app`)

## 3. 고급 설정 (선택사항)
- **Python version**: 3.9 (기본값 사용)
- **Requirements file**: `requirements.txt` (자동 감지됨)

## 4. 배포 시작
- "Deploy!" 버튼 클릭
- 배포 과정이 시작됩니다 (약 2-3분 소요)

## 5. 배포 완료
- 배포가 완료되면 제공된 URL로 앱에 접속 가능
- URL 형식: `https://YOUR_APP_NAME.streamlit.app`

## 6. 업데이트 방법
- GitHub에 코드를 푸시하면 자동으로 재배포됩니다
- Streamlit Cloud에서 수동으로 재배포도 가능합니다

## 주의사항
- GitHub 저장소는 **Public**이어야 합니다
- `requirements.txt` 파일이 올바르게 작성되어 있어야 합니다
- 앱이 정상 작동하는지 로컬에서 먼저 테스트해보세요
