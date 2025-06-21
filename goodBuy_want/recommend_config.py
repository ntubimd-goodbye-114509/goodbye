# -------------------------
# 熱門 Want 推薦權重
# -------------------------
WANT_HOT_WEIGHTS = {
    'recent_views': 1,     # 每次被瀏覽 +1
    'recent_replies': 5,   # 每次被回覆 +5
}

WANT_HOT_PROPORTIONS = {
    'recent_views': 0.4,
    'recent_replies': 0.6,
}

# -------------------------
# 個性化 Want 推薦權重
# -------------------------
WANT_PERSONAL_WEIGHTS = {
    'search_keyword': 4,              # 搜尋關鍵字匹配
    'viewed_related_multiplier': 0.7, # 觀看過相關 want 的關鍵字提取
    'replied_related_bonus': 2,       # 回覆過相關 want 的 tag 關聯加分
}

WANT_PERSONAL_PROPORTIONS = {
    'search_history': 0.4,
    'viewed_related': 0.4,
    'replied_related': 0.2,
}

# -------------------------
# Want 關鍵字匹配加權
# -------------------------
WANT_KEYWORD_SCORES = {
    'tags': 5,
    'title': 3,
    'post_text': 2,
}

WANT_KEYWORD_PROPORTIONS = {
    'tags': 0.5,
    'title': 0.3,
    'post_text': 0.2,
}

# -------------------------
# 已推薦加權調整
# -------------------------
RECOMMENDED_WANT_WEIGHT_MULTIPLIER = 0.5

# -------------------------
# 查詢時間範圍
# -------------------------
WANT_SEARCH_HISTORY_DAYS = 3
WANT_VIEW_DAYS = 14
WANT_REPLY_DAYS = 14
