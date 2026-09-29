# Lv2. 모듈 ①과제 - OpenCR·다이나믹셀 통합 4문제

## 공통 수행 조건

라즈베리파이 Ubuntu Server 22.04, OpenCR 1.0, 다이나믹셀 1개를 사용합니다. PC는 SSH 접속에만 사용하고, OpenCR 업로드와 시리얼 송수신·로그 저장은 모두 라즈베리파이에서 수행해야 합니다. 모터 모델에 맞는 전원과 통신 방식을 확인하세요.

제공된 P 제어 예제를 사용할 수 있습니다. 펌웨어 컴파일, 새 PID 구현, 외부 ADC·엔코더 배선, PWM 직접 구동과 micro-ROS 설치는 필수 요구사항이 아닙니다. 수행 전에 장비 고정, 이동 범위와 정지 방법을 확인하세요.

환경 준비가 완료된 뒤 전체 4문제의 예상 수행 시간은 약 90분입니다. 최초 환경 구성 시간은 별도입니다. 오늘은 [과제 1 발제문서](과제1_발제_SSH_라즈베리파이_OpenCR.md)의 요구사항만 수행합니다.




## 문제 1. 목표 입력과 응답 확인
라즈베리파이의 원격 수행 환경을 구성하고, OpenCR에 펌웨어를 업로드한 뒤 한 개의 작은 상대 목표각에 대한 응답을 기록하세요. 목표값·측정값·제어 출력과 단위를 구분하고 실제 움직임을 설명하세요.

제출 증거: 환경 및 업로드 확인, 설정, 목표 변경 이후 5행 이상의 실행 A 기록과 정지 확인.

 1. 원격 수행 환경 구성
 ```
- 라즈베리 파이 OS
```     
```bash
pa10@pa10:~$ cat /etc/os-release
PRETTY_NAME="Ubuntu 22.04.5 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
VERSION="22.04.5 LTS (Jammy Jellyfish)"
VERSION_CODENAME=jammy
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=jammy
```
    - ssh 원격 접속 
 ```bash
 pa9@pa9-Legion-Pro-5-16IAX10:~$ ssh pa10@pa10.local
Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 5.15.0-1061-raspi aarch64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

Last login: Tue Sep 22 14:09:49 2026 from 10.2.17.14
```
    - OpenCR USB 인식과 포트 접근 권한
```bash
pa10@pa10:~$ lsusb
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 008: ID 0483:5740 STMicroelectronics Virtual COM Port
Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub

pa10@pa10:~$ ls -l /dev/ttyACM*
crw-rw---- 1 root dialout 166, 0 Sep 23 11:07 /dev/ttyACM0

pa10@pa10:~$ groups
pa10 adm dialout cdrom floppy sudo audio dip video plugdev netdev lxd
```

- 장치: 라즈베리파이, OpenCR 보드, 다이나믹셀(XM430-W210, ID=1, baud rate=1000000)
- 포트:
1. OpenCR <-> 라즈베리 파이: /dev/ttyACM0
2. 모터 <-> OpenCE: baud 1000000
```
[작업 장치 및 포트 기록]

- 호스트: Raspberry Pi (OS: Ubuntu 22.04.5 LTS)
- 컨트롤러: OpenCR R1.0 (Board Ver 0x17020800)
  · 연결 포트: /dev/ttyACM0
  · USB 인식: ID 0483:5740 (STMicroelectronics Virtual COM Port / ROBOTIS OpenCR)
  · 통신 속도(PC↔OpenCR): 115200 bps
- 모터: Dynamixel XM430-W210 (model 1030)
  · ID: 1
  · Protocol: 2.0
  · 통신 속도(OpenCR↔모터): 1,000,000 bps (1 Mbps)
```

2. OpenCR 펌웨어 업로드
```
- 펌웨어 컴파일
```
```bash
pa10@pa10:~$ "$BASE/bin/arduino-cli" --config-file "$BASE/arduino-cli.yaml" \
  compile --fqbn ROBOTIS:OpenCR:OpenCR --jobs 1 \
  --output-dir "$BASE/output" \
  "$BASE/sketches/opencr_position_p"
Sketch uses 104296 bytes (13%) of program storage space. Maximum is 786432 bytes.
Global variables use 40620 bytes of dynamic memory.
```

    - 펌웨어 업로드
```bash
pa10@pa10:~$ UPLOADER="$BASE/uploader-src/arduino/opencr_develop/opencr_ld/opencr_ld"
"$UPLOADER" /dev/ttyACM0 115200 \
  "$BASE/output/opencr_position_p.ino.bin" 1
opencr_ld ver 1.0.4
opencr_ld_main 
>>
file name : /home/pa10/pa-opencr-build/output/opencr_position_p.ino.bin 
file size : 102 KB
Open port OK
Clear Buffer Start
Clear Buffer End
Board Name : OpenCR R1.0
Board Ver  : 0x17020800
Board Rev  : 0x00000000
>>
flash_erase : 0 : 0.855000 sec
flash_write : 0 : 1.179000 sec 
CRC OK 9B81E2 9B81E2 0.004000 sec
[OK] Download 
jump_to_fw 
jump finished
```
```
- miniterm 실행
```
```bash
python3 -m serial.tools.miniterm "$PORT" 115200 --eol LF -e
--- Miniterm on /dev/ttyACM0  115200,8,N,1 ---
--- Quit: Ctrl+] | Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H ---
Invalid setting. Finite Kp, positive speed or max, angle -90..90. Use k/v/a or s <Kp> <speed_deg_s|max> <angle_deg>.
```

3. 목표 입력과 응답기록

```
- s 6.5 5 20
```
```bash
target_deg:20.000       position_deg:0.000      error_deg:20.000        p_deg_s:130.000 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:130.000       speed_deg_s:0.000       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.000
target_deg:20.000       position_deg:0.176      error_deg:19.824        p_deg_s:128.857 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:128.857       speed_deg_s:0.000       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.100
target_deg:20.000       position_deg:0.615      error_deg:19.385        p_deg_s:126.001 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:126.001       speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.200
target_deg:20.000       position_deg:1.143      error_deg:18.857        p_deg_s:122.573 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:122.573       speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.300
target_deg:20.000       position_deg:1.494      error_deg:18.506        p_deg_s:120.288 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:120.288       speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.400
target_deg:20.000       position_deg:1.934      error_deg:18.066        p_deg_s:117.432 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:117.432       speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.500
target_deg:20.000       position_deg:2.373      error_deg:17.627        p_deg_s:114.575 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:114.575       speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.600
target_deg:20.000       position_deg:2.813      error_deg:17.187        p_deg_s:111.719 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:111.719       speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.700
target_deg:20.000       position_deg:3.252      error_deg:16.748        p_deg_s:108.862 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:108.862       speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.800
target_deg:20.000       position_deg:3.516      error_deg:16.484        p_deg_s:107.148 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:107.148       speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.900
target_deg:20.000       position_deg:4.043      error_deg:15.957        p_deg_s:103.721 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:103.721       speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.000
target_deg:20.000       position_deg:4.395      error_deg:15.605        p_deg_s:101.436 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:101.436       speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.100
target_deg:20.000       position_deg:4.834      error_deg:15.166        p_deg_s:98.579  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:98.579        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.200
target_deg:20.000       position_deg:5.273      error_deg:14.727        p_deg_s:95.723  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:95.723        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.300
target_deg:20.000       position_deg:5.537      error_deg:14.463        p_deg_s:94.009  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:94.009        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.400
target_deg:20.000       position_deg:6.064      error_deg:13.936        p_deg_s:90.581  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:90.581        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.500
target_deg:20.000       position_deg:6.416      error_deg:13.584        p_deg_s:88.296  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:88.296        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.600
target_deg:20.000       position_deg:6.943      error_deg:13.057        p_deg_s:84.868  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:84.868        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.700
target_deg:20.000       position_deg:7.295      error_deg:12.705        p_deg_s:82.583  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:82.583        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.800
target_deg:20.000       position_deg:7.734      error_deg:12.266        p_deg_s:79.727  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:79.727        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.900
target_deg:20.000       position_deg:8.086      error_deg:11.914        p_deg_s:77.441  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:77.441        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.000
target_deg:20.000       position_deg:8.525      error_deg:11.475        p_deg_s:74.585  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:74.585        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.100
target_deg:20.000       position_deg:8.965      error_deg:11.035        p_deg_s:71.729  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:71.729        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.200
target_deg:20.000       position_deg:9.316      error_deg:10.684        p_deg_s:69.443  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:69.443        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.300
target_deg:20.000       position_deg:9.844      error_deg:10.156        p_deg_s:66.016  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:66.016        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.400
target_deg:20.000       position_deg:10.195     error_deg:9.805 p_deg_s:63.730  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:63.730        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.500
target_deg:20.000       position_deg:10.635     error_deg:9.365 p_deg_s:60.874  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:60.874        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.600
target_deg:20.000       position_deg:10.986     error_deg:9.014 p_deg_s:58.589  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:58.589        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.700
target_deg:20.000       position_deg:11.338     error_deg:8.662 p_deg_s:56.304  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:56.304        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.800
target_deg:20.000       position_deg:11.777     error_deg:8.223 p_deg_s:53.447  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:53.447        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.900
target_deg:20.000       position_deg:12.129     error_deg:7.871 p_deg_s:51.162  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:51.162        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.000
target_deg:20.000       position_deg:12.656     error_deg:7.344 p_deg_s:47.734  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:47.734        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.100
target_deg:20.000       position_deg:12.920     error_deg:7.080 p_deg_s:46.020  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:46.020        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.200
target_deg:20.000       position_deg:13.447     error_deg:6.553 p_deg_s:42.593  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:42.593        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.300
target_deg:20.000       position_deg:13.799     error_deg:6.201 p_deg_s:40.308  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:40.308        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.400
target_deg:20.000       position_deg:14.150     error_deg:5.850 p_deg_s:38.022  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:38.022        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.500
target_deg:20.000       position_deg:14.590     error_deg:5.410 p_deg_s:35.166  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:35.166        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.600
target_deg:20.000       position_deg:14.941     error_deg:5.059 p_deg_s:32.881  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:32.881        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.700
target_deg:20.000       position_deg:15.469     error_deg:4.531 p_deg_s:29.453  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:29.453        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.800
target_deg:20.000       position_deg:15.732     error_deg:4.268 p_deg_s:27.739  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:27.739        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.900
target_deg:20.000       position_deg:16.260     error_deg:3.740 p_deg_s:24.312  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:24.312        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:6.000
target_deg:20.000       position_deg:16.611     error_deg:3.389 p_deg_s:22.026  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:22.026        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:6.100
target_deg:20.000       position_deg:17.051     error_deg:2.949 p_deg_s:19.170  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:19.170        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:6.200
target_deg:20.000       position_deg:17.578     error_deg:2.422 p_deg_s:15.742  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:15.742        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:6.300
target_deg:20.000       position_deg:17.842     error_deg:2.158 p_deg_s:14.028  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:14.028        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:6.400
target_deg:20.000       position_deg:18.281     error_deg:1.719 p_deg_s:11.172  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:11.172        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:6.500
target_deg:20.000       position_deg:18.545     error_deg:1.455 p_deg_s:9.458   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:9.458 speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.003    kp:6.5000  ki:0.0000       kd:0.0000       t_s:6.600
target_deg:20.000       position_deg:19.072     error_deg:0.928 p_deg_s:6.030   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:6.030 speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.002    kp:6.5000  ki:0.0000       kd:0.0000       t_s:6.700
target_deg:20.000       position_deg:19.424     error_deg:0.576 p_deg_s:3.745   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:3.745 speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001    kp:6.5000  ki:0.0000       kd:0.0000       t_s:6.800
target_deg:20.000       position_deg:19.775     error_deg:0.225 p_deg_s:1.460   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:1.460 speed_deg_s:2.748       u_deg_s:1.374   v_limit_deg_s:5.000     dt_ms:10.000    kp:6.5000  ki:0.0000       kd:0.0000       t_s:6.900
target_deg:20.000       position_deg:19.863     error_deg:0.137 p_deg_s:0.000   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:0.000 speed_deg_s:1.374       u_deg_s:0.000   v_limit_deg_s:5.000     dt_ms:10.003    kp:6.5000  ki:0.0000       kd:0.0000       t_s:7.000
xSTOP: user
```

4. 결과 설명
```
<s 6.5 5 20>
- 예제 이름: opencr_position_p
- 모터 모델: 다이나믹셀(XM430-W210)
- 모터 ID: 1
- 게인(Kp): 6.5
- 목표각: 20도 (°)
- 속도 상한: 5 deg/s 

- 목표값: 20도 → 20 도(°)
- 측정값: 19.863도 → 19.863 도(°)
- 제어 출력: 0 ~ 4.122 deg/s 

P제어 만을 이용한 명령 입력 후, 4.122deg/s 속도로 목표인 20도각에 가까워지는 것을 볼 수 있습니다. 오버슈팅은 없었지만 P제어 한계로 인해 목표각에 정확히 도달하지 못하고 19.863도에서 정상 상태 오차가 발생했습니다.
```

## 문제 2. 오차와 피드백 해석 
실행 A의 초기·중간·마지막 시점에서 목표각과 현재각을 선택하고 오차 = 목표각 - 현재각을 계산하세요. 오차 크기의 변화를 설명하고, 위치 측정값을 얻는 센서와 OpenCR까지의 통신 경로를 적으세요. 목표가 +30°이고 현재각이 +35°인 경우의 오차 부호와 양의 Kp에 의한 보정 방향을 설명하세요.

제출 증거: 시점·목표각·현재각·오차 표와 짧은 설명. 새 실행은 필요하지 않습니다.
```
<s 6.5 5 20>
출력 데이터:
- 초기 시점
target_deg:20.000       position_deg:0.176      error_deg:19.824        p_deg_s:128.857 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:128.857       speed_deg_s:0.000       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.100

 목표각: 20.000°
 현재각: 0.175°
 오차 = 목표각 - 현재각 = 19.824°

- 중간 시점
target_deg:20.000       position_deg:6.064      error_deg:13.936        p_deg_s:90.581  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:90.581        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.500

 목표각: 20.000°
 현재각: 6.064°
 오차 = 목표각 - 현재각 = 13.936°

- 마지막 시점
target_deg:20.000       position_deg:19.863     error_deg:0.137 p_deg_s:0.000   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:0.000 speed_deg_s:1.374       u_deg_s:0.000   v_limit_deg_s:5.000     dt_ms:10.003    kp:6.5000  ki:0.0000       kd:0.0000       t_s:7.000

 목표각: 20.000°
 현재각: 19.863°
 오차 = 목표각 - 현재각 = 0.137°

 ***오차 크기의 변화
 목표 변경(t≈2.0s) 직후 오차는 20.000°로 가장 컸고, 모터가 목표로 접근하면서 오차가 점차 줄어들었습니다. 속도 상한(5 deg/s)에 걸려 일정한 속도로 이동하는 동안 오차는 거의 선형으로 감소했고(예: t=2.0s에서 20.000° → t=5.0s에서 7.871°), 목표 근처에서는 감속하며 더 천천히 줄어들었습니다. 최종적으로 19.863°에서 멈춰 약 0.137°의 정상상태 오차가 남았습니다.
 ```

 ```bash
 위치 측정 센서와 OpenCR까지의 통신 경로
 
 - 센서: 다이나믹셀(XM430-W210) 내장 엔코더 (4096 tick/회전)
 - 통신 경로:
    내장 엔코더 -> 모터 내부 MCU -> DXL 버스 (TTL 반이중, Protocol 2.0, 1Mbps) -> OpenCR(Serial3 UART + 84번 핀)

    *OpenCR이 모터의 PRESENT_POSITION 레지스터를 요청/응답 방식으로 읽어옵니다.
```

```
목표가 +30°이고 현재각이 +35°인 경우의 오차 부호와 양의 Kp에 의한 보정 방향

목표각 = +30°
현재각 = +35°

오차 = 목표각 - 현재각 = -5°
오차 부호 -> -(음수)
Kp에 의한 보정 방향 = - (음수 방향으로 작용)

P제어 = Kp * error 이므로, 출력은 음수가 되어 현재각을 줄이는 방향으로 모터를 회전시킵니다.
즉 오버슈팅이 발생했을 때, 음수가 된 오차가 자동으로 반대 방향을 만들어 목표로 가깝게 보정합니다.
```

## 문제 3. P게인 변경에 따른 응답 비교
제공 P 제어 예제에서 과제용으로 검증된 두 Kp 설정으로 실행 A와 B를 비교하세요. 목표각·속도 상한·부하·측정 주기를 유지하고, 시작 자세와 이동 여유를 맞추세요. 두 기록의 같은 경과 시간에서 현재각과 목표 초과 여부를 비교하고, 차이를 근거와 함께 설명하세요.

변경한 게인이 OpenCR 위치 제어 게인인지 다이나믹셀 내부 게인인지 구분하고 I항과 D항의 역할을 각각 한 문장으로 설명하세요. 최적 게인 탐색이나 I·D 튜닝은 요구하지 않습니다.

- 실행 A
  - <s 6.5 5 20>
  - START: current position = 0 deg.
  - P SET Kp=6.5000, Ki=0.0000, Kd=0.0000, speed_limit_deg_s=5.000, angle_deg=20.000
```bash
target_deg:20.000       position_deg:0.000      error_deg:20.000        p_deg_s:130.000 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:130.000       speed_deg_s:0.000       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.000
target_deg:20.000       position_deg:0.176      error_deg:19.824        p_deg_s:128.857 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:128.857       speed_deg_s:0.000       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.100
target_deg:20.000       position_deg:0.615      error_deg:19.385        p_deg_s:126.001 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:126.001       speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.200
target_deg:20.000       position_deg:1.143      error_deg:18.857        p_deg_s:122.573 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:122.573       speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.300
target_deg:20.000       position_deg:1.494      error_deg:18.506        p_deg_s:120.288 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:120.288       speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.400
target_deg:20.000       position_deg:1.934      error_deg:18.066        p_deg_s:117.432 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:117.432       speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.500
target_deg:20.000       position_deg:2.373      error_deg:17.627        p_deg_s:114.575 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:114.575       speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.600
target_deg:20.000       position_deg:2.813      error_deg:17.187        p_deg_s:111.719 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:111.719       speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.700
target_deg:20.000       position_deg:3.252      error_deg:16.748        p_deg_s:108.862 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:108.862       speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.800
target_deg:20.000       position_deg:3.516      error_deg:16.484        p_deg_s:107.148 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:107.148       speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:2.900
target_deg:20.000       position_deg:4.043      error_deg:15.957        p_deg_s:103.721 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:103.721       speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.000
target_deg:20.000       position_deg:4.395      error_deg:15.605        p_deg_s:101.436 i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:101.436       speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.100
target_deg:20.000       position_deg:4.834      error_deg:15.166        p_deg_s:98.579  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:98.579        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.200
target_deg:20.000       position_deg:5.273      error_deg:14.727        p_deg_s:95.723  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:95.723        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.300
target_deg:20.000       position_deg:5.537      error_deg:14.463        p_deg_s:94.009  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:94.009        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.400
target_deg:20.000       position_deg:6.064      error_deg:13.936        p_deg_s:90.581  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:90.581        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.500
target_deg:20.000       position_deg:6.416      error_deg:13.584        p_deg_s:88.296  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:88.296        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.600
target_deg:20.000       position_deg:6.943      error_deg:13.057        p_deg_s:84.868  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:84.868        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.700
target_deg:20.000       position_deg:7.295      error_deg:12.705        p_deg_s:82.583  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:82.583        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.800
target_deg:20.000       position_deg:7.734      error_deg:12.266        p_deg_s:79.727  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:79.727        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:3.900
target_deg:20.000       position_deg:8.086      error_deg:11.914        p_deg_s:77.441  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:77.441        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.000
target_deg:20.000       position_deg:8.525      error_deg:11.475        p_deg_s:74.585  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:74.585        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.100
target_deg:20.000       position_deg:8.965      error_deg:11.035        p_deg_s:71.729  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:71.729        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.200
target_deg:20.000       position_deg:9.316      error_deg:10.684        p_deg_s:69.443  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:69.443        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.300
target_deg:20.000       position_deg:9.844      error_deg:10.156        p_deg_s:66.016  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:66.016        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.400
target_deg:20.000       position_deg:10.195     error_deg:9.805 p_deg_s:63.730  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:63.730        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.500
target_deg:20.000       position_deg:10.635     error_deg:9.365 p_deg_s:60.874  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:60.874        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.600
target_deg:20.000       position_deg:10.986     error_deg:9.014 p_deg_s:58.589  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:58.589        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.700
target_deg:20.000       position_deg:11.338     error_deg:8.662 p_deg_s:56.304  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:56.304        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.800
target_deg:20.000       position_deg:11.777     error_deg:8.223 p_deg_s:53.447  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:53.447        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:4.900
target_deg:20.000       position_deg:12.129     error_deg:7.871 p_deg_s:51.162  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:51.162        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.000
target_deg:20.000       position_deg:12.656     error_deg:7.344 p_deg_s:47.734  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:47.734        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.100
target_deg:20.000       position_deg:12.920     error_deg:7.080 p_deg_s:46.020  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:46.020        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.200
target_deg:20.000       position_deg:13.447     error_deg:6.553 p_deg_s:42.593  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:42.593        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.300
target_deg:20.000       position_deg:13.799     error_deg:6.201 p_deg_s:40.308  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:40.308        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.400
target_deg:20.000       position_deg:14.150     error_deg:5.850 p_deg_s:38.022  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:38.022        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.500
target_deg:20.000       position_deg:14.590     error_deg:5.410 p_deg_s:35.166  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:35.166        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.600
target_deg:20.000       position_deg:14.941     error_deg:5.059 p_deg_s:32.881  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:32.881        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.700
target_deg:20.000       position_deg:15.469     error_deg:4.531 p_deg_s:29.453  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:29.453        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.800
target_deg:20.000       position_deg:15.732     error_deg:4.268 p_deg_s:27.739  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:27.739        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:5.900
target_deg:20.000       position_deg:16.260     error_deg:3.740 p_deg_s:24.312  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:24.312        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:6.000
target_deg:20.000       position_deg:16.611     error_deg:3.389 p_deg_s:22.026  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:22.026        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:6.100
target_deg:20.000       position_deg:17.051     error_deg:2.949 p_deg_s:19.170  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:19.170        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:6.200
target_deg:20.000       position_deg:17.578     error_deg:2.422 p_deg_s:15.742  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:15.742        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:6.5000       ki:0.0000       kd:0.0000       t_s:6.300
target_deg:20.000       position_deg:17.842     error_deg:2.158 p_deg_s:14.028  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:14.028        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:6.400
target_deg:20.000       position_deg:18.281     error_deg:1.719 p_deg_s:11.172  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:11.172        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:6.5000       ki:0.0000       kd:0.0000       t_s:6.500
target_deg:20.000       position_deg:18.545     error_deg:1.455 p_deg_s:9.458   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:9.458 speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.003    kp:6.5000  ki:0.0000       kd:0.0000       t_s:6.600
target_deg:20.000       position_deg:19.072     error_deg:0.928 p_deg_s:6.030   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:6.030 speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.002    kp:6.5000  ki:0.0000       kd:0.0000       t_s:6.700
target_deg:20.000       position_deg:19.424     error_deg:0.576 p_deg_s:3.745   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:3.745 speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001    kp:6.5000  ki:0.0000       kd:0.0000       t_s:6.800
target_deg:20.000       position_deg:19.775     error_deg:0.225 p_deg_s:1.460   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:1.460 speed_deg_s:2.748       u_deg_s:1.374   v_limit_deg_s:5.000     dt_ms:10.000    kp:6.5000  ki:0.0000       kd:0.0000       t_s:6.900
target_deg:20.000       position_deg:19.863     error_deg:0.137 p_deg_s:0.000   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:0.000 speed_deg_s:1.374       u_deg_s:0.000   v_limit_deg_s:5.000     dt_ms:10.003    kp:6.5000  ki:0.0000       kd:0.0000       t_s:7.000
xSTOP: user
```

- 실행 B
  - <s 2 5 20>
  - START: current position = 0 deg.
  - P SET Kp=2.0000, Ki=0.0000, Kd=0.0000, speed_limit_deg_s=5.000, angle_deg=20.000
```bash
target_deg:20.000       position_deg:0.000      error_deg:20.000        p_deg_s:40.000  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:40.000        speed_deg_s:0.000       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:2.000
target_deg:20.000       position_deg:0.176      error_deg:19.824        p_deg_s:39.648  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:39.648        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:2.100
target_deg:20.000       position_deg:0.615      error_deg:19.385        p_deg_s:38.770  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:38.770        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:2.0000       ki:0.0000       kd:0.0000       t_s:2.200
target_deg:20.000       position_deg:0.879      error_deg:19.121        p_deg_s:38.242  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:38.242        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:2.300
target_deg:20.000       position_deg:1.406      error_deg:18.594        p_deg_s:37.187  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:37.187        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:2.0000       ki:0.0000       kd:0.0000       t_s:2.400
target_deg:20.000       position_deg:1.758      error_deg:18.242        p_deg_s:36.484  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:36.484        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:2.500
target_deg:20.000       position_deg:2.197      error_deg:17.803        p_deg_s:35.605  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:35.605        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:2.600
target_deg:20.000       position_deg:2.725      error_deg:17.275        p_deg_s:34.551  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:34.551        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:2.0000       ki:0.0000       kd:0.0000       t_s:2.700
target_deg:20.000       position_deg:2.988      error_deg:17.012        p_deg_s:34.023  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:34.023        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:2.0000       ki:0.0000       kd:0.0000       t_s:2.800
target_deg:20.000       position_deg:3.516      error_deg:16.484        p_deg_s:32.969  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:32.969        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:2.0000       ki:0.0000       kd:0.0000       t_s:2.900
target_deg:20.000       position_deg:3.779      error_deg:16.221        p_deg_s:32.441  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:32.441        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:3.000
target_deg:20.000       position_deg:4.307      error_deg:15.693        p_deg_s:31.387  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:31.387        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:3.100
target_deg:20.000       position_deg:4.658      error_deg:15.342        p_deg_s:30.684  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:30.684        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:3.200
target_deg:20.000       position_deg:5.098      error_deg:14.902        p_deg_s:29.805  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:29.805        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:3.300
target_deg:20.000       position_deg:5.537      error_deg:14.463        p_deg_s:28.926  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:28.926        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:3.400
target_deg:20.000       position_deg:5.889      error_deg:14.111        p_deg_s:28.223  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:28.223        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:2.0000       ki:0.0000       kd:0.0000       t_s:3.500
target_deg:20.000       position_deg:6.416      error_deg:13.584        p_deg_s:27.168  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:27.168        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:3.600
target_deg:20.000       position_deg:6.680      error_deg:13.320        p_deg_s:26.641  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:26.641        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:3.700
target_deg:20.000       position_deg:7.295      error_deg:12.705        p_deg_s:25.410  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:25.410        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:3.800
target_deg:20.000       position_deg:7.646      error_deg:12.354        p_deg_s:24.707  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:24.707        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:3.900
target_deg:20.000       position_deg:8.086      error_deg:11.914        p_deg_s:23.828  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:23.828        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:4.000
target_deg:20.000       position_deg:8.525      error_deg:11.475        p_deg_s:22.949  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:22.949        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:4.100
target_deg:20.000       position_deg:8.877      error_deg:11.123        p_deg_s:22.246  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:22.246        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:2.0000       ki:0.0000       kd:0.0000       t_s:4.200
target_deg:20.000       position_deg:9.316      error_deg:10.684        p_deg_s:21.367  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:21.367        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:2.0000       ki:0.0000       kd:0.0000       t_s:4.300
target_deg:20.000       position_deg:9.668      error_deg:10.332        p_deg_s:20.664  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:20.664        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.002       kp:2.0000       ki:0.0000       kd:0.0000       t_s:4.400
target_deg:20.000       position_deg:10.195     error_deg:9.805 p_deg_s:19.609  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:19.609        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.002       kp:2.0000       ki:0.0000       kd:0.0000       t_s:4.500
target_deg:20.000       position_deg:10.547     error_deg:9.453 p_deg_s:18.906  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:18.906        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.002       kp:2.0000       ki:0.0000       kd:0.0000       t_s:4.600
target_deg:20.000       position_deg:10.986     error_deg:9.014 p_deg_s:18.027  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:18.027        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:2.0000       ki:0.0000       kd:0.0000       t_s:4.700
target_deg:20.000       position_deg:11.426     error_deg:8.574 p_deg_s:17.148  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:17.148        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.003       kp:2.0000       ki:0.0000       kd:0.0000       t_s:4.800
target_deg:20.000       position_deg:11.777     error_deg:8.223 p_deg_s:16.445  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:16.445        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:4.900
target_deg:20.000       position_deg:12.217     error_deg:7.783 p_deg_s:15.566  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:15.566        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:5.000
target_deg:20.000       position_deg:12.568     error_deg:7.432 p_deg_s:14.863  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:14.863        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:2.0000       ki:0.0000       kd:0.0000       t_s:5.100
target_deg:20.000       position_deg:13.096     error_deg:6.904 p_deg_s:13.809  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:13.809        speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.002       kp:2.0000       ki:0.0000       kd:0.0000       t_s:5.200
target_deg:20.000       position_deg:13.447     error_deg:6.553 p_deg_s:13.105  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:13.105        speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001       kp:2.0000       ki:0.0000       kd:0.0000       t_s:5.300
target_deg:20.000       position_deg:13.887     error_deg:6.113 p_deg_s:12.227  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:12.227        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:5.400
target_deg:20.000       position_deg:14.326     error_deg:5.674 p_deg_s:11.348  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:11.348        speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:5.500
target_deg:20.000       position_deg:14.678     error_deg:5.322 p_deg_s:10.645  i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:10.645        speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000       kp:2.0000       ki:0.0000       kd:0.0000       t_s:5.600
target_deg:20.000       position_deg:15.205     error_deg:4.795 p_deg_s:9.590   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:9.590 speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.002    kp:2.0000  ki:0.0000       kd:0.0000       t_s:5.700
target_deg:20.000       position_deg:15.557     error_deg:4.443 p_deg_s:8.887   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:8.887 speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.002    kp:2.0000  ki:0.0000       kd:0.0000       t_s:5.800
target_deg:20.000       position_deg:15.996     error_deg:4.004 p_deg_s:8.008   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:8.008 speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001    kp:2.0000  ki:0.0000       kd:0.0000       t_s:5.900
target_deg:20.000       position_deg:16.348     error_deg:3.652 p_deg_s:7.305   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:7.305 speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.003    kp:2.0000  ki:0.0000       kd:0.0000       t_s:6.000
target_deg:20.000       position_deg:16.787     error_deg:3.213 p_deg_s:6.426   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:6.426 speed_deg_s:5.496       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001    kp:2.0000  ki:0.0000       kd:0.0000       t_s:6.100
target_deg:20.000       position_deg:17.227     error_deg:2.773 p_deg_s:5.547   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:5.547 speed_deg_s:1.374       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.000    kp:2.0000  ki:0.0000       kd:0.0000       t_s:6.200
target_deg:20.000       position_deg:17.578     error_deg:2.422 p_deg_s:4.844   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:4.844 speed_deg_s:4.122       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001    kp:2.0000  ki:0.0000       kd:0.0000       t_s:6.300
target_deg:20.000       position_deg:18.018     error_deg:1.982 p_deg_s:3.965   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:3.965 speed_deg_s:2.748       u_deg_s:4.122   v_limit_deg_s:5.000     dt_ms:10.001    kp:2.0000  ki:0.0000       kd:0.0000       t_s:6.400
target_deg:20.000       position_deg:18.369     error_deg:1.631 p_deg_s:3.262   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:3.262 speed_deg_s:2.748       u_deg_s:2.748   v_limit_deg_s:5.000     dt_ms:10.002    kp:2.0000  ki:0.0000       kd:0.0000       t_s:6.500
target_deg:20.000       position_deg:18.721     error_deg:1.279 p_deg_s:2.559   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:2.559 speed_deg_s:2.748       u_deg_s:2.748   v_limit_deg_s:5.000     dt_ms:10.002    kp:2.0000  ki:0.0000       kd:0.0000       t_s:6.600
target_deg:20.000       position_deg:18.896     error_deg:1.104 p_deg_s:2.207   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:2.207 speed_deg_s:1.374       u_deg_s:2.748   v_limit_deg_s:5.000     dt_ms:10.002    kp:2.0000  ki:0.0000       kd:0.0000       t_s:6.700
target_deg:20.000       position_deg:19.072     error_deg:0.928 p_deg_s:1.855   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:1.855 speed_deg_s:0.000       u_deg_s:1.374   v_limit_deg_s:5.000     dt_ms:10.001    kp:2.0000  ki:0.0000       kd:0.0000       t_s:6.800
target_deg:20.000       position_deg:19.248     error_deg:0.752 p_deg_s:1.504   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:1.504 speed_deg_s:1.374       u_deg_s:1.374   v_limit_deg_s:5.000     dt_ms:10.001    kp:2.0000  ki:0.0000       kd:0.0000       t_s:6.900
target_deg:20.000       position_deg:19.336     error_deg:0.664 p_deg_s:1.328   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:1.328 speed_deg_s:0.000       u_deg_s:1.374   v_limit_deg_s:5.000     dt_ms:10.000    kp:2.0000  ki:0.0000       kd:0.0000       t_s:7.000
target_deg:20.000       position_deg:19.512     error_deg:0.488 p_deg_s:0.977   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:0.977 speed_deg_s:1.374       u_deg_s:1.374   v_limit_deg_s:5.000     dt_ms:10.002    kp:2.0000  ki:0.0000       kd:0.0000       t_s:7.100
target_deg:20.000       position_deg:19.600     error_deg:0.400 p_deg_s:0.801   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:0.801 speed_deg_s:0.000       u_deg_s:1.374   v_limit_deg_s:5.000     dt_ms:10.001    kp:2.0000  ki:0.0000       kd:0.0000       t_s:7.200
target_deg:20.000       position_deg:19.688     error_deg:0.312 p_deg_s:0.625   i_deg_s:0.000   d_deg_s:0.000      pid_deg_s:0.625 speed_deg_s:0.000       u_deg_s:0.000   v_limit_deg_s:5.000     dt_ms:10.001    kp:2.0000  ki:0.0000       kd:0.0000       t_s:7.300
```

- 실행 A와 B의 비교

| 경과 시간(s) | A 현재각(°)<br>Kp=6.5 | A 목표 초과 | B 현재각(°)<br>Kp=2 | B 목표 초과 |
|:---:|:---:|:---:|:---:|:---:|
| 2.0 | 0.000 | 미도달 | 0.000 | 미도달 |
| 3.0 | 4.043 | 미도달 | 3.779 | 미도달 |
| 4.0 | 8.086 | 미도달 | 8.086 | 미도달 |
| 5.0 | 12.129 | 미도달 | 12.217 | 미도달 |
| 6.0 | 16.260 | 미도달 | 16.348 | 미도달 |
| 7.0 | 19.863 | 미도달 | 19.336 | 미도달 |
| 7.3 | 종료(t=7.0 정지) | — | 19.688 | 미도달 |

  - 공통점: Kp 값이 6.5와 2를 주었을 때 모두 오버슈팅이 발생하지 않았습니다.
  - 차이점: 
      - 실행 A는 약 7.0초에 정상상태에 도달하여 19.863°에서 정지했고, 목표 20°에 완전히 도달하지 못한 채 0.137°의 정상상태 오차가 남았습니다. 
      
      - 실행 B는 약 7.3초에 정상상태에 도달하여 19.688°에서 정지했고, 목표 20°에 완전히 도달하지 못한 채 0.312°의 정상상태 오차가 남았습니다.
      - 정착 시간은 목표(20°)가 인가된 t=2.0s부터 오차가 ±0.2°(deadband) 이내로 진입한 시점까지로 정의한다.
        - A: t=7.0s 진입 → 정착 시간 약 5.0초 (정상상태 오차 0.137°)
        - B: 기록 구간 내(t=7.3s, 오차 0.312°) ±0.2° 이내 미진입 -> 정상 시간 약 5.3초
  - 위 실험을 통해 알게된 점:
      - 이번 실험에서는 속도 상한(5 deg/s)이 낮아 A(Kp=6.5)·B(Kp=2) 모두
    오버슈트가 발생하지 않았다. (일반적으로 Kp가 크고 속도 여유가 있으면
    오버슈트가 생길 수 있다.)
    - Kp가 작은 B는 같은 경과 시간에 목표에 덜 도달했고(t=7.0s: A 19.863° vs B 19.336°),
    정상상태 오차도 더 컸다(A 0.137° < B 0.312°). 이는 Kp가 작을수록 목표 근처에서
    만들어내는 속도 명령이 작아, 목표에 더 못 미친 지점에서 멈추기 때문이다.
  
- OpenCR 위치 제어 게인 VS 다이나믹셀 내부 게인 구분
  - 명령어로 입력한 <s Kp 상한속도 목표각> 은 OpenCR 위치 제어 게인이입니다.
  - 다이나믹셀은 속도 PI 제어기만 존재합니다.
      - 근거. opencr_position_p.ino에 주석에 명시
      ```bash
      // Lv2 3강 — P 제어: 휠 모드 + 엔코더 피드백으로 위치 제어.
      // 수강생이 튜닝하는 Kp는 OpenCR의 위치 제어 게인이다.
      // 목표각도 - 엔코더 각도 -> P 계산 -> Goal Velocity -> 모터 -> 엔코더.
      // 다이나믹셀은 내부 속도 PI만 사용한다. 내부 위치 PID는 사용하지 않는다.
      // XM430-W210, Protocol 2.0, ID 12, 1 Mbps, firmware >= 38, 모터 1개.
      // 실행: s <Kp> <speed_deg_s|max> <angle_deg>; x 정지. 시작 위치가 0도, 2초 후 입력 목표로 이동.

      p_term = static_cast<double>(kp) * error;   // OpenCR 변수 kp로 계산
      dxl.setGoalVelocity(DXL_ID, velocity_raw, UNIT_RAW);   // 모터엔 속도만 전달
      dxl.setOperatingMode(DXL_ID, OP_VELOCITY);   // 속도 모드 → 내부는 속도 PI만

      ```

  - I항과 D항의 역할
    - I항: 시간에 따라 누적된 오차에 비례해 출력을 더하여, P 제어만으로는
    남는 정상상태 오차를 제거하는 역할을 한다.
    - D항: 오차의 변화율(접근 속도)에 반응하여, 목표에 빠르게 접근할수록
    출력을 줄여 오버슈트와 진동을 억제하는 역할을 한다.

## 문제4. 제어와 통신의 역할 해석
아래는 답안 작성을 위한 가상 기록의 일부이며 실제 실행 결과가 아닙니다. 설명용 인터페이스의 목표와 현재값 단위는 °입니다. 기존 8강의 RPM 속도 인터페이스와 구분하세요.

| 항목 | 설명용 조건·기록 |
|---|---|
| 제어 계산 | OpenCR에서 10ms마다 수행 |
| 상태 발행 | 100ms마다 수행 |
| 0.0초 | PC가 /motor/target에 30.0 발행 |
| 0.1초 | PC가 /motor/state에서 2.0 수신 |
| 0.5초 | PC가 /motor/state에서 12.0 수신 |
| 1.0초 | PC가 /motor/state에서 22.0 수신 |
| 2.0초 | PC가 /motor/state에서 29.0 수신 |

PC ROS2 노드·micro-ROS Agent·OpenCR·다이나믹셀을 연결한 구조도에 목표 전달과 측정값 반환 방향을 표시하세요. 목표와 상태를 보내고 받는 주체를 설명하세요. 상태 발행 한 주기 동안 제어 계산이 몇 번 수행되는지 계산하고, 통신 단절 시 오래된 명령을 어떻게 처리할지 정책과 이유를 적으세요.



```
[목표 전달 ▼]                      [측정값 반환 ▲]

  PC ROS2 노드                       PC ROS2 노드
       │ ROS2 토픽                        ▲ ROS2 토픽
       ▼                                  │
  micro-ROS Agent                    micro-ROS Agent
       │ USB 시리얼(/dev/ttyACM0)         ▲ USB 시리얼
       ▼   (ROS2 ↔ 시리얼 번역)            │
  OpenCR                             OpenCR
       │ DXL 버스(Protocol 2.0, 1Mbps)   ▲ DXL 버스
       ▼                                  │
  다이나믹셀(XM430-W210)              다이나믹셀(XM430-W210)


목표 전달:  PC ROS2 노드 → Agent → OpenCR → 다이나믹셀   (/motor/target, 단위 °)
측정값 반환: 다이나믹셀 → OpenCR → Agent → PC ROS2 노드  (/motor/state, 단위 °)

주기: 제어 계산 10ms / 상태 발행 100ms → 발행 1주기당 제어 10회
```

- 통신 단절 시 조치 방법
  - 정책: 통신 단절 시 오래된 명령을 따르지 않고, watchdog(BUS_WATCHDOG)를
    이용해 모터를 안전 정지시킵니다.
  - 이유: 이 시스템은 위치를 '속도 명령'으로 제어하므로, 통신이 끊긴 채
    오래된 속도 명령을 계속 실행하면 모터가 목표를 지나쳐 폭주할 수 있습니다.
    따라서 일정 시간 새 명령이 없으면 watchdog가 속도를 0으로 만들어 정지시킵니다.
  ```cpp
  dxl.writeControlTableItem(BUS_WATCHDOG, DXL_ID, 5);
  ```