#!/usr/bin/env python3
"""
CCTV YSP 直播流获取 - Python 完整版
100% 还原 Rust 二进制 (uhdiptv.bin) 行为
IDA Pro MCP 逐函数验证

用法: python cctv_live.py [cctv5|cctv164k|cctv4k|cctv8k]
      默认 cctv5, 随机1台设备
"""

import json, time, hashlib, os, base64, sys, random, requests
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import urllib3; urllib3.disable_warnings()

# ═══════════ 常量 (IDA sub_4413C/sub_44188/sub_441D4 提取) ═══════════
APPID    = '9f5c54c4ed0e50109b800f7e28fec205'
APP_KEY  = '1178c84d-4818-44ff-b415-02106e87e144'
APP_VER  = '1.4.1'
LIVE_UID = 'BAEBFF2B-C516-4F34-ABC0-A824A6461CBD'

RSA_PEM  = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkKeLy4ywWLSnBkwRyqYg\nF3HMIj05V5uuh5HjyEsZOWnu1NHu3jPQv3sr32wwQNYv5qapsNXmNgLUDHtgHZxq\nPQAYXltjSRc0qhcD286t62wOIHId8zXS3s1Jy4rgU4qjQWzI9rp/1sE0pMsmwTaJ\na4zuJ5iz8VwF8Av5oJ1k+HxY+/HLnjNlW1hmWLpuDYmkZYuAoTHa1VGeHQh9FEKI\n8ZcL3GTQphShUoC+Kg3P1hGUVTtCYapmzPS5lkAdwebuzwvTCfGiTErYZCnPBUSe\nV7BVlgjtLYIi29KvF0a8FHsJMfe/UdHcyW/RihsIYOtDQcRRpFGXyPXbVrzFJse2\n4QIDAQAB\n-----END PUBLIC KEY-----'
RSA_KEY = load_pem_public_key(RSA_PEM)

CHANNELS = {
    'cctv5':    'Live1719474204987287',
    'cctv164k': 'Live1704966749996185',
    'cctv4k':   'Live1767871224782105',
    'cctv8k':   'Live1688400593818102',
}

# ═══════════ 52款真机设备池 (uhdiptv.bin DeviceProfile) ═══════════
DEVICE_POOL = [
    # Sony 8K
    {'hw':'mt5895','board':'mt5895','brand':'Sony','device':'sony_xr_85z9k','mfr':'Sony','model':'XR-85Z9K','prod':'sony_xr_85z9k','res':'7680*4320','screen':'7680-4320-260','ver':'SONYTV.2022.XR_85Z9K'},
    {'hw':'mt5895','board':'mt5895','brand':'Sony','device':'sony_xr_75z9k','mfr':'Sony','model':'XR-75Z9K','prod':'sony_xr_75z9k','res':'7680*4320','screen':'7680-4320-260','ver':'SONYTV.2022.XR_75Z9K'},
    {'hw':'mt5895','board':'mt5895','brand':'Sony','device':'sony_xr_85z9j','mfr':'Sony','model':'XR-85Z9J','prod':'sony_xr_85z9j','res':'7680*4320','screen':'7680-4320-260','ver':'SONYTV.2021.XR_85Z9J'},
    {'hw':'mt5895','board':'mt5895','brand':'Sony','device':'sony_xr_75z9j','mfr':'Sony','model':'XR-75Z9J','prod':'sony_xr_75z9j','res':'7680*4320','screen':'7680-4320-260','ver':'SONYTV.2021.XR_75Z9J'},
    {'hw':'mt5893','board':'mt5893','brand':'Sony','device':'sony_kd_98zg9','mfr':'Sony','model':'KD-98ZG9','prod':'sony_kd_98zg9','res':'7680*4320','screen':'7680-4320-320','ver':'SONYTV.2019.KD_98ZG9'},
    {'hw':'mt5893','board':'mt5893','brand':'Sony','device':'sony_kd_85zg9','mfr':'Sony','model':'KD-85ZG9','prod':'sony_kd_85zg9','res':'7680*4320','screen':'7680-4320-320','ver':'SONYTV.2019.KD_85ZG9'},
    {'hw':'mt5893','board':'mt5893','brand':'Sony','device':'sony_kd_85zh8','mfr':'Sony','model':'KD-85ZH8','prod':'sony_kd_85zh8','res':'7680*4320','screen':'7680-4320-320','ver':'SONYTV.2020.KD_85ZH8'},
    {'hw':'mt5893','board':'mt5893','brand':'Sony','device':'sony_kd_75zh8','mfr':'Sony','model':'KD-75ZH8','prod':'sony_kd_75zh8','res':'7680*4320','screen':'7680-4320-320','ver':'SONYTV.2020.KD_75ZH8'},
    # Samsung 8K
    {'hw':'s5e9925','board':'neo8k','brand':'Samsung','device':'samsung_qa85qn900a','mfr':'Samsung','model':'QA85QN900A','prod':'samsung_qa85qn900a','res':'7680*4320','screen':'7680-4320-260','ver':'SAMSUNGTV.2021.QN900A'},
    {'hw':'s5e9925','board':'neo8k','brand':'Samsung','device':'samsung_qa75qn900a','mfr':'Samsung','model':'QA75QN900A','prod':'samsung_qa75qn900a','res':'7680*4320','screen':'7680-4320-260','ver':'SAMSUNGTV.2021.QN900A'},
    {'hw':'s5e9925','board':'neo8k','brand':'Samsung','device':'samsung_qa85qn900b','mfr':'Samsung','model':'QA85QN900B','prod':'samsung_qa85qn900b','res':'7680*4320','screen':'7680-4320-260','ver':'SAMSUNGTV.2022.QN900B'},
    {'hw':'s5e9925','board':'neo8k','brand':'Samsung','device':'samsung_qa75qn900b','mfr':'Samsung','model':'QA75QN900B','prod':'samsung_qa75qn900b','res':'7680*4320','screen':'7680-4320-260','ver':'SAMSUNGTV.2022.QN900B'},
    {'hw':'s5e9935','board':'neo8k','brand':'Samsung','device':'samsung_qa85qn900c','mfr':'Samsung','model':'QA85QN900C','prod':'samsung_qa85qn900c','res':'7680*4320','screen':'7680-4320-260','ver':'SAMSUNGTV.2023.QN900C'},
    {'hw':'s5e9935','board':'neo8k','brand':'Samsung','device':'samsung_qa75qn900c','mfr':'Samsung','model':'QA75QN900C','prod':'samsung_qa75qn900c','res':'7680*4320','screen':'7680-4320-260','ver':'SAMSUNGTV.2023.QN900C'},
    {'hw':'s5e9945','board':'neo8k','brand':'Samsung','device':'samsung_qa85qn900d','mfr':'Samsung','model':'QA85QN900D','prod':'samsung_qa85qn900d','res':'7680*4320','screen':'7680-4320-260','ver':'SAMSUNGTV.2024.QN900D'},
    {'hw':'s5e9935','board':'neo8k','brand':'Samsung','device':'samsung_qa98qn990c','mfr':'Samsung','model':'QA98QN990C','prod':'samsung_qa98qn990c','res':'7680*4320','screen':'7680-4320-320','ver':'SAMSUNGTV.2023.QN990C'},
    {'hw':'s5e9935','board':'neo8k','brand':'Samsung','device':'samsung_qa85qn800c','mfr':'Samsung','model':'QA85QN800C','prod':'samsung_qa85qn800c','res':'7680*4320','screen':'7680-4320-260','ver':'SAMSUNGTV.2023.QN800C'},
    {'hw':'s5e9945','board':'neo8k','brand':'Samsung','device':'samsung_qa75qn800d','mfr':'Samsung','model':'QA75QN800D','prod':'samsung_qa75qn800d','res':'7680*4320','screen':'7680-4320-260','ver':'SAMSUNGTV.2024.QN800D'},
    # LG 8K
    {'hw':'alpha9gen4','board':'lg8k','brand':'LG','device':'lg_oled88z1pca','mfr':'LGE','model':'OLED88Z1PCA','prod':'lg_oled88z1pca','res':'7680*4320','screen':'7680-4320-260','ver':'LGTV.2021.OLED88Z1'},
    {'hw':'alpha9gen4','board':'lg8k','brand':'LG','device':'lg_oled77z1pca','mfr':'LGE','model':'OLED77Z1PCA','prod':'lg_oled77z1pca','res':'7680*4320','screen':'7680-4320-260','ver':'LGTV.2021.OLED77Z1'},
    {'hw':'alpha9gen5','board':'lg8k','brand':'LG','device':'lg_oled88z2pca','mfr':'LGE','model':'OLED88Z2PCA','prod':'lg_oled88z2pca','res':'7680*4320','screen':'7680-4320-260','ver':'LGTV.2022.OLED88Z2'},
    {'hw':'alpha9gen5','board':'lg8k','brand':'LG','device':'lg_oled77z2pca','mfr':'LGE','model':'OLED77Z2PCA','prod':'lg_oled77z2pca','res':'7680*4320','screen':'7680-4320-260','ver':'LGTV.2022.OLED77Z2'},
    {'hw':'alpha9gen6','board':'lg8k','brand':'LG','device':'lg_oled88z3pca','mfr':'LGE','model':'OLED88Z3PCA','prod':'lg_oled88z3pca','res':'7680*4320','screen':'7680-4320-260','ver':'LGTV.2023.OLED88Z3'},
    {'hw':'alpha9gen6','board':'lg8k','brand':'LG','device':'lg_oled77z3pca','mfr':'LGE','model':'OLED77Z3PCA','prod':'lg_oled77z3pca','res':'7680*4320','screen':'7680-4320-260','ver':'LGTV.2023.OLED77Z3'},
    {'hw':'alpha9gen7','board':'lg8k','brand':'LG','device':'lg_oled88z4pca','mfr':'LGE','model':'OLED88Z4PCA','prod':'lg_oled88z4pca','res':'7680*4320','screen':'7680-4320-260','ver':'LGTV.2024.OLED88Z4'},
    {'hw':'alpha9gen6','board':'lg8k','brand':'LG','device':'lg_86qned99','mfr':'LGE','model':'86QNED99','prod':'lg_86qned99','res':'7680*4320','screen':'7680-4320-300','ver':'LGTV.2021.86QNED99'},
    # Sony 4K
    {'hw':'mt5895','board':'mt5895','brand':'Sony','device':'sony_xr_85x95k','mfr':'Sony','model':'XR-85X95K','prod':'sony_xr_85x95k','res':'3840*2160','screen':'3840-2160-300','ver':'SONYTV.2022.XR_85X95K'},
    {'hw':'mt5895','board':'mt5895','brand':'Sony','device':'sony_xr_75x95k','mfr':'Sony','model':'XR-75X95K','prod':'sony_xr_75x95k','res':'3840*2160','screen':'3840-2160-280','ver':'SONYTV.2022.XR_75X95K'},
    {'hw':'mt5895','board':'mt5895','brand':'Sony','device':'sony_xr_65x90k','mfr':'Sony','model':'XR-65X90K','prod':'sony_xr_65x90k','res':'3840*2160','screen':'3840-2160-260','ver':'SONYTV.2022.XR_65X90K'},
    {'hw':'mt5895','board':'mt5895','brand':'Sony','device':'sony_xr_55x90k','mfr':'Sony','model':'XR-55X90K','prod':'sony_xr_55x90k','res':'3840*2160','screen':'3840-2160-240','ver':'SONYTV.2022.XR_55X90K'},
    {'hw':'mt5895','board':'mt5895','brand':'Sony','device':'sony_xr_65a95k','mfr':'Sony','model':'XR-65A95K','prod':'sony_xr_65a95k','res':'3840*2160','screen':'3840-2160-260','ver':'SONYTV.2022.XR_65A95K'},
    # Samsung 4K
    {'hw':'s5e9935','board':'neo4k','brand':'Samsung','device':'samsung_qa85qn90c','mfr':'Samsung','model':'QA85QN90C','prod':'samsung_qa85qn90c','res':'3840*2160','screen':'3840-2160-300','ver':'SAMSUNGTV.2023.QN90C'},
    {'hw':'s5e9935','board':'neo4k','brand':'Samsung','device':'samsung_qa75qn90c','mfr':'Samsung','model':'QA75QN90C','prod':'samsung_qa75qn90c','res':'3840*2160','screen':'3840-2160-280','ver':'SAMSUNGTV.2023.QN90C'},
    {'hw':'s5e9935','board':'neo4k','brand':'Samsung','device':'samsung_qa65qn90c','mfr':'Samsung','model':'QA65QN90C','prod':'samsung_qa65qn90c','res':'3840*2160','screen':'3840-2160-260','ver':'SAMSUNGTV.2023.QN90C'},
    {'hw':'s5e9935','board':'neo4k','brand':'Samsung','device':'samsung_qa55qn90c','mfr':'Samsung','model':'QA55QN90C','prod':'samsung_qa55qn90c','res':'3840*2160','screen':'3840-2160-240','ver':'SAMSUNGTV.2023.QN90C'},
    {'hw':'s5e9935','board':'oled4k','brand':'Samsung','device':'samsung_qa65s95c','mfr':'Samsung','model':'QA65S95C','prod':'samsung_qa65s95c','res':'3840*2160','screen':'3840-2160-260','ver':'SAMSUNGTV.2023.S95C'},
    # LG 4K
    {'hw':'alpha9gen6','board':'lg4k','brand':'LG','device':'lg_oled83c3pca','mfr':'LGE','model':'OLED83C3PCA','prod':'lg_oled83c3pca','res':'3840*2160','screen':'3840-2160-260','ver':'LGTV.2023.OLED83C3'},
    {'hw':'alpha9gen6','board':'lg4k','brand':'LG','device':'lg_oled77c3pca','mfr':'LGE','model':'OLED77C3PCA','prod':'lg_oled77c3pca','res':'3840*2160','screen':'3840-2160-260','ver':'LGTV.2023.OLED77C3'},
    {'hw':'alpha9gen6','board':'lg4k','brand':'LG','device':'lg_oled65c3pca','mfr':'LGE','model':'OLED65C3PCA','prod':'lg_oled65c3pca','res':'3840*2160','screen':'3840-2160-260','ver':'LGTV.2023.OLED65C3'},
    {'hw':'alpha9gen6','board':'lg4k','brand':'LG','device':'lg_oled55c3pca','mfr':'LGE','model':'OLED55C3PCA','prod':'lg_oled55c3pca','res':'3840*2160','screen':'3840-2160-260','ver':'LGTV.2023.OLED55C3'},
    {'hw':'alpha7gen5','board':'lg4k','brand':'LG','device':'lg_86qned90','mfr':'LGE','model':'86QNED90','prod':'lg_86qned90','res':'3840*2160','screen':'3840-2160-260','ver':'LGTV.2022.86QNED90'},
    # TCL 8K
    {'hw':'mt9615','board':'tcl8k','brand':'TCL','device':'tcl_85x925pro','mfr':'TCL','model':'85X925PRO','prod':'tcl_85x925pro','res':'7680*4320','screen':'7680-4320-260','ver':'TCLTV.2021.X925PRO'},
    {'hw':'mt9615','board':'tcl8k','brand':'TCL','device':'tcl_75x925pro','mfr':'TCL','model':'75X925PRO','prod':'tcl_75x925pro','res':'7680*4320','screen':'7680-4320-260','ver':'TCLTV.2021.X925PRO'},
    # TCL 4K
    {'hw':'tcl4k','board':'tcl4k','brand':'TCL','device':'tcl_85c845','mfr':'TCL','model':'85C845','prod':'tcl_85c845','res':'3840*2160','screen':'3840-2160-260','ver':'TCLTV.2023.C845'},
    {'hw':'tcl4k','board':'tcl4k','brand':'TCL','device':'tcl_75c845','mfr':'TCL','model':'75C845','prod':'tcl_75c845','res':'3840*2160','screen':'3840-2160-260','ver':'TCLTV.2023.C845'},
    {'hw':'tcl4k','board':'tcl4k','brand':'TCL','device':'tcl_65c845','mfr':'TCL','model':'65C845','prod':'tcl_65c845','res':'3840*2160','screen':'3840-2160-260','ver':'TCLTV.2023.C845'},
    {'hw':'tcl4k','board':'tcl4k','brand':'TCL','device':'tcl_75c745','mfr':'TCL','model':'75C745','prod':'tcl_75c745','res':'3840*2160','screen':'3840-2160-260','ver':'TCLTV.2023.C745'},
    {'hw':'tcl4k','board':'tcl4k','brand':'TCL','device':'tcl_65c745','mfr':'TCL','model':'65C745','prod':'tcl_65c745','res':'3840*2160','screen':'3840-2160-260','ver':'TCLTV.2023.C745'},
    # CHANGHONG 4K
    {'hw':'mt9632','board':'changhong4k','brand':'CHANGHONG','device':'changhong_u65g7','mfr':'CHANGHONG','model':'U65G7','prod':'changhong_u65g7','res':'3840*2160','screen':'3840-2160-260','ver':'CHANGHONGTV.2022.U65G7'},
    {'hw':'mt9632','board':'changhong4k','brand':'CHANGHONG','device':'changhong_u55g7','mfr':'CHANGHONG','model':'U55G7','prod':'changhong_u55g7','res':'3840*2160','screen':'3840-2160-260','ver':'CHANGHONGTV.2022.U55G7'},
    {'hw':'mt9632','board':'changhong4k','brand':'CHANGHONG','device':'changhong_l55qcn1','mfr':'CHANGHONG','model':'L55QCN1','prod':'changhong_l55qcn1','res':'3840*2160','screen':'3840-2160-220','ver':'CHANGHONGTV.2021.L55QCN1'},
    {'hw':'mt9632','board':'changhong4k','brand':'CHANGHONG','device':'changhong_u43qcn1','mfr':'CHANGHONG','model':'U43QCN1','prod':'changhong_u43qcn1','res':'3840*2160','screen':'3840-2160-220','ver':'CHANGHONGTV.2021.U43QCN1'},
]

# ═══════════ 核心算法 (IDA sub_4C080 + sub_5EE50) ═══════════

def java_hashcode(s):
    """sub_4C080: h = h*31 + c, 32-bit wrapping"""
    h = 0
    for c in s:
        h = (h * 31 + ord(c)) & 0xFFFFFFFF
    if h > 0x7FFFFFFF:
        h -= 0x100000000
    if h < -0x80000000:
        h += 0x100000000
    return h

def java_uuid_nohyphen(h1, h2):
    """sub_4C080: %08x%04x%04x%04x%012x"""
    m = h1 if h1 >= 0 else (1 << 64) + h1
    l = h2 if h2 >= 0 else (1 << 64) + h2
    return '%08x%04x%04x%04x%012x' % (
        (m >> 32) & 0xFFFFFFFF,
        (m >> 16) & 0xFFFF,
        m & 0xFFFF,
        (l >> 48) & 0xFFFF,
        l & 0xFFFFFFFFFFFF
    )

def compute_xuid(dev, aid, mac):
    """sub_4C080: base='1698'+hw+board+brand+device+mfr+model+prod+tags+bt+user+res+mac
       SHA1(aid + '|' + javaUUID(jh(base), jh(model))) → uppercase"""
    base = ('1698' + dev['hw'] + dev['board'] + dev['brand'] + dev['device']
            + dev['mfr'] + dev['model'] + dev['prod']
            + 'release-keys' + 'user' + 'build' + dev['res'] + mac)
    uuid = java_uuid_nohyphen(java_hashcode(base), java_hashcode(dev['model']))
    return hashlib.sha1((aid + '|' + uuid).encode()).hexdigest().upper()

def compute_fingerprint(xuid, t1):
    """sub_5EE50: t2=86400000*floor((t1/1000+28800)/86400)-28800000
       SHA256(hex(SHA256(APPID+xuid+t1+t2)))"""
    sec = int(t1) // 1000
    t2 = str(86400000 * ((sec + 28800) // 86400) - 28800000)
    inner = hashlib.sha256((APPID + xuid + t1 + t2).encode()).hexdigest()
    return hashlib.sha256(inner.encode()).hexdigest()

# ═══════════ 工具 ═══════════

def gen_aid():
    return os.urandom(8).hex()

def gen_mac():
    b = bytearray(os.urandom(6))
    b[0] = (b[0] & 0xFE) | 0x02
    return ':'.join('%02x' % x for x in b)

def gen_nonce():
    b = bytearray(os.urandom(16))
    b[6] = (b[6] & 0x0F) | 0x40
    b[8] = (b[8] & 0x3F) | 0x80
    h = b.hex()
    return '%s-%s-%s-%s-%s' % (h[0:8], h[8:12], h[12:16], h[16:20], h[20:32])

def rsa_encrypt(plaintext):
    return base64.b64encode(RSA_KEY.encrypt(
        plaintext.encode(),
        OAEP(mgf=MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=b'')
    )).decode()

def aes_gcm_decrypt(b64, key_ascii):
    raw = base64.b64decode(b64)
    if len(raw) < 28:
        return ''
    nonce, ct, tag = raw[:12], raw[12:-16], raw[-16:]
    return AESGCM(key_ascii.encode()).decrypt(nonce, ct + tag, None).decode()

def aes_gcm_encrypt(plaintext, key_ascii):
    nonce = os.urandom(12)
    ct = AESGCM(key_ascii.encode()).encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ct).decode()

# ═══════════ HTTP header构建 (IDA sub_4C6F0: 13头 + Content-Type, 无Accept) ═══════════

def make_headers(xuid, fp, aid, ts, content_type='application/json'):
    return {
        'X-Timestamp':      ts,
        'X-Nonce':          '0',
        'Accept':           'application/json',
        'Accept-Language':  'zh-CN,zh;q=0.8',
        'Referer':          'api.cctv.cn',
        'User-Agent':       'cctv_app_tv',
        'UID':              aid,
        'appChannel':       'CCTV',
        'X-Uid':            xuid,
        'X-Fingerprint':    fp,
        'X-Version':        APP_VER,
        'Content-Type':     content_type,
        'Connection':       'Keep-Alive',
        'Accept-Encoding':  'gzip',
        'Cache-Control':    'no-cache, no-store, max-age=0',
    }

# ═══════════ 完整流程 ═══════════

def resolve(channel_id, dev, aid, mac, xuid, is_new=True):
    sess = requests.Session()
    sess.verify = False
    # 二进制步骤2: 第一次 time → fingerprint_timestamp_ms
    fp_ts_stored = str(int(time.time() * 1000))
    # 二进制步骤3-5: compute_xuid
    compute_xuid(dev, aid, mac)
    # 二进制步骤6: 第二次 time → 指纹计算用
    fp_ts = str(int(time.time() * 1000))
    fp = compute_fingerprint(xuid, fp_ts)
    h0 = make_headers(xuid, fp, aid, fp_ts)
    dbg = lambda *a: print('[DEBUG]', *a)

    dbg(f'设备: {dev["brand"]} {dev["model"]}')
    def log_r(r, label):
        dbg(f'{label} response headers: {dict(r.headers)}')
        try:
            ck = list(sess.cookies) if sess.cookies else []
            dbg(f'{label} cookies({len(ck)}): {[c.name for c in ck]}')
        except: pass
    dbg(f'aid={aid} xuid={xuid[:16]}... fpTs(指纹)={fp_ts} fpTs(存储)={fp_ts_stored}')
    dbg(f'fp={fp}')
    dbg(f'hw={dev["hw"]} board={dev["board"]} res={dev["res"]} screen={dev["screen"]}')

    # ── 设备信息模板 (das/message 复用) ──
    def device_info_body():
        return {
            'cctv_id': xuid, 'device_id': aid, 'app_key': APP_KEY,
            'android_id': aid, 'mac': mac,
            'build_type': 'user',
            'hardware': dev['hw'],
            'board': dev['board'],
            'brand': dev['brand'],
            'device': dev['device'],
            'display': f'{dev["model"]}-user 13 {dev["ver"]} 2024 release-keys',
            'version_id': dev['ver'],
            'host': dev['mfr'].lower() + '-tv-build',
            'product': dev['prod'],
            'tags': 'release-keys',
            'user': 'build',
            'fingerprint': f'{dev["brand"]}/{dev["device"]}/{dev["device"]}:13/{dev["ver"]}/2024:user/release-keys',
            'manufacturer': dev['mfr'],
            'model': dev['model'],
            'resolution': dev['res'],
            'report_model': dev['model'],
            'system_type': 'Android', 'device_type': 'TV',
            'app_language': 'CHINESE', 'app_version': APP_VER,
            'os_version': '13', 'app_channel': 'CCTV',
        }

    # ══════════════════════════════════════════════
    # sub_7C1D0: 会话初始化 (IDA确认顺序)
    # ══════════════════════════════════════════════

    # [0] cloud/get → cloud/register FIRST for new devices (风控需要注册传播)
    reg_done = False
    if is_new:
        print('[0] cloud/get + register (新设备先注册)...')
        enc = rsa_encrypt(xuid)
        r = sess.post('https://ytpcloudws.cctv.cn/cloudps/wssapi/device/v2/get',
            data=('{"device_name":"cctv_app_tv","device_id":"'+enc+'"}').encode('utf-8'),
            headers=h0, timeout=15)
        try: cloud_result = r.json().get('result')
        except: cloud_result = 'err'
        dbg(f'cloud/get: {cloud_result}')
        if cloud_result != 0:
            r = sess.post('https://ytpcloudws.cctv.cn/cloudps/wssapi/device/v2/register',
                data=('{"device_name":"cctv_app_tv","device_id":"'+enc+'"}').encode('utf-8'),
                headers=h0, timeout=15)
            reg_j = r.json()
            dbg(f'cloud/register: result={reg_j.get("result")} guid={reg_j.get("data",{}).get("guid","")}')
            if reg_j.get('result') == 0:
                reg_data = reg_j.get('data', {})
                save_device_state({'dev': dev, 'aid': aid, 'mac': mac, 'xuid': xuid,
                                   'guid': reg_data.get('guid', ''),
                                   'secretKey': reg_data.get('secretKey', '')})
                reg_done = True
                dbg(f'设备已保存, 等待30s传播...')
        if reg_done:
            time.sleep(30)

    # [1] heartbeat
    print('[1/13] heartbeat...')
    def make_hb_body(ts):
        return {
            'cctv_id': xuid, 'device_id': aid, 'idfa': '', 'idfv': '', 'user_id': '',
            'app_key': APP_KEY, 'imei': '', 'android_id': aid, 'mac': mac,
            'build_type': 'user', 'hardware': dev['hw'],
            'board': dev['board'], 'brand': dev['brand'],
            'device': dev['device'],
            'display': f'{dev["model"]}-user 13 {dev["ver"]} 2024 release-keys',
            'version_id': dev['ver'],
            'host': dev['mfr'].lower() + '-tv-build',
            'product': dev['prod'],
            'tags': 'release-keys', 'user': 'build',
            'fingerprint': f'{dev["brand"]}/{dev["device"]}/{dev["device"]}:13/{dev["ver"]}/2024:user/release-keys',
            'manufacturer': dev['mfr'], 'model': dev['model'],
            'resolution': dev['res'], 'report_model': dev['model'],
            'system_type': 'Android', 'device_type': 'TV',
            'app_language': 'CHINESE', 'app_version': APP_VER,
            'sdk_version': '', 'os_version': '13', 'app_channel': 'CCTV',
            'event_id': 'app_heartbeat', 'event_name': 'APP心跳',
            'event_time': ts, 'network_type': 'WIFI', 'channel': 'CCTV',
        }
    hb = make_hb_body(fp_ts)
    r = sess.post(
        'https://collect.cctv.cn/cctvmobileinf/rest/cctv/receive/new/app',
        data='info=' + requests.utils.quote(json.dumps(hb, separators=(',', ':'))),
        headers=make_headers(xuid, fp, aid, fp_ts, 'application/x-www-form-urlencoded; charset=UTF-8'),
        timeout=15
    )
    dbg(f'heartbeat: succeed={r.json().get("succeed")}')
    log_r(r, 'hb')

    # [2] app/start @ 0x7ed30
    print('[2/13] app/start...')
    r = sess.post(
        'https://ytpaddr.cctv.cn/gsnw/api/app/start/v1/01',
        json={
            'key': 'app_start_d1',
            'value': {
                **device_info_body(),
                'data_time': fp_ts,
                'idfa': '', 'idfv': '', 'user_id': '',
                'imei': '', 'sdk_version': '',
            }
        },
        headers=h0, timeout=15
    )
    j = r.json()
    print(f'     result={j.get("result")} time={j.get("time")}')
    dbg(f'app/start FULL: {json.dumps(j, ensure_ascii=False)}')
    if j.get('result') != '0':
        dbg(f'FAILED: {json.dumps(j, ensure_ascii=False)[:300]}')
        return None
    session_key = aes_gcm_decrypt(j['data']['key'], fp[:32])
    dbg(f'sessionKey={session_key[:20]}...')
    log_r(r, 'app/start')

    # [3] das/message @ 0x7fdab
    print('[3/13] das/message (1)...')
    r = sess.post(
        'https://ytpdata.cctv.cn/das/app/data/message/single',
        json={
            'key': 'event',
            'value': {
                **device_info_body(),
                'data_time': fp_ts,
                'event_id': 'app_start', 'event_name': 'APP启动',
                'event_time': fp_ts,
                'network_type': 'WIFI', 'channel': 'CCTV',
                'cur_version': APP_VER, 'pre_version': APP_VER,
                'idfa': '', 'idfv': '', 'user_id': '',
                'imei': '', 'sdk_version': '',
            }
        },
        headers=h0, timeout=15
    )
    dbg(f'das/message: status={r.status_code}')

    # [4] heartbeat @ 0x80830
    print('[4/13] heartbeat (2)...')
    hb_ts = str(int(time.time() * 1000))
    hb2 = make_hb_body(hb_ts)
    r = sess.post(
        'https://collect.cctv.cn/cctvmobileinf/rest/cctv/receive/new/app',
        data='info=' + requests.utils.quote(json.dumps(hb2, separators=(',', ':'))),
        headers=make_headers(xuid, fp, aid, hb_ts, 'application/x-www-form-urlencoded; charset=UTF-8'),
        timeout=15
    )
    dbg(f'heartbeat: succeed={r.json().get("succeed")}')

    # [5] das/message @ 0x81058
    print('[5/13] das/message (2)...')
    r = sess.post(
        'https://ytpdata.cctv.cn/das/app/data/message/single',
        json={
            'key': 'event',
            'value': {
                **device_info_body(),
                'data_time': fp_ts,
                'event_id': 'app_start', 'event_name': 'APP启动',
                'event_time': fp_ts,
                'network_type': 'WIFI', 'channel': 'CCTV',
                'cur_version': APP_VER, 'pre_version': APP_VER,
                'idfa': '', 'idfv': '', 'user_id': '',
                'imei': '', 'sdk_version': '',
            }
        },
        headers=h0, timeout=15
    )
    dbg(f'das/message: status={r.status_code}')

    # [6] das/message @ 0x82bfc
    print('[6/13] das/message (3)...')
    r = sess.post(
        'https://ytpdata.cctv.cn/das/app/data/message/single',
        json={
            'key': 'event',
            'value': {
                **device_info_body(),
                'data_time': fp_ts,
                'event_id': 'app_start', 'event_name': 'APP启动',
                'event_time': fp_ts,
                'network_type': 'WIFI', 'channel': 'CCTV',
                'cur_version': APP_VER, 'pre_version': APP_VER,
                'idfa': '', 'idfv': '', 'user_id': '',
                'imei': '', 'sdk_version': '',
            }
        },
        headers=h0, timeout=15
    )

    # [7] das/message sub_7B850 @ 0x82e5c
    print('[7/13] das/message (4 sub_7B850)...')
    r = sess.post(
        'https://ytpdata.cctv.cn/das/app/data/message/single',
        json={
            'key': 'event',
            'value': {
                **device_info_body(),
                'data_time': fp_ts,
                'event_id': 'app_start', 'event_name': 'APP启动',
                'event_time': fp_ts,
                'network_type': 'WIFI', 'channel': 'CCTV',
                'cur_version': APP_VER, 'pre_version': APP_VER,
                'idfa': '', 'idfv': '', 'user_id': '',
                'imei': '', 'sdk_version': '',
            }
        },
        headers=h0, timeout=15
    )

    # [8] index sub_6E1E0 @ 0x82eae
    print('[8/13] index/v1/01...')
    r = sess.post(
        'https://ytpaddr.cctv.cn/gsnw/api/index/v1/01',
        json={'channel': 'CCTV', 'source': 'application'},
        headers=h0, timeout=15
    )
    dbg(f'index: result={r.json().get("result")}')

    # [9] dictionary+drm sub_75BC0 @ 0x82ecd
    print('[9/13] dictionary + drm/config...')
    appcommon = json.dumps({
        'adid': aid, 'av': APP_VER, 'an': 'app', 'ap': 'cctv_app_tv'
    })

    # drm first
    r = sess.post(
        'https://ytpaddr.cctv.cn/gsnw/drm/config/obtain/v1',
        data='appcommon=' + requests.utils.quote(appcommon),
        headers=make_headers(xuid, fp, aid, str(int(time.time() * 1000)), 'application/x-www-form-urlencoded'),
        timeout=15
    )
    dbg(f'drm/config: result={r.json().get("result")}')

    # dictionary
    dh = make_headers(xuid, fp, aid, fp_ts)
    dh['X-Uid'] = 'ROOT'; dh['X-Fingerprint'] = 'ROOT'
    dh['UID'] = 'ROOT'; dh['appChannel'] = 'ROOT'
    del dh['Content-Type']; del dh['Cache-Control']
    r = sess.post(
        'https://ytpaddr.cctv.cn/gsnw/player/dictionary/obtain/v1',
        data='', headers=dh, timeout=15
    )
    dbg(f'dictionary: status={r.status_code}')

    # [10] cloud/get → cloud/register (如果前面[0]已经注册过了就跳过)
    if is_new and not reg_done:
        print('[10/13] cloud/get...')
        enc = rsa_encrypt(xuid)
        r = sess.post(
            'https://ytpcloudws.cctv.cn/cloudps/wssapi/device/v2/get',
            data=('{"device_name":"cctv_app_tv","device_id":"'+enc+'"}').encode('utf-8'),
            headers=h0, timeout=15
        )
        cg_data = r.json()
        cloud_result = cg_data.get('result')
        dbg(f'cloud/get FULL: {json.dumps(cg_data, ensure_ascii=False)}')
        if cloud_result != 0:
            print('[11/13] cloud/register...')
            r = sess.post(
                'https://ytpcloudws.cctv.cn/cloudps/wssapi/device/v2/register',
                data=('{"device_name":"cctv_app_tv","device_id":"'+enc+'"}').encode('utf-8'),
                headers=h0, timeout=15
            )
            reg_j = r.json()
            dbg(f'cloud/register FULL: {json.dumps(reg_j, ensure_ascii=False)}')
            if reg_j.get('result') == 0:
                reg_data = reg_j.get('data', {})
                save_device_state({'dev': dev, 'aid': aid, 'mac': mac, 'xuid': xuid,
                                   'guid': reg_data.get('guid', ''),
                                   'secretKey': reg_data.get('secretKey', '')})
                dbg(f'设备已保存到 {STATE_FILE}')
                log_r(r, 'cloud/reg')
        else:
            # cloud/get result=0: 设备已注册, 从返回中提取guid(如果state文件中没有)
            cg_guid = cg_data.get('data', {}).get('guid', '')
            cg_sk = cg_data.get('data', {}).get('secretKey', '')
            if cg_guid or cg_sk:
                saved = load_device_state() or {}
                if not saved.get('guid') and cg_guid:
                    saved['guid'] = cg_guid
                if not saved.get('secretKey') and cg_sk:
                    saved['secretKey'] = cg_sk
                save_device_state(saved)
                dbg(f'从cloud/get更新guid/secretKey, 已保存')
    else:
        print('[10-11/13] cloud: SKIP (已注册设备)')

    # [12] 新设备预热 30s (如果前面[0]已经等过了就跳过)
    if is_new and not reg_done:
        print('[12] 预热 30s...')
        time.sleep(30)
        hb_ts = str(int(time.time() * 1000))
        hb_warmup = make_hb_body(hb_ts)
        r = sess.post(
            'https://collect.cctv.cn/cctvmobileinf/rest/cctv/receive/new/app',
            data='info=' + requests.utils.quote(json.dumps(hb_warmup, separators=(',', ':'))),
            headers=make_headers(xuid, fp, aid, hb_ts, 'application/x-www-form-urlencoded; charset=UTF-8'),
            timeout=15
        )
        dbg(f'warmup hb: succeed={r.json().get("succeed")}')
    else:
        print('[12] 预热: SKIP (已注册设备)')

    # [12.5] live 前最后一次心跳 (保持session活跃)
    print('[12.5] live前心跳...')
    pre_live_hb_ts = str(int(time.time() * 1000))
    hb_pre = make_hb_body(pre_live_hb_ts)
    r = sess.post(
        'https://collect.cctv.cn/cctvmobileinf/rest/cctv/receive/new/app',
        data='info=' + requests.utils.quote(json.dumps(hb_pre, separators=(',', ':'))),
        headers=make_headers(xuid, fp, aid, pre_live_hb_ts, 'application/x-www-form-urlencoded; charset=UTF-8'),
        timeout=15
    )
    dbg(f'pre-live hb: succeed={r.json().get("succeed")}')

    # [13] live/v1/01
    print('[13/15] live/v1/01...')
    live_ts = str(int(time.time() * 1000))
    saved = load_device_state() or {}
    user_id = saved.get('secretKey') or saved.get('guid', '').rsplit('-', 1)[0] or LIVE_UID
    cloud_guid = saved.get('guid', '')
    live_body = json.dumps({
        'screenParam': dev['screen'],
        'rate': '',
        'systemType': 'ios',
        'model': dev['model'],
        'id': channel_id,
        'userId': user_id,
        'clientSign': 'cctvVideo',
        'deviceId': {'serial': '', 'imei': '', 'android_id': aid},
    }, separators=(',', ':'))
    live_h = make_headers(xuid, fp, aid, live_ts)
    dbg(f'body={live_body}')
    dbg(f'body_len={len(live_body)}')
    dbg(f'headers={json.dumps(live_h, indent=2)}')

    r = sess.post(
        'https://ytpaddr.cctv.cn/gsnw/api/live/v1/01',
        data=live_body,
        headers=live_h,
        timeout=15
    )
    j = r.json()
    print(f'     result={j.get("result")} time={j.get("time")} errCode={j.get("errCode")}')
    if j.get('result') != '0':
        dbg(f'live FAILED: {json.dumps(j, ensure_ascii=False)[:400]}')
        log_r(r, 'live')
        return None

    videos = j['data'].get('videoList') or j['data'].get('videos')
    if not videos or not videos[0]:
        dbg('no videos in response')
        return None

    raw_url = aes_gcm_decrypt(videos[0]['url'], session_key)
    print(f'     码率: {videos[0].get("rateName", videos[0].get("rate"))}')
    print(f'     rawUrl: {raw_url[:80]}...')

    # [14] live/v1/02
    print('[14/15] live/v1/02...')
    r = sess.post(
        'https://ytpaddr.cctv.cn/gsnw/api/live/v1/02',
        json={'guid': aes_gcm_encrypt(cloud_guid, session_key)},
        headers=make_headers(xuid, fp, aid, str(int(time.time() * 1000))),
        timeout=15
    )
    j = r.json()
    if j.get('result') != '0':
        dbg(f'live/v1/02 FAILED: {json.dumps(j, ensure_ascii=False)[:200]}')
        return None
    app_secret = aes_gcm_decrypt(j['data']['appSecret'], session_key)
    dbg(f'appSecret={app_secret[:20]}...')

    # getstream
    print('     getstream...')
    rand = '%08x-%04x-%04x-%04x-%012x' % tuple(int.from_bytes(os.urandom(b), 'big') for b in [4, 2, 2, 2, 6])
    app_sign = hashlib.md5((APPID + app_secret + rand).encode()).hexdigest()
    gs_h = make_headers(xuid, fp, aid, str(int(time.time() * 1000)), 'application/x-www-form-urlencoded')
    gs_h['APPID'] = APPID
    gs_h['APPSIGN'] = app_sign
    gs_h['APPRANDOMSTR'] = rand

    r = sess.post(
        'https://ytpvdn.cctv.cn/cctvmobileinf/rest/cctv/videoliveUrl/getstream',
        data='appcommon=' + requests.utils.quote(appcommon) + '&url=' + requests.utils.quote(raw_url),
        headers=gs_h, timeout=15
    )
    j = r.json()
    if j.get('succeed') == 1:
        return j.get('url')
    dbg(f'getstream FAILED: {json.dumps(j, ensure_ascii=False)[:200]}')
    return None

# ═══════════ 设备持久化 (匹配Rust device-state-rs.json) ═══════════
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cctv_device.json')

def load_device_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return None

def save_device_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

# ═══════════ 入口 ═══════════

if __name__ == '__main__':
    channel = sys.argv[1] if len(sys.argv) > 1 else 'cctv5'
    channel_id = CHANNELS.get(channel, CHANNELS['cctv5'])

    print('=' * 50)
    print(f'CCTV YSP 直播流 - Python (IDA逆向)')
    print(f'频道: {channel} ({channel_id})')
    print(f'设备池: {len(DEVICE_POOL)} 款真机')
    print(f'持久化: {STATE_FILE}')
    print('=' * 50)

    state = load_device_state()
    if state:
        # 复用已注册设备
        dev = state['dev']
        aid = state['aid']
        mac = state['mac']
        xuid = state['xuid']
        print(f'\n── 复用设备: {dev["brand"]} {dev["model"]} (已注册) ──')
    else:
        # 全新设备
        dev = random.choice(DEVICE_POOL)
        aid = gen_aid()
        mac = gen_mac()
        xuid = compute_xuid(dev, aid, mac)
        print(f'\n── 新设备: {dev["brand"]} {dev["model"]} ──')

    url = resolve(channel_id, dev, aid, mac, xuid, is_new=(state is None))
    if url:
        print(f'\n✓ 成功!')
        print(f'M3U8: {url}')
    else:
        print(f'\n✗ 失败')
        print(f'[提示] cloud/register后需等待服务器信任, 1-2分钟后再跑 python3 cctv_live.py')
