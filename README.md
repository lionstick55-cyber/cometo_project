# 2D → 3D 변환 및 Depth Estimation

## 📌 실습 목표
본 실습의 목표는 2D 이미지로부터 Depth Map을 생성하며

이를 기반으로 3D Point Cloud로 변환한다

또한, Unit Test를 통해 정상 동작을 검증하고,

기존 Depth Map 방식의 한계를 인식하여 DPT 기반 Depth을 추가로 실습했다.



## 📂 프로젝트 구조


```cometo_project01/```
```├── depth_bf_af_images/        # 원본 이미지 및 결과 저장 폴더```
```├── src/```
```│   ├── depth_map.py         # 기본 Depth Map 생성```
```│   ├── pointcloud.py        # Depth → 3D Point Cloud 변환```
```│   └── depth_dpt.py          # DPT 기반 Depth Estimation```
```├── tests/```
```│   └── test_depth_map.py      # Unit Test 코드```
```├── main.py                    # 기본 방식 실행 파일```
```├── pytest.ini                 # pytest 설정 파일```
```├── README.md```
```└── .gitignore```





## ▶ 실행 방법

### 1️⃣ 기본 Depth Map + 3D 변환 실행
1. `depth_bf_af_images/` 폴더에 원본 이미지 저장  
   (예: `street_1.jpeg`)

2. 실행
`bash`
`python main.py`


이미지 이름 입력

`street_1.jpeg`


결과 파일

`depth_street_1.png`

`depth_color_street_1.png`

`pointcloud_street_1.xyz`

### 2️⃣ DPT 기반 Depth Estimation 실행

기존 grayscale 기반 Depth Map은 깊이의 상대적 표현만 가능하여
실제 거리감 파악이 어렵다고 판단하였다.
이에 따라 Hugging Face에서 제공하는 사전학습된 DPT 모델을 활용하여
Depth Estimation 결과를 비교 실습하였다.

실행

`python src/depth_dpt.py`


이미지 이름 입력

`street_1.jpeg`


결과 파일

`dpt_depth_street_1.png`
`dpt_depth_color_street_1.png`

## 🧪 Unit Test 코드 및 실행 결과 문서화

### ✔ Unit Test 목적

Unit Test는 Depth Map 생성과 3D Point Cloud 변환 로직이
의도한 대로 동작하는지를 자동으로 검증하기 위해 작성되었다.

### ✔ 테스트 코드 위치
`tests/test_depth_map.py`

### ✔ 테스트 항목

Depth Map 출력 크기 검증

Depth 값의 범위(0~1) 검증

Depth → Point Cloud 변환 결과 형태 검증

잘못된 입력(None)에 대한 예외 처리 검증

### ✔ Unit Test 실행 방법

프로젝트 루트에서 다음 명령어를 실행한다.

`pytest`

### ✔ 실행 결과

pytest 실행 결과, 총 4개의 테스트가 수집되었으며
모든 테스트가 정상적으로 통과하였다.

`collected 4 items`
`tests/test_depth_map.py .... [100%]`
```4 passed in 0.83s```


이를 통해 Depth Map 및 3D 변환 로직이
의도한 대로 정상 동작을 확인했다.

## 📊 결과 및 고찰

단순 grayscale 기반 Depth Map은 깊이의 상대적인 표현만 가능하여
실제 거리 정보 해석에 한계가 있었다고 판단하였다.
또한, Depth_Map_color를 실행했을 당시 색깔이 거리감을 직관적으로 판단하지 못했다.
DPT 기반 Depth Estimation은 장면의 구조를 보다 직관적으로 표현하였다.

두 방식의 결과를 비교함으로써
전통적인 방식과 딥러닝 기반 접근 방식의 차이를 알 수 있었다.