# coding: utf-8


class FreshSource(object):
    missfresh = 1
    sevenfresh = 2
    dmall = 3

    @classmethod
    def get_text(cls, source):
        return {cls.missfresh: '每日优鲜',
                cls.dmail: '多点',
                cls.sevenfresh: '7 Fresh'}.get(source)
