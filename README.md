# 새봄추 언제와
이 프로그램은 특정 채널의 방송 시작 여부를 확인하고 알림을 제공합니다.

## 실행 방법
1. `build/downlink.txt` 링크를 통해 파일을 다운로드하여 실행하세요.
2. 또는 아래 단계를 따라 EXE 파일을 직접 생성할 수 있습니다.

## 작동 방법
1. 아무것도 입력하지 않을 시 기본 정보로 작동합니다.
2. 여러개의 방송에 적용하고 싶다면, 채널 아이디를 공백없이 쉽표(,)를 이용해서 입력하면, 모두에 적용되어 작동합니다.

## EXE 파일 생성 방법
1. Python 3.10 이하 설치 ( Pyqt5가 높은버전에서는 제대로 작동하지 않습니다. )
2. `pip install pyqt5 requests`로 필요한 패키지 설치
3. 배경화면으로 사용할 사진을 코드와 같은 경로에 넣고 'background.png'로 이름을 입력하세요.
4. `pyinstaller --onefile --noconsole --add-data "background.png;." chk_auto_waiting.py` 명령어 실행
5. ㄴ background 파일을 exe파일에 포함시키며, 프로그램창 이외의 터미널 생성을 억제합니다.

## 다운로드 링크
EXE 파일을 다운로드하려면 [여기](https://drive.google.com/file/d/1g8HldDRYY_KFP3Z5qLd3Rr3PgZtip2HY/view?usp=sharing)를 클릭하세요.



## 보안 검토

