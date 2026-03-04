# YOLOv8 객체 탐지 프로젝트

## 1. 프로젝트 개요

YOLOv8 모델을 활용하여 이미지에서 **Person, Dog, Car 객체를 탐지**하는 시스템을 구현하였다.

초기에는 기본 모델을 사용하여 테스트를 진행하였고, 이후 정확도를 높이기 위해 외부 데이터셋을 다운로드하여 
필요한 클래스만 추출하여 재학습을 수행하였다.
최종적으로 학습된 모델을 이용하여 이미지에서 객체를 탐지하고 결과를 시각화하였다.



## 2. 프로젝트 구조

```
cometo_project
├── train.py              # 모델 학습 스크립트
├── infer.py              # 객체 탐지 추론
├── make_subset_3cls.py   # 데이터셋 필터링 (person/dog/car)
├── check_classes.py      # 데이터셋 클래스 분포 확인
│
├── data.yaml             # 데이터셋 설정
├── data_3cls.yaml        # 필터링된 데이터셋 설정
│
├── best.pt               # 학습된 모델
│
├── photos                # 테스트 이미지
│
└── results               # 추론 결과 이미지
```

## 3. 개발 환경

- Python
- YOLOv8 (Ultralytics)
- OpenCV

### 설치

`bash`
`pip install ultralytics opencv-python`

## 4. 데이터셋 구성 과정

### 1단계: 원본 데이터셋 준비

외부 데이터셋을 다운로드하여 프로젝트에 사용하였다.

하지만 원본 데이터셋에는 다양한 클래스가 포함되어 있어
필요한 객체만 학습하도록 3개의 클래스만 추출하였다.

목표 클래스

`person, dog, car`

### 2단계: 데이터셋 필터링

`make_subset_3cls.py`
스크립트를 이용하여
원본 데이터셋에서 필요한 클래스만 추출하였다.

#### 기능

`person / dog / car` 클래스만 유지

다른 클래스 제거

새로운 dataset 폴더 생성

새로운 data yaml 생성

`python make_subset_3cls.py`

#### 결과

`datasets_3cls/`

데이터셋이 생성된다.

### 3단계: 클래스 매핑

원본 데이터셋에서는 같은 의미의 클래스가 여러 이름으로 존재할 수 있기 때문에
다음과 같이 동의어(alias)를 이용하여 하나의 클래스로 통합하였다.

#### 예시


`person → person / people / persons / pedestrian`
`car → car / Car`
`dog → dog`


이를 통해 데이터셋의 클래스 일관성을 유지하였다.

## 5. 모델 학습

train.py는 YOLOv8 모델을 이용하여 객체 탐지를 학습하는 스크립트이다.

### 학습 과정

YOLOv8 기본 모델 로드

data.yaml을 통해 데이터셋 경로 설정

### 학습 수행

`python train.py`

### 학습 완료 후

`best.pt`

생성되며, 이는 최종 학습된 모델이다.

## 6. 추론 (Inference)

infer.py는 학습된 모델을 이용하여 이미지에서 객체를 탐지한다.

### 동작 과정

학습된 모델(best.pt) 로드

입력 이미지 분석

객체 탐지 수행

탐지 결과를 이미지에 표시

결과 이미지를 results 폴더에 저장

### 예시 실행

`python infer.py photos/dogwalk2.jpg --model best.pt`

## 7. 클래스별 Confidence Threshold

추론 과정에서 클래스별로 다른 confidence threshold를 적용하였다.


`person - 0.25`
`dog - 0.05`
`car - 0.20`

이를 통해 객체 특성에 따라 탐지 민감도를 조정하였다.

## 8. 결과 저장

추론 결과는 자동으로 다음 폴더에 저장된다.

`results/`

저장되는 파일 형식

`result_이미지이름.jpg`

예시

`result_dogwalk.jpg`
`result_peopledogcar.jpg`

## 9. 데이터 검증

`check_classes.py`

스크립트를 사용하여
데이터셋에서 클래스 분포를 확인하였다.

기능

label 파일 개수 확인

클래스별 객체 수 확인

`python check_classes.py`

## 10. 결론

YOLOv8 모델을 이용하여 person, dog, car 객체 탐지 시스템을 구현하였다.

외부 데이터셋을 재구성하고 클래스 필터링을 수행함으로써
필요한 객체만 학습하도록 하고 
모델의 효율성과 정확도를 개선할 수 있었다.
