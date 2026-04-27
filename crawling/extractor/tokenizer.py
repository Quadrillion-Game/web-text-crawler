"""形態素解析によるトークナイザー。"""

import fugashi

_tagger = fugashi.Tagger()
_SKIP_POS = {"補助記号", "空白"}


def tokenize(text: str) -> list[str]:
    """テキストを形態素解析し、単語リストを返す。"""
    tokens = []
    for word in _tagger(text):
        if word.feature.pos1 in _SKIP_POS:
            continue
        tokens.append(word.surface)
    return tokens
