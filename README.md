# physicalai-lv2-taeyoungMoon
PA과정 Level 2 과제 제출을 위한 저장소

## 환경
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

## 실행 방법
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

## 결과 파일
- results/01_environment.txt : 환경 확인
- results/02_upload.txt : 업로드 기록
- results/03_run_A.txt : 실행 A 로그
- results/04_run_B.txt : 실행 B 로그
- report.md : 문제별 해석
