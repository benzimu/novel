#!/usr/bin/env python
#  -*- coding:utf-8 -*-

"""
@author: ben
@time: 4/21/17
@desc: 
"""


import re
from urlparse import urlparse


def get_domain(url):
    """
    解析url，获取顶级域名
    :param url:
    :return:
    """
    top_host_postfix = (
        '.com', '.la', '.io', '.co', '.info', '.net', '.org', '.me', '.mobi',
        '.us', '.biz', '.xxx', '.ca', '.co.jp', '.com.cn', '.net.cn',
        '.org.cn', '.mx', '.tv', '.ws', '.ag', '.com.ag', '.net.ag',
        '.org.ag', '.am', '.asia', '.at', '.be', '.com.br', '.net.br',
        '.bz', '.com.bz', '.net.bz', '.cc', '.com.co', '.net.co',
        '.nom.co', '.de', '.es', '.com.es', '.nom.es', '.org.es',
        '.eu', '.fm', '.fr', '.gs', '.in', '.co.in', '.firm.in', '.gen.in',
        '.ind.in', '.net.in', '.org.in', '.it', '.jobs', '.jp', '.ms',
        '.com.mx', '.nl', '.nu', '.co.nz', '.net.nz', '.org.nz',
        '.se', '.tc', '.tk', '.tw', '.com.tw', '.idv.tw', '.org.tw',
        '.hk', '.co.uk', '.me.uk', '.org.uk', '.vg', ".com.hk")

    regx = r'[^\.]+(' + '|'.join([h.replace('.', r'\.') for h in top_host_postfix]) + ')$'
    pattern = re.compile(regx, re.IGNORECASE)

    if not url:
        return None
    parts = urlparse(url)
    host = parts.netloc
    m = pattern.search(host)
    res = m.group() if m else host

    return res


