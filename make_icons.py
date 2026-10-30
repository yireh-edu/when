# 앱 아이콘(icon-192.png, icon-512.png)을 표준 라이브러리만으로 그린다. (시계 + 체크)
import math, os, struct, zlib

BG = (18, 137, 123)
FACE = (255, 255, 255)
HAND = (27, 31, 36)
CHECK = (245, 166, 35)
R_FACE = 0.30
SS = 3  # 가장자리 부드럽게: 픽셀당 SS x SS 샘플


def seg_dist(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / (vx * vx + vy * vy)))
    dx, dy = px - (ax + vx * t), py - (ay + vy * t)
    return math.hypot(dx, dy)


C = (0.5, 0.5)
# 시침(10시 방향), 분침(12시 방향)
HOUR = (C[0] + 0.13 * math.cos(math.radians(-150)), C[1] + 0.13 * math.sin(math.radians(-150)))
MIN = (C[0], C[1] - 0.20)
# 오른쪽 아래 체크 배지
BADGE = (0.70, 0.70)
R_BADGE = 0.12
CK = [(0.645, 0.70), (0.69, 0.745), (0.76, 0.655)]


def sample(x, y):
    bx, by = x - BADGE[0], y - BADGE[1]
    if bx * bx + by * by <= R_BADGE * R_BADGE:
        if min(seg_dist(x, y, *CK[0], *CK[1]), seg_dist(x, y, *CK[1], *CK[2])) <= 0.018:
            return FACE
        return CHECK
    dx, dy = x - C[0], y - C[1]
    d = math.hypot(dx, dy)
    if d <= R_FACE:
        if seg_dist(x, y, *C, *HOUR) <= 0.022 or seg_dist(x, y, *C, *MIN) <= 0.017:
            return HAND
        # 12/3/6/9 눈금
        for k in range(4):
            a = math.radians(90 * k)
            ox, oy = math.cos(a), math.sin(a)
            if seg_dist(x, y, C[0] + ox * 0.235, C[1] + oy * 0.235, C[0] + ox * 0.27, C[1] + oy * 0.27) <= 0.012:
                return HAND
        return FACE
    return BG


def pixel(i, j, size):
    acc = [0, 0, 0]
    for sj in range(SS):
        for si in range(SS):
            c = sample((i + (si + 0.5) / SS) / size, (j + (sj + 0.5) / SS) / size)
            for k in range(3):
                acc[k] += c[k]
    return tuple(v // (SS * SS) for v in acc)


def png(size, path):
    rows = []
    for j in range(size):
        row = bytearray([0])
        for i in range(size):
            row += bytes(pixel(i, j, size))
        rows.append(bytes(row))
    raw = zlib.compress(b"".join(rows), 9)

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)))
        f.write(chunk(b"IDAT", raw))
        f.write(chunk(b"IEND", b""))


here = os.path.dirname(os.path.abspath(__file__))
for s in (192, 512):
    png(s, os.path.join(here, f"icon-{s}.png"))
