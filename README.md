# 공책RPG - 텍스트 기반 상태 입력에 따른 이미지 생성 시스템

어린 시절, 손재주가 좋은 친구, 말재주가 좋은 친구와 함께 만들어가던 ‘공책 RPG’.

이제는 AI가 그 역할을 이어받습니다.

당신은 꿈을 꾸세요. 구현은 우리가 맡겠습니다.

# 1. 프로젝트 개요

본 프로젝트는 텍스트 기반 상태(장면/게임 진행 정도)를 입력으로 받아 이미지 생성 모델을 활용하여 게임 장면을 생성하는 시스템입니다.

공책에 그려 구현했던, 이야기 진행 상황에 맞는 그림 및 아이템 등을 Diffusion 기반 모델을 통해 생성하는 구조를 가지고 있습니다.

본 프로젝트는, 단순한 이미지 생성이 아니라 다음을 목표로 설계되었습니다. 

● 기존 Diffusion 기반 이미지 생성 모델의 서비스 적용 시 한계 분석

● 동일한 입력에 대한 불필요한 재생성 비용 문제 확인

● 생성 모델을 실제 서비스에 적용할 때 발생하는 응답 지연 / 캐싱 / 상태 관리 문제를 구조적으로 해결

즉, 기존 이미지 생성 모델을 실제 서비스에 도입했을 때 발생하는 문제를 실험하고 개선하기 위한 프로젝트입니다.

# 2. 문제 정의

기존 Diffusion 기반 모델은 다음과 같은 한계를 가집니다:

● 동일 입력에도 매번 이미지 재생성 → 비용 낭비

● 초기 모델 로딩 시간 → UX 저하

● CPU 환경에서의 극단적인 속도 저하

● 상태 기반 서비스 설계 부재

이 프로젝트는 이를 해결하기 위해:

● Scene/State 기반 캐싱 구조

● 이미지 생성과 서비스 로직 분리

● 재사용 가능한 생성 결과 관리

를 설계 및 구현합니다.

# 3. 핵심 기능

🎮 Scene(게임 진행 상황) 기반 이미지 생성

♻️ 동일 Scene 재진입 시 이미지 캐싱 재사용

⚡ FastAPI 기반 비동기 API 구조

🧩 이미지 생성 모듈 분리 (추후 FLUX / Rectified Flow 교체 가능)

🗂 로컬 이미지 캐시 시스템

# 4. 시스템 아키텍처

----------------------------------------------------------------------------> [Cache Hit] -> 이미지 반환
                                                                         
[User Input] -> [React Frontend] -> [Scene/State 분석] -> [Cache Check] -|

----------------------------------------------------------------------------> [Cache Miss] -> 이미지 생성 -> 이미지 저장 -> 결과 반환 



# 5. 기술 스택

Backend

● Python

● FastAPI: API 서버 및 요청 처리

● Uvicorn: ASGI 서버

AI / Model

● PyTorch

● Diffusion Model (Stable Diffusion)
→ 텍스트 기반 이미지 생성

Frontend

● React
→ 사용자 입력 및 결과 시각화

Storage

● SQLite 

● Local File System (Image Cache)

# 6. 설치 방법 (Conda)

1. Python 가상 환경 생성
   
conda create -n notebook-rpg python=3.10

conda activate notebook-rpg

2. 패키지 설치

pip install -r requirements.txt

# 7. 설치 방법 (VS Code)

1. Python 가상 환경 생성

python -m venv venv

venv\Scripts\activate (Windows)

source venv/bin/activate (macOS / Linux)

2. 패키지 설치

pip install -r requirements.txt

3. 환경 변수 설정 (공통)

cp .env.example .env ( 필요시 주석 참고 후 수정 )

# 8. 실행 방법

1. Backend 실행

uvicorn app.main:app --reload

2. Frontend 실행

cd frontend

npm install

npm start

# 9. 동작 방식

1. 게임의 기본적인 시나리오를 입력해줌.
<img width="931" height="542" alt="image" src="https://github.com/user-attachments/assets/7b2265f8-724d-436d-a648-d23d4d81e074" />

2. 스토리에 적합한 이미지가 출력되며, 이야기가 진행됨.
<img width="983" height="834" alt="image" src="https://github.com/user-attachments/assets/ac5f33b0-caa7-40ee-945a-9cc2315e612d" />

3. 게임 도중 얻은 아이템은 스케치 기능을 통해 대략적인 프롬프트와 함께 img2img 모듈에 입력되어 내가 원하는 아이템 디자인이 가능함.
<img width="509" height="865" alt="image" src="https://github.com/user-attachments/assets/cdb42413-252c-4015-a61e-f16ef3a2fa83" />

# 10. 성능 및 한계

이 프로젝트를 통해 다음을 확인했습니다:

Diffusion 모델의 한계

● 초기 로딩 시간 매우 큼

● CPU 환경에서 실시간 사용 어려움

● 성능과 시간 사이의 트레이드 오프 관계를 고려해야 함

서비스 관점 문제

● 캐싱 없으면 비용 폭증

● 상태 관리 구조 필수

● 게임 플레이어의 특성을 고려해 실시간성 확보가 요구됨

# 11. 개선 방향

● Rectified Flow 기반 모델 (FLUX, Z-Image)로 교체

● 비동기 작업 큐 (Celery / Redis)

● LLM 기반 스토리 플래너 개발

● 게임의 재미를 느낄 수 있게 놀이 형태로 발전 
