# coding=utf-8

import jieba
import os
from whoosh.analysis import Tokenizer
from whoosh.fields import *
from whoosh.analysis import Token
from whoosh.index import create_in, open_dir

class ChineseTokenizer(Tokenizer):
    """
    中文分词解析器
    """
    def __call__(self, value, positions=False, chars=False,
                 keeporiginal=True, removestops=True, start_pos=0, start_char=0,
                 mode='', **kwargs):
        assert isinstance(value, text_type), "%r is not unicode "% value
        t = Token(positions, chars, removestops=removestops, mode=mode, **kwargs)
        list_seg = jieba.cut_for_search(value)  ## 使用了结巴分词的机制
        for w in list_seg:
            t.original = t.text = w
            t.boost = 0.5
            if positions:
                t.pos = start_pos + value.find(w)
            if chars:
                t.startchar = start_char + value.find(w)
                t.endchar = start_char + value.find(w) + len(w)
            yield t


def chinese_analyzer():
    return ChineseTokenizer()


class MyWhoosh:

    @staticmethod
    def create_index(document_dir):
        analyzer = chinese_analyzer()
        schema = Schema(titel=TEXT(stored=True, analyzer=analyzer), path=ID(stored=True),
                        content=TEXT(stored=True, analyzer=analyzer))
        ix = create_in("./", schema)  
        writer = ix.writer()
        for parents, dirnames, filenames in os.walk(document_dir):
            for filename in filenames:
                title = filename.replace(".txt", "").decode('utf8')　## 文件名作为标题
                content = open(document_dir + '/' + filename, 'r').read().decode('utf-8')  ## 评论内容做内容
                path = u"/b" ## 文件保存的物理路径
                writer.add_document(titel=title, path=path, content=content)
        writer.commit()

    @staticmethod
    def search(search_str):
        title_list = []
        ix = open_dir("./")
        searcher = ix.searcher()
        print search_str,type(search_str)
        results = searcher.find("content", search_str)
        for hit in results:
            print hit['titel']  ##　检索结果的标题
            print hit.score  ## 检索结果的排序得分
            print hit.highlights("content", top=10) ##　检索的强调部分
            title_list.append(hit['titel'])
        return title_list


MyWhoosh.search(u"速度与激情")





