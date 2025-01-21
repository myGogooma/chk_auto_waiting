import sys  # 시스템 관련 기능을 사용할 수 있게 해주는 모듈
from PyQt5 import QtCore, QtGui, QtWidgets  # PyQt5를 통해 GUI를 만들기 위한 모듈들
import requests  # HTTP 요청을 보내기 위한 모듈
import time  # 시간 관련 기능을 사용할 수 있게 해주는 모듈
import webbrowser  # 웹 브라우저를 열기 위한 모듈
import datetime  # 날짜와 시간을 다루기 위한 모듈
from threading import Thread, Event  # 멀티스레딩 기능을 위한 모듈
import os  # 운영 체제 관련 기능을 사용할 수 있게 해주는 모듈

#
# 채널 아이디 입력이 없을 경우, 기본값으로 적용되도록 추가
#

Title = "새봄추 언제와"  # 프로그램의 제목
background = "background.png"  # 배경 이미지 파일 이름

# 기본 채널 아이디 설정 (변수로 설정)
default_channel_id = "458f6ec20b034f49e0fc6d03921646d2"  # 기본 채널 아이디 값 설정

# Worker 클래스 정의
class Worker(Thread):
    def __init__(self, channel_ids, refresh, text_edit):
        super().__init__()  # Thread 클래스 초기화
        self.channel_ids = channel_ids  # 체크할 채널 ID 리스트
        self.refresh = refresh  # 갱신 간격
        self.text_edit = text_edit  # 텍스트 출력용 위젯
        self._stop_event = Event()  # 스레드 중지 이벤트

    def run(self):  # 스레드가 실행될 때 호출되는 메서드
        while not self._stop_event.is_set():  # 중지 이벤트가 설정되지 않았을 때 반복
            if not self.channel_ids:  # 확인할 채널이 없을 경우
                self.update_text("더 이상 확인할 채널이 없습니다. 프로그램을 종료합니다.")
                self.stop()  # 정지 프로세스 호출
                return

            for channel_id in self.channel_ids[:]:  # 리스트 복사 (현재 리스트에서 반복)
                try:
                    headers = {'User-Agent': 'Mozilla/5.0'}  # HTTP 요청 헤더 설정
                    # API 요청
                    request = requests.get(f"https://api.chzzk.naver.com/service/v1/channels/{channel_id}", headers=headers)

                    # 요청 실패 시 처리
                    if request.status_code != 200:
                        self.update_text(f"채널 {channel_id}에 대한 요청이 실패했습니다. 상태 코드: {request.status_code}")
                        self.channel_ids.remove(channel_id)  # 잘못된 채널 ID는 제외
                        continue

                    channel_info = request.json().get("content")  # JSON 형식으로 응답 받은 데이터 처리

                    # 채널 정보가 없거나 channelId가 없을 경우 처리
                    if channel_info is None or channel_info.get("channelId") is None:
                        self.update_text(f"{channel_id} - 존재하지 않는 채널 ID입니다.")
                        self.channel_ids.remove(channel_id)  # 잘못된 채널 ID는 제외
                        continue

                    open_live = channel_info.get("openLive")  # 방송 상태 확인
                    channel_name = channel_info.get("channelName")  # 채널 이름 가져오기

                    if open_live:  # 방송 중인 경우
                        self.update_text(f"{channel_name} 방송이 켜졌습니다! 10초 후에 접속합니다...")
                        for i in range(10, 0, -1):  # 10초 카운트다운
                            if self._stop_event.is_set():  # 중지 이벤트가 설정되면 종료
                                return
                            self.update_text(f"{i}초 남았습니다...")
                            time.sleep(1)  # 1초 대기
                        webbrowser.open(f"https://chzzk.naver.com/live/{channel_id}", new=0)  # 웹 브라우저에서 방송 링크 열기

                        # 방송 중인 채널은 제외
                        self.channel_ids.remove(channel_id)
                        self.update_text(f"{channel_name} 방송 중입니다. 이후 체크에서 제외됩니다.")

                    date = datetime.datetime.today().strftime('%H:%M:%S')  # 현재 시간 가져오기
                    self.update_text(f'[{date}] {channel_name} 방송 대기중...')  # 대기 메시지 출력

                except requests.exceptions.RequestException as e:  # 요청 오류 발생 시
                    self.update_text(f"오류 발생: {e}")
                    self.channel_ids.remove(channel_id)  # 오류 발생 시 채널 ID 제외
                except Exception as e:  # 기타 예외 처리
                    self.update_text(f"예상치 못한 오류 발생: {e}")

            self.update_text(f"모든 채널을 확인했습니다. {self.refresh}초 후에 다시 확인합니다...\n")
            time.sleep(self.refresh)  # 갱신 간격만큼 대기

    def stop(self):  # 스레드를 중지하는 메서드
        self._stop_event.set()

    def update_text(self, message):  # 텍스트 위젯에 메시지를 추가하는 메서드
        QtCore.QMetaObject.invokeMethod(self.text_edit, "append", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, message))

# UI 설정을 위한 클래스
class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(780, 720)  # 창 크기 설정

        # 시작 버튼
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(30, 20, 75, 23))  # 버튼 위치 및 크기 설정
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.start_checking)  # 버튼 클릭 시 start_checking 메서드 호출

        # 정지 버튼
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(675, 20, 75, 23))  # 버튼 위치 및 크기 설정
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.stop_program)  # 버튼 클릭 시 stop_program 메서드 호출

        # 채널 ID 입력 필드
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(30, 60, 720, 23))  # 위치 및 크기 설정
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setPlaceholderText("채널 ID를 쉼표로 구분하여 입력하세요 (예: 1234, 5678), 입력없을경우 기본값 서새봄")  # 플레이스홀더 텍스트 설정

        # 갱신 간격 입력 필드
        self.lineEdit_2 = QtWidgets.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(30, 100, 720, 23))  # 위치 및 크기 설정
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setPlaceholderText("갱신 간격(초)을 입력하세요 (기본: 5초)")  # 플레이스홀더 텍스트 설정

        # 배경 이미지 설정
        self.background_label = QtWidgets.QLabel(Form)
        self.background_label.setGeometry(QtCore.QRect(30, 150, 720, 540))  # 위치 및 크기 설정
        image_path = os.path.join(os.path.dirname(__file__), background)  # 배경 이미지 경로 설정
        self.background_pixmap = QtGui.QPixmap(image_path)  # 배경 이미지 불러오기
        self.background_label.setPixmap(self.background_pixmap)  # 배경 이미지 설정
        self.background_label.setScaledContents(True)  # 이미지 크기 조정

        # 텍스트 출력 필드
        self.textEdit = QtWidgets.QTextEdit(Form)
        self.textEdit.setGeometry(QtCore.QRect(30, 150, 720, 540))  # 위치 및 크기 설정
        self.textEdit.setStyleSheet("color: black; font-size: 12px; font-weight: bold; "
                                     "background: transparent; padding: 5px; ")  # 텍스트 스타일 설정
        self.textEdit.setReadOnly(True)  # 읽기 전용 설정

        self.retranslateUi(Form)  # UI 요소 텍스트 재설정
        QtCore.QMetaObject.connectSlotsByName(Form)  # UI 슬롯 연결
        self.worker = None  # 작업자 스레드 초기화

    def retranslateUi(self, Form):  # UI 텍스트 재설정 메서드
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", Title))  # 창 제목 설정
        self.pushButton.setText(_translate("Form", "Start"))  # 시작 버튼 텍스트 설정
        self.pushButton_2.setText(_translate("Form", "Stop"))  # 정지 버튼 텍스트 설정

    def start_checking(self):  # 채널 체크 시작 메서드
        if self.worker is None:  # 현재 작업자가 없을 경우
            # 채널 ID 입력 필드에서 값 가져오기
            channel_ids = self.lineEdit.text().strip().split(",") if self.lineEdit.text().strip() else [default_channel_id]
            # 갱신 간격 입력 필드에서 값 가져오기
            refresh_interval = int(self.lineEdit_2.text().strip()) if self.lineEdit_2.text().strip() else 5

            self.worker = Worker(channel_ids, refresh_interval, self.textEdit)  # Worker 객체 생성
            self.worker.start()  # 스레드 시작

            self.pushButton.setEnabled(False)  # 시작 버튼 비활성화
            self.pushButton_2.setEnabled(True)  # 정지 버튼 활성화
            self.update_text("채널 확인을 시작합니다...")

    def stop_program(self):  # 프로그램 종료 메서드
        if self.worker:  # 작업자가 있을 경우
            self.worker.stop()  # 작업자 중지
            self.worker = None  # 작업자 객체 초기화
            self.pushButton.setEnabled(True)  # 시작 버튼 활성화
            self.pushButton_2.setEnabled(False)  # 정지 버튼 비활성화
            self.update_text("프로그램이 종료되었습니다.")

    def update_text(self, message):  # 텍스트 출력 메서드
        self.textEdit.append(message)  # 메시지 추가

# PyQt5 애플리케이션 실행
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # 애플리케이션 객체 생성
    Form = QtWidgets.QWidget()  # 메인 윈도우 객체 생성
    ui = Ui_Form()  # UI 객체 생성
    ui.setupUi(Form)  # UI 설정
    Form.show()  # 윈도우 보여주기
    sys.exit(app.exec_())  # 애플리케이션 실행
