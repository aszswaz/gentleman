"""
测试正则表达式
"""

import re

if __name__ == '__main__':
    demo_str = "abcdefghijklmnopqrstuvwxyz0123456789"
    reg = re.compile('\\?')
    result = reg.search(demo_str)
    print(result and result.group(0))
    pass
