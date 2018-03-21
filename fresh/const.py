# coding: utf-8


class FreshSource(object):
    missfresh = 1
    sevenfresh = 2

    @classmethod
    def get_text(cls, source):
        return {cls.missfresh: '每日优鲜',
                cls.sevenfresh: '7 Fresh'}.get(source)
