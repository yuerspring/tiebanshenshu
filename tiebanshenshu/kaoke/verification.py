"""候选核验：没有唯一匹配时，不默认选择基本卦。"""


def select_verified_candidate(candidates, db=None, verify_condition=None):
    """核验基本卦及变卦；回调代表调用者条件，不代表书籍准确性证明。"""
    verses = getattr(db, 'FORTUNE_DUANYU_MAP', {})
    matched = []
    for index, candidate in enumerate(candidates):
        entry = verses.get(candidate['number'])
        candidate['duanyu'] = entry[0] if entry is not None else ''
        candidate['match'] = (
            bool(verify_condition(candidate['number'], candidate['duanyu']))
            if verify_condition is not None else False
        )
        if candidate['match']:
            matched.append(index)
    if verify_condition is None:
        status = 'not_provided'
    elif not matched:
        status = 'no_match'
    elif len(matched) > 1:
        status = 'ambiguous'
    else:
        status = 'unique_candidate'
    return {
        'status': status,
        'matched_indices': matched,
        'candidate': candidates[matched[0]] if status == 'unique_candidate' else None,
    }
