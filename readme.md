# 집중하세요 AI

## 1. 프로젝트 소개

집중하세요 AI는 **컴퓨터 비전 기반 집중도 관리 프로그램**이다.  
웹캠을 통해 사용자의 얼굴과 손을 인식하여 사용자의 집중 상태를 분석하고,  
집중이 흐트러질 경우 경고 및 다양한 인터랙션 기능을 제공한다.

사용자가 장시간 자리를 비우거나, 집중 상태가 저하되면 음성 안내,  
화면 알림, 동기부여 영상 재생 등의 기능을 통해 집중을 유도한다.

---

# 2. 전체 동작 메커니즘

프로그램의 전체 동작 흐름은 다음과 같다.

웹캠 입력
↓
Face Detection (얼굴 감지)
↓
Hand Detection (손 감지)
↓
## 행동 분석

## 얼굴 중앙 위치 여부

## 얼굴 터치 여부

몸 흔들림 여부
↓
집중도 계산
↓
집중 상태 유지 / 경고 발생
↓
사용자 인터랙션

## 정지

## 재시작

## 동기부여 영상


# 3. 주요 기능

## 3.1 얼굴 인식
`MediaPipe`를 이용하여 얼굴을 탐지하고 사용자가 화면 중앙에 있는지 판단한다.

기능
- 얼굴 위치 추적
- 중앙 ROI 영역 판단
- 장시간 미감지 상태 확인

---

## 3.2 손 인식
`MediaPipe Hands`를 사용하여 손을 감지한다.

기능
- 손 개수 탐지
- 손 좌표 추적
- 얼굴 터치 감지

---

## 3.3 집중도 계산

다음 요소를 기반으로 집중도를 계산한다.

요소

- 얼굴 존재 여부
- 얼굴 터치 여부
- 몸 흔들림 여부
- 경고 상태 여부

집중도 범위

`0 ~ 100`



## 3.4 경고 시스템

### 사용자가 일정 시간 동안 자리를 비우면 다음 기능이 동작한다.

- 음성 안내 (TTS)
- 경고 화면 표시
- 전체 화면 알림


## 3.5 바른 자세 알림

### 조건

- 얼굴이 중앙 ROI에 있음
- 손이 감지됨
- 3초 유지

동작

`"바른 자세 합시다"`

텍스트 및 음성으로 안내



## 3.6 일시 정지 기능

`Q` 키 입력 시 다음 메뉴가 표시된다.

메뉴

- 종료
- 정지

정지 선택 시 다음 옵션 제공

- 담타
- 화장실
- 밥 (4회 제한)
- 솔직히 집중하기 힘듬



## 3.7 동기부여 영상 재생

다음 조건에서 영상이 재생된다.

1. "솔직히 집중하기 힘듬" 선택
2. "집중하겠습니다" 문구 5회 입력

### 영상

`assets/video2.mp4`


### 특징

- 전체 화면 재생
- 얼굴 중앙 유지 감지
- 30초 벗어나면 영상 재시작
- 영상 종료 후 자동 재시작

---

# 4. 사용 기술

## Computer Vision

- OpenCV
- MediaPipe

## AI / 분석

- 행동 분석 로직
- 집중도 계산 알고리즘

## 기타

- PyTTSx3 (음성 안내)
- Tkinter (UI 입력)
- VLC (영상 재생)

---

# 5. 프로젝트 구조
```
cometo_project01
│
├ assets
│ ├ lock_image.jpg
│ └ video2.mp4
│
├ src
│ ├ alerts
│ │ ├ lock_screen.py
│ │ └ voice.py
│ │
│ ├ analysis
│ │ ├ behavior.py
│ │ └ roi.py
│ │
│ ├ detectors
│ │ ├ face_detector.py
│ │ └ hands_detector.py
│ │
│ ├ utils
│ │ ├ fps.py
│ │ ├ resource_path.py
│ │ └ session_logger.py
│ │
│ ├ vision
│ │ ├ camera.py
│ │ ├ drawing.py
│ │ ├ korean_text.py
│ │ ├ motivation_player.py
│ │ └ pause_ui.py
│ │
│ ├ config.py
│ └ main.py
│
├ tests
│ ├ test_behavior.py
│ └ test_smoke.py
│
├ requirements.txt
└ README.md
```

# 6. 설치 방법

## 1. 저장소 다운로드
```
git clone [repository url]
cd cometo_project01
```


`또는 GitHub에서 ZIP 다운로드`


## 2. Python 설치

`Python 3.12` 사용

### 다운로드

`https://www.python.org/downloads/`


### 설치 후 확인

`python --version`


## 3. 가상환경 생성


`py -3.12 -m venv venv312`


### 활성화


`.\venv312\Scripts\Activate`


## 4. 라이브러리 설치


`pip install -r requirements.txt`


## 5. VLC 설치

### 영상 음성 재생을 위해 VLC 설치 필요


`https://www.videolan.org/vlc/`


# 7. 프로그램 실행


`python -m src.main`


# 8. 테스트 실행


`python -m pytest -q`


### 정상 출력 예시


`4 passed`

# 9. exe 실행 방법

## 빌드된 실행 파일 위치

`dist/FocusAI/FocusAI.exe`


## 실행 방법

`FocusAI.exe` 더블클릭

```
FocusAI
├ FocusAI.exe
└ _internal
```


# 10. 타 PC 실행 시 주의사항

## 다른 컴퓨터에서 실행할 경우 다음 조건 필요

1. 웹캠 존재
2. Windows 환경
3. VLC 설치
4. FocusAI 폴더 전체 복사

---

# 11. 테스트 방법

프로그램 실행 후 다음을 확인한다.

- 카메라 실행
- 얼굴 인식
- 손 인식
- 집중도 표시
- Q 메뉴 작동
- 영상 재생
- 음성 안내

---

# 12. 한계점 및 향후 개선

## 현재 한계

- 조명 환경에 따른 인식 정확도 변화
- 단일 카메라 기반 행동 분석

## 향후 개선

- Pose Estimation 추가
- 집중도 AI 모델 개선
- 사용자 행동 데이터 분석 기능 추가
