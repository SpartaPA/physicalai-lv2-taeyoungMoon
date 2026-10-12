#!/usr/bin/env bash
# A/B를 같은 입력 프레임(header.stamp 고정)으로 비교하기 위한 캡처.
# Mask·Overlay는 debug_rate_hz(기본 5Hz)마다만 발행되어 특정 프레임이 빠질 수 있으므로, 캡처하는 동안만 30으로 올린다.
# debug_rate_hz는 디버그 영상 발행 주기일 뿐 Mask 생성·검출 결과에는 영향이 없다 (perception_node.cpp:262).
source /opt/ros/lyrical/setup.bash
HERE=$(cd "$(dirname "$0")/.." && pwd)
REC=${REC:-$HOME/Lv2_noon_Assignment/lv2_module5/recordings}
P_BAG=20261012_102611_no1_pillar_v1;    P_STAMP=1791768374.766279053
N_BAG=20261012_102713_no1_nontarget_v1; N_STAMP=1791768434.874002686
N_STAMP2=1791768444.914093018  # 실험 2-B에서도 남은 오검출 프레임

cap() {  # out stamp hsv_lower min_area
  ros2 param set /perception_node hsv_lower "$3" > /dev/null
  ros2 param set /perception_node min_area_ratio "$4" > /dev/null
  sleep 1
  echo "[$1] hsv_lower=$3 min_area_ratio=$4 stamp=$2 :: $(python3 "$HERE/tools/capture_topics.py" --out "$HERE/results/$1" --duration 34 --stamp "$2" | tr '\n' ' ')"
}

ros2 param set /perception_node debug_rate_hz 30.0 > /dev/null
for which in P N; do
  bag=${which}_BAG; stamp=${which}_STAMP; key=$([ $which = P ] && echo pillar || echo nontarget)
  ros2 bag play "$REC/${!bag}" --topics /camera/camera/color/image_raw /camera/camera/color/camera_info -l > /dev/null 2>&1 &
  BAG_PID=$!; sleep 3
  cap exp1/A/$key/same_frame ${!stamp} '[103, 220, 20]' 0.0006
  cap exp1/B/$key/same_frame ${!stamp} '[103, 30, 20]'  0.0006
  cap exp2/A/$key/same_frame ${!stamp} '[103, 30, 20]'  0.0006
  cap exp2/B/$key/same_frame ${!stamp} '[103, 30, 20]'  0.002
  if [ $which = N ]; then
    cap exp2/A/nontarget/same_frame2 $N_STAMP2 '[103, 30, 20]' 0.0006
    cap exp2/B/nontarget/same_frame2 $N_STAMP2 '[103, 30, 20]' 0.002
  fi
  kill -TERM $BAG_PID; wait $BAG_PID 2>/dev/null; sleep 1
done
ros2 param set /perception_node hsv_lower '[103, 220, 20]' > /dev/null
ros2 param set /perception_node min_area_ratio 0.0006 > /dev/null
ros2 param set /perception_node debug_rate_hz 5.0 > /dev/null
echo "restored: $(ros2 param get /perception_node hsv_lower) / $(ros2 param get /perception_node min_area_ratio) / $(ros2 param get /perception_node debug_rate_hz)"
