# -*- coding: utf-8 -*
import re


def analysis_reconfigure_result(lines):
    """
    分析kolla-ansible reconfigure -i ~/multinode –t cinder结果，并转化成dic
    :param lines:
    :return: [{u'node': u'node1', u'unreachable': u'0', u'changed': u'0', u'ok': u'75', u'failed': u'0'}]
    """

    # 正则r'.+ok=\d.+\schanged=\d.+\sunreachable=\d.+\sfailed=\d
    # 查找字符串  node1                      : ok=65   changed=0    unreachable=0    failed=1
    # 返回一个字典组，格式 [{'node': 'node2', 'unreachable': '0', 'changed': '0', 'ok': '142', 'failed': '0'}]
    maplist = []
    success = True
    for line in reversed(lines):
        # 将正则表达式编译成Pattern对象
        pattern = re.compile(r'.+ok=\d.+\schanged=\d.+\sunreachable=\d.+\sfailed=\d')
        # 使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
        match = pattern.search(line)
        if match:
            # 使用Match获得分组信息
            result = match.group()
            map = {}
            map['node'], result = re.compile(r'\s*:\s*').split(result.strip())
            p = re.compile(r'\s+')
            for item in p.split(result.strip()):
                list = item.split('=')
                key = list[0]
                val = list[1]
                map[key] = val
            if int(map['failed']) > 0:
                success = False
            maplist.append(map)
    return success, maplist


def test1():
    file_object = open(r'D:\wangyueWorkspace\mytest\kolla.log')
    try:
        all_the_text = file_object.readlines()
        success, list = analysis_reconfigure_result(all_the_text)
        print('====%s===%s' % (success, list))
    finally:
        file_object.close()


if __name__ == '__main__':
    test1()
