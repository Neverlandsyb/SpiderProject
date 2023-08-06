import re
import base64
import struct
import requests
import xxhash
import plistlib
from plistlib import FMT_BINARY, _BinaryPlistParser, _undefined


def rc4(string, sec_key):
    assert isinstance(sec_key, str), "sec_key 为字符串"

    string_length = len(string)
    box = list(range(256))
    randkey = []

    key_length = len(sec_key)

    sec_key = list(map(ord, sec_key))

    # Init sbox
    for i in range(256):
        randkey.append(sec_key[i % key_length])

    # Key setup
    j = 0
    for i in range(256):
        j = (j + box[i] + randkey[i]) % 256
        box[i], box[j] = box[j], box[i]  # swap

    S = range(256)
    # Pseudo-random generation algorithm
    # 此算法保证每256次循环中S盒的每个元素至少被交换过一次。
    result = []
    a = j = 0
    for i in range(string_length):
        a = (a + 1) % 256
        j = (j + box[a]) % 256

        box[a], box[j] = box[j], box[a]  # swap
        # 以上再次进行了打乱
        # 真正的明文string逐字节与box中的随机值异或生成加密的result
        # 不管怎么随机打乱，由于cryptkey以及string_length总是一样的，因此box最终也一样
        # 解密时，密文在与box异或则返回明文

        result.append(string[i] ^ (box[(box[a] + box[j]) % 256]))
    return bytearray(result)


def _read_object(self, ref):
    result = self._objects[ref]
    if result is not _undefined:
        return result

    offset = self._object_offsets[ref]
    self._fp.seek(offset)
    token = self._fp.read(1)[0]
    token_h, token_l = token & 0xF0, token & 0x0F

    if token == 0x00:
        result = None

    elif token == 0x08:
        result = False

    elif token == 0x09:
        result = True

    elif token == 0x0f:
        result = b''

    elif token_h == 0x10:  # int
        result = int.from_bytes(self._fp.read(1 << token_l),
                                "big", signed=token_l >= 3)

    elif token == 0x22:  # real
        result = struct.unpack(">f", self._fp.read(4))[0]

    elif token == 0x23:  # real
        result = struct.unpack(">d", self._fp.read(8))[0]

    elif token_h == 0x40:  # ascii string
        s = self._get_size(token_l)
        result = self._fp.read(s).decode("ascii")
        result = result

    elif token_h == 0x50:  # unicode string
        s = self._get_size(token_l)
        result = self._fp.read(s * 2).decode("utf-16be")

    elif token_h == 0xA0:  # array
        s = self._get_size(token_l)
        obj_refs = self._read_refs(s)
        result = []
        self._objects[ref] = result
        result.extend(self._read_object(x) for x in obj_refs)

    elif token_h == 0xD0:  # dict
        s = self._get_size(token_l)
        key_refs = self._read_refs(s)
        obj_refs = self._read_refs(s)
        result = self._dict_type()
        self._objects[ref] = result
        for k, o in zip(key_refs, obj_refs):
            result[self._read_object(k)] = self._read_object(o)

    self._objects[ref] = result
    return result


# 利用猴子补丁，修改源代码的方法
# python 3.6.8。其它版本可能不行。自行修改补丁即可。
_BinaryPlistParser._read_object = _read_object


def o_encrypt(data):
    a = base64.b64decode(data)
    i = 16
    s = max((len(a) - 2 * i) // 3, 0)
    u = a[s: s + i]
    a = a[0: s] + a[s + i:]
    sec_key = xxhash.xxh64_hexdigest(u, 41405)
    # print(sec_key)

    text = rc4(a, sec_key)

    data = plistlib.loads(text, fmt=FMT_BINARY)
    return data


class DoubanSpider:
    """
    豆瓣搜索api
    """

    def __init__(self):
        self.URL = "https://search.douban.com/movie/subject_search?"
        self.HEADERS = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                      "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/78.0.3904.70 Safari/537.36",
        }

    def get_result(self):
        """
        获取加密window_data、解密得结果
        :return:
        """
        params = {
            "search_text": "黄晓明",
            "cat": 1002,
            "start": 15
        }
        response = requests.get(self.URL, params=params, headers=self.HEADERS)
        window_data = re.findall('window.__DATA__ = "(.*?)"', response.text)
        r = window_data[0]  # 加密的数据

        fin_data = o_encrypt(r)

        print(fin_data)


if __name__ == '__main__':
    spider = DoubanSpider()
    spider.get_result()
