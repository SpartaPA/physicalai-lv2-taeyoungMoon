# physicalai-lv2-taeyoungMoon
PA과정 Level 2 과제 제출을 위한 저장소

- 이름: 문태영

## 과제 목록

| 모듈 | 주제 | 보고서 | 결과 파일 |
|---|---|---|---|
| 모듈 1 | OpenCR·다이나믹셀 통합 | [lv2_module1/report.md](lv2_module1/report.md) | [lv2_module1/results/](lv2_module1/results/) |
| 모듈 3 | 설정값에 따른 Mask와 검출 결과 변화 분석 | [lv2_module3/report.md](lv2_module3/report.md) | [lv2_module3/results/](lv2_module3/results/) |

---

## 모듈 1. OpenCR·다이나믹셀 통합

### 환경
- 호스트: Raspberry Pi 5,
  - OS:
    - PRETTY_NAME="Ubuntu 22.04.5 LTS"
    - NAME="Ubuntu"
    - VERSION_ID="22.04"
    - VERSION="22.04.5 LTS (Jammy Jellyfish)"
    - VERSION_CODENAME=jammy
    - ID=ubuntu
    - ID_LIKE=debian
    - HOME_URL="https://www.ubuntu.com/"
    - SUPPORT_URL="https://help.ubuntu.com/"
    - BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
    - PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
    - UBUNTU_CODENAME=jammy
- 컨트롤러: OpenCR R1.0
- 모터: Dynamixel XM430-W210 (ID 1, Protocol 2.0, 1 Mbps)
- 연결: USB 시리얼 /dev/ttyACM0 (115200 8N1)
- 툴: arduino-cli 1.5.1, opencr_ld 1.0.4

### 실행 방법
1. 환경 변수 설정
```bash
   export BASE="$HOME/pa-opencr-build"
```
   
2. 컴파일
  ```bash
   "$BASE/bin/arduino-cli" --config-file "$BASE/arduino-cli.yaml" \
  compile --fqbn ROBOTIS:OpenCR:OpenCR --jobs 1 \
  --output-dir "$BASE/output" \
  "$BASE/sketches/opencr_position_p"
  ```

3. 업로드
  ```bash
  UPLOADER="$BASE/uploader-src/arduino/opencr_develop/opencr_ld/opencr_ld"
  "$UPLOADER" /dev/ttyACM0 115200 \
  "$BASE/output/opencr_position_p.ino.bin" 1
  ```

4. 실행/모니터
```bash
   python3 -m serial.tools.miniterm /dev/ttyACM0 115200 --eol LF -e
   명령 형식: s <Kp> <속도> <각도>
```

### 결과 파일
- [lv2_module1/results/01_environments](lv2_module1/results/01_environments) : 환경 확인
- [lv2_module1/results/02_upload](lv2_module1/results/02_upload) : 업로드 기록
- [lv2_module1/results/03_run_A](lv2_module1/results/03_run_A) : 실행 A 로그
- [lv2_module1/results/04_run_B](lv2_module1/results/04_run_B) : 실행 B 로그
- [lv2_module1/report.md](lv2_module1/report.md) : 문제별 해석

---

## 모듈 3. 설정값에 따른 Mask와 검출 결과 변화 분석

### 환경
- 호스트: 개발 PC, Ubuntu 24.04.5 LTS
- ROS 2 Lyrical, OpenCV 4.6.0, Python 3.12.3, rqt_image_view 2.0.5
- 카메라: Intel RealSense D435 (424x240x30, rosbag 녹화에만 사용)
- 비전 노드: 팀 프로젝트 `visualkhh/Lv2_noon_Assignment` 커밋 `130c1ba`의 `lv2_module5/ros2_ws/src/realsense` (`perception_node`)

### 실행 방법
```bash
# 터미널 1: 비전 노드 (카메라 끔, 모터 제어 노드 없음)
source /opt/ros/lyrical/setup.bash
source ~/Lv2_noon_Assignment/lv2_module5/ros2_ws/install/setup.bash
ros2 launch realsense realsense.launch.py use_camera:=false

# 터미널 2: rosbag 반복 재생
ros2 bag play ~/Lv2_noon_Assignment/lv2_module5/recordings/20261012_102611_no1_pillar_v1 \
  --topics /camera/camera/color/image_raw /camera/camera/color/camera_info -l

# 터미널 3: 이미지 뷰어
ros2 run rqt_image_view rqt_image_view /camera/camera/color/image_raw
```

### 결과 파일
- [lv2_module3/report.md](lv2_module3/report.md) : 토픽 구성, 실험 가설·통제 조건, A·B 결과 비교, 최종 선택값
- [lv2_module3/results/](lv2_module3/results/) : 토픽 정보, 실험별 A·B 적용값·수신 이미지·검출 로그, 목표 없음 확인 결과
- [lv2_module3/tools/](lv2_module3/tools/) : 토픽 수신·저장 도구와 실험 실행 스크립트
