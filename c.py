VARIATION_SELECTOR_START = 0xfe00
VARIATION_SELECTOR_END = 0xfe0f

VARIATION_SELECTOR_SUPPLEMENT_START = 0xe0100
VARIATION_SELECTOR_SUPPLEMENT_END = 0xe01ef


def to_variation_selector(byte):
    """
    将字节转换为变体选择器

    Args:
        byte (int): 要转换的字节

    Returns:
        str|None: 变体选择器字符或None
    """
    if 0 <= byte < 16:
        return chr(VARIATION_SELECTOR_START + byte)
    elif 16 <= byte < 256:
        return chr(VARIATION_SELECTOR_SUPPLEMENT_START + byte - 16)
    else:
        return None


def from_variation_selector(code_point):
    """
    从变体选择器转换为字节

    Args:
        code_point (int): 变体选择器的码点

    Returns:
        int|None: 字节或None
    """
    if VARIATION_SELECTOR_START <= code_point <= VARIATION_SELECTOR_END:
        return code_point - VARIATION_SELECTOR_START
    elif (VARIATION_SELECTOR_SUPPLEMENT_START <= code_point <=
          VARIATION_SELECTOR_SUPPLEMENT_END):
        return code_point - VARIATION_SELECTOR_SUPPLEMENT_START + 16
    else:
        return None


def encode(text, carrier):
    """
    将文本编码到一段文本中

    Args:
        text (str): 要隐藏的文本
        carrier (str): 承载隐藏文本的文本

    Returns:
        str: 编码后的文本
    """
    # 将字符串转换为utf-8字节
    bytes_data = text.encode('utf-8')

    # 如果carrier是空字符串，使用默认字符
    if not carrier:
        carrier = "A"

    # 将字节分布到carrier的每个字符中
    carrier_chars = list(carrier)
    result = ""

    # 如果隐藏文字字节少于载体文本，使用随机算法分散
    if len(bytes_data) <= len(carrier_chars):
        # 创建一个随机位置数组，用于随机分布字节
        import random
        positions = list(range(len(carrier_chars)))

        # 随机打乱位置数组
        random.shuffle(positions)

        # 选择前bytes_data个位置用于插入变体选择器
        selected_positions = sorted(positions[:len(bytes_data)])

        # 构建结果字符串，在选定的位置插入变体选择器
        byte_index = 0
        for i in range(len(carrier_chars)):
            result += carrier_chars[i]

            # 检查当前位置是否是选定的位置之一
            if i in selected_positions and byte_index < len(bytes_data):
                selector = to_variation_selector(bytes_data[byte_index])
                if selector:
                    result += selector
                byte_index += 1
    else:
        # 如果隐藏文字字节多于载体文本，将多余的字节叠加到最后一个字符
        byte_index = 0

        # 先处理能均匀分配到载体字符的字节
        for i in range(len(carrier_chars)):
            result += carrier_chars[i]

            # 如果还有字节需要处理
            if byte_index < len(bytes_data):
                selector = to_variation_selector(bytes_data[byte_index])
                if selector:
                    result += selector
                byte_index += 1

        # 将剩余的字节全部叠加到最后一个字符
        while byte_index < len(bytes_data):
            selector = to_variation_selector(bytes_data[byte_index])
            if selector:
                result += selector
            byte_index += 1

    return result


def decode(encoded_text):
    """
    从编码文本中解码隐藏的文本

    Args:
        encoded_text (str): 编码后的文本

    Returns:
        str: 解码后的文本
    """
    decoded = []
    chars = list(encoded_text)

    # 遍历每个字符，检查其后是否有变体选择器
    i = 0
    while i < len(chars):
        # 检查当前字符后的所有连续变体选择器
        i_next = i + 1
        while i_next < len(chars):
            next_char = chars[i_next]
            byte = from_variation_selector(ord(next_char))

            if byte is not None:
                decoded.append(byte)
                i_next += 1
            else:
                break  # 如果不是变体选择器，退出内部循环

        i = i_next

    # 将字节数组转换回字符串
    return bytes(decoded).decode('utf-8')


def clean_hidden_text(text):
    """
    清除文本中的隐藏内容（变体选择器）

    Args:
        text (str): 包含隐藏内容的文本

    Returns:
        str: 清除隐藏内容后的文本
    """
    if not text:
        return ''

    result = ''

    for char in text:
        code_point = ord(char)

        # 添加非变体选择器字符到结果中
        if not (
                (VARIATION_SELECTOR_START <= code_point <= VARIATION_SELECTOR_END) or
                (VARIATION_SELECTOR_SUPPLEMENT_START <= code_point <= VARIATION_SELECTOR_SUPPLEMENT_END)
        ):
            result += char

    return result


a = encode("123", "hello")
b = decode(a)
print(a)
print(b)
c = clean_hidden_text(a)
d = decode(c)
print(c)
print(d)
