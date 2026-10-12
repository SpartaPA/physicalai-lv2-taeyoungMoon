#!/usr/bin/env python3
"""토픽 수신 증빙 저장 도구 (비전 처리 없음, 구독·저장만 한다).

perception_node가 발행하는 Mask·Overlay(CompressedImage)를 받고, 같은 header.stamp를 가진
Raw Image를 골라 함께 저장한다. 지정한 시간 동안 /target과 perception_node 로그(/rosout)도 기록한다.

사용 예:
  python3 capture_topics.py --out results/exp1/A --duration 16
  python3 capture_topics.py --out results/exp1/A --duration 32 --stamp 1791768374.766279053
    (--stamp: 이 header.stamp 프레임의 Raw·Mask·Overlay만 저장. A/B를 같은 입력 프레임으로 비교할 때 사용)
"""
import argparse
import csv
import os
import time

import cv2
import numpy as np
import rclpy
from geometry_msgs.msg import PointStamped
from rcl_interfaces.msg import Log
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import CompressedImage, Image


def stamp_str(stamp):
    return f'{stamp.sec}.{stamp.nanosec:09d}'


class Capture(Node):
    def __init__(self, args):
        super().__init__('capture_topics')
        self.args = args
        self.raw = {}  # stamp -> Image (최근 프레임만 보관)
        self.mask = None
        self.debug = None
        self.saved = False
        self.targets = []
        self.logs = []
        self.create_subscription(Image, args.raw, self.on_raw, QoSProfile(depth=5))
        self.create_subscription(CompressedImage, args.mask, self.on_mask, QoSProfile(depth=5))
        self.create_subscription(CompressedImage, args.debug, self.on_debug, QoSProfile(depth=5))
        self.create_subscription(
            PointStamped, args.target, self.on_target,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT))
        self.create_subscription(Log, '/rosout', self.on_log, QoSProfile(depth=50))

    def on_raw(self, msg):
        self.raw[stamp_str(msg.header.stamp)] = msg
        if len(self.raw) > 60:
            self.raw.pop(next(iter(self.raw)))
        self.try_save()

    def on_mask(self, msg):
        if not self.saved:
            self.mask = msg
        self.try_save()

    def on_debug(self, msg):
        if not self.saved:
            self.debug = msg
        self.try_save()

    def on_target(self, msg):
        p = msg.point
        self.targets.append((stamp_str(msg.header.stamp), p.x, p.y, p.z))

    def on_log(self, msg):
        if msg.name == 'perception_node':
            self.logs.append(msg.msg)

    def try_save(self):
        # Mask와 Overlay는 같은 header로 발행된다. 같은 stamp의 Raw가 도착하면 3장을 함께 저장한다
        if self.saved or self.mask is None or self.debug is None:
            return
        key = stamp_str(self.mask.header.stamp)
        if stamp_str(self.debug.header.stamp) != key or key not in self.raw:
            return
        if self.args.stamp and key != self.args.stamp:
            return
        raw = self.raw[key]
        img = np.frombuffer(bytes(raw.data), np.uint8).reshape(raw.height, raw.width, -1)
        if raw.encoding == 'rgb8':
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        out = self.args.out
        cv2.imwrite(os.path.join(out, 'raw.png'), img)
        with open(os.path.join(out, 'mask.jpg'), 'wb') as f:
            f.write(bytes(self.mask.data))
        with open(os.path.join(out, 'overlay.jpg'), 'wb') as f:
            f.write(bytes(self.debug.data))
        mask = cv2.imdecode(np.frombuffer(bytes(self.mask.data), np.uint8), cv2.IMREAD_GRAYSCALE)
        with open(os.path.join(out, 'frame_info.txt'), 'w') as f:
            f.write(f'header.stamp: {key}\n')
            f.write(f'raw: {self.args.raw} {raw.width}x{raw.height} encoding={raw.encoding}\n')
            f.write(f'mask: {self.args.mask} format={self.mask.format} '
                    f'nonzero(>127)={int((mask > 127).sum())} px\n')
            f.write(f'overlay: {self.args.debug} format={self.debug.format}\n')
        self.saved = True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--duration', type=float, default=16.0)
    ap.add_argument('--raw', default='/camera/camera/color/image_raw')
    ap.add_argument('--mask', default='/perception_node/mask/compressed')
    ap.add_argument('--debug', default='/perception_node/debug_image/compressed')
    ap.add_argument('--target', default='/target')
    ap.add_argument('--stamp', default='', help='저장할 프레임의 header.stamp (sec.nanosec 9자리)')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    rclpy.init()
    node = Capture(args)
    end = time.monotonic() + args.duration
    while rclpy.ok() and time.monotonic() < end:
        rclpy.spin_once(node, timeout_sec=0.1)

    with open(os.path.join(args.out, 'target.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['stamp', 'x_ex', 'y_ey', 'z_area_ratio'])
        w.writerows(node.targets)
    with open(os.path.join(args.out, 'rosout.txt'), 'w') as f:
        f.write('\n'.join(node.logs) + '\n')

    z = np.array([t[3] for t in node.targets]) if node.targets else np.zeros(0)
    det = z[z > 0]
    summary = [
        f'/target 수신 {len(z)}개, 검출(z>0) {len(det)}개, 미검출(z=0) {len(z) - len(det)}개',
        f'images saved: {node.saved}',
    ]
    if len(det):
        xs = np.array([t[1] for t in node.targets if t[3] > 0])
        ys = np.array([t[2] for t in node.targets if t[3] > 0])
        summary.append(
            f'검출 프레임 중앙값 ex={np.median(xs):+.4f} ey={np.median(ys):+.4f} '
            f'area_ratio={np.median(det):.5f} (min {det.min():.5f}, max {det.max():.5f})')
    with open(os.path.join(args.out, 'summary.txt'), 'w') as f:
        f.write('\n'.join(summary) + '\n')
    print('\n'.join(summary))
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
