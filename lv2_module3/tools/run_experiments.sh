#!/usr/bin/env bash
# 실험 1·2의 A/B 조건을 실행 중인 perception_node에 ros2 param set으로 적용하고,
# 객체 있음/없음 bag을 각각 반복 재생하며 capture_topics.py로 토픽을 수신·저장한다.
# 전제: perception_node 실행 중 (ros2 launch realsense realsense.launch.py use_camera:=false), 다른 bag 재생은 꺼 둔다.
# set -u 는 ROS setup.bash와 충돌해 쓰지 않는다
source /opt/ros/lyrical/setup.bash
HERE=$(cd "$(dirname "$0")/.." && pwd)
REC=${REC:-$HOME/Lv2_noon_Assignment/lv2_module5/recordings}
declare -A BAGS=([pillar]=20261012_102611_no1_pillar_v1 [nontarget]=20261012_102713_no1_nontarget_v1)

apply() {  # $1 = 출력 폴더, 나머지 = name=value
  local out=$1; shift
  mkdir -p "$out"
  : > "$out/applied_params.txt"
  for kv in "$@"; do
    echo "\$ ros2 param set /perception_node ${kv%%=*} ${kv#*=}" >> "$out/applied_params.txt"
    ros2 param set /perception_node "${kv%%=*}" "${kv#*=}" >> "$out/applied_params.txt" 2>&1
  done
  for p in hsv_lower hsv_upper hsv_bright_enabled hsv_bright_lower hsv_bright_upper open_kernel close_kernel min_area_ratio max_area_ratio aspect_max fill_min select_rule; do
    echo "$p: $(ros2 param get /perception_node $p)" >> "$out/applied_params.txt"
  done
  sleep 1.5
}

for key in pillar nontarget; do
  ros2 bag play "$REC/${BAGS[$key]}" --topics /camera/camera/color/image_raw /camera/camera/color/camera_info -l > /dev/null 2>&1 &
  BAG_PID=$!
  sleep 3
  apply "$HERE/results/exp1/A/$key" 'hsv_lower=[103, 220, 20]' min_area_ratio=0.0006
  echo "[exp1 A $key] $(python3 "$HERE/tools/capture_topics.py" --out "$HERE/results/exp1/A/$key" --duration 16 | head -1)"
  apply "$HERE/results/exp1/B/$key" 'hsv_lower=[103, 30, 20]' min_area_ratio=0.0006
  echo "[exp1 B $key] $(python3 "$HERE/tools/capture_topics.py" --out "$HERE/results/exp1/B/$key" --duration 16 | head -1)"
  apply "$HERE/results/exp2/A/$key" 'hsv_lower=[103, 30, 20]' min_area_ratio=0.0006
  echo "[exp2 A $key] $(python3 "$HERE/tools/capture_topics.py" --out "$HERE/results/exp2/A/$key" --duration 16 | head -1)"
  apply "$HERE/results/exp2/B/$key" 'hsv_lower=[103, 30, 20]' min_area_ratio=0.002
  echo "[exp2 B $key] $(python3 "$HERE/tools/capture_topics.py" --out "$HERE/results/exp2/B/$key" --duration 16 | head -1)"
  kill -TERM $BAG_PID; wait $BAG_PID 2>/dev/null
  sleep 1
done

# 기본값 복구
ros2 param set /perception_node hsv_lower '[103, 220, 20]'
ros2 param set /perception_node min_area_ratio 0.0006
