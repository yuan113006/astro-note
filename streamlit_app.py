import streamlit as st
from PIL import Image
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# ----------------- 基本資料 -------------------
SHEET_ID = '1VbZQlZgWm2QSnHNCXp08MiOr-ZZ3s1GXN_fhHxgA19s'
WORKSHEET_NAME = '工作表1'

# ----------------- 塔羅牌資料 -------------------
tarot_cards = [
    ("The Fool", "愚者"), ("The Magician", "魔術師"), ("The High Priestess", "女祭司"),
    ("The Empress", "皇后"), ("The Emperor", "皇帝"), ("The Hierophant", "教皇"),
    ("The Lovers", "戀人"), ("The Chariot", "戰車"), ("Strength", "力量"),
    ("The Hermit", "隱者"), ("Wheel of Fortune", "命運之輪"), ("Justice", "正義"),
    ("The Hanged Man", "吊人"), ("Death", "死神"), ("Temperance", "節制"),
    ("The Devil", "惡魔"), ("The Tower", "高塔"), ("The Star", "星星"),
    ("The Moon", "月亮"), ("The Sun", "太陽"), ("Judgement", "審判"),
    ("The World", "世界")
]
tarot_dict = dict(tarot_cards)

# ----------------- 星座轉換 -------------------
zodiac_map = {
    "牡羊座": "aries", "金牛座": "taurus", "雙子座": "gemini", "巨蟹座": "cancer",
    "獅子座": "leo", "處女座": "virgo", "天秤座": "libra", "天蠍座": "scorpio",
    "射手座": "sagittarius", "魔羯座": "capricorn", "水瓶座": "aquarius", "雙魚座": "pisces"
}

# ----------------- 抽牌 -------------------
def draw_tarot():
    card_en, card_zh = random.choice(tarot_cards)
    upright = random.choice(["正位", "逆位"])
    return card_en, card_zh, upright

# ----------------- 星座運勢 -------------------
def get_fake_horoscope(zodiac_en):
    horoscope_map = {
        "aries": "今天你充滿行動力，適合展開新計畫。別害怕冒險，宇宙挺你！",
        "taurus": "穩定是今天的關鍵字，踏實前進會帶來預期的成果。",
        "gemini": "溝通特別順利，適合表達自己或與朋友談心。",
        "cancer": "情緒起伏較大，給自己一點空間，慢慢來就好。",
        "leo": "你會成為眾人目光的焦點，發揮你的魅力吧！",
        "virgo": "今天適合整理生活與思緒，清理將帶來新能量。",
        "libra": "人際關係和諧，適合參與社交或處理合作事務。",
        "scorpio": "內在直覺很強，相信你的直覺，事情會有轉機。",
        "sagittarius": "冒險的心又被喚醒，不妨計畫一場短旅行。",
        "capricorn": "專注於目標會有好成果，努力會有回報。",
        "aquarius": "創意湧現，不妨動手嘗試新的點子或計畫。",
        "pisces": "情感豐富的一天，與人連結能帶來溫暖。"
    }
    return horoscope_map.get(zodiac_en, "今天是觀察內心的一天，給自己多一點時間思考。")

# ----------------- 塔羅解析 -------------------
tarot_meanings = {
    "愚者": ("新開始、冒險與無限可能。", "衝動、天真，可能缺乏準備。"),
    "魔術師": ("掌握資源，開始行動的最佳時機。", "操弄或欺瞞，需小心現實與假象。"),
    "女祭司": ("直覺與內在智慧，適合靜心與觀察。", "壓抑情緒、誤解直覺訊息。"),
    "皇后": ("豐盛、愛與照顧他人。", "過度付出，忽略自己的需求。"),
    "皇帝": ("權威、穩定與結構。", "控制欲強，缺乏彈性。"),
    "教皇": ("傳統、智慧與學習。", "教條主義、盲從規範。"),
    "戀人": ("愛、選擇與內在連結。", "關係緊張或難以做出選擇。"),
    "戰車": ("意志力與勝利，克服障礙。", "衝動行事，忽略他人感受。"),
    "力量": ("內在勇氣、溫柔而堅定。", "缺乏自信、情緒起伏大。"),
    "隱者": ("尋求內在智慧、獨處與省思。", "孤立、逃避現實或封閉。"),
    "命運之輪": ("轉變與好運，新的契機到來。", "不穩定與不可控的變化。"),
    "正義": ("公平、平衡與誠實面對問題。", "偏見、不公或責任逃避。"),
    "吊人": ("等待、犧牲與新視角。", "拖延、停滯不前，固執己見。"),
    "死神": ("結束與重生，蛻變時刻。", "抗拒改變，停滯不前。"),
    "節制": ("平衡、療癒與合作。", "失衡、情緒或能量分裂。"),
    "惡魔": ("欲望、束縛與成癮。", "擺脫負面模式的契機。"),
    "高塔": ("突發事件、崩解與重建。", "抗拒改變可能帶來更大衝擊。"),
    "星星": ("希望、靈感與新希望的開始。", "失望、缺乏信心或方向感。"),
    "月亮": ("潛意識、幻象與直覺。", "混亂、迷惘與自我欺騙。"),
    "太陽": ("喜悅、成功與光明。", "自我中心、過度樂觀。"),
    "審判": ("覺醒、重生與反思過往。", "逃避責任、停滯不前。"),
    "世界": ("完成、圓滿與進入新階段。", "未完成的課題與遺憾。")
}

def explain_tarot(card_zh, upright):
    meanings = tarot_meanings.get(card_zh, ("神秘能量圍繞著你。", "可能的挑戰等待探索。"))
    return meanings[0] if upright == "正位" else meanings[1]

# ----------------- 儲存 Google Sheet -------------------
def save_to_google_sheet(name, zodiac_tw, card_en, upright, horoscope, moodlog):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials_dict = st.secrets["GCP_SERVICE_ACCOUNT_JSON"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    card_zh = tarot_dict.get(card_en, "未知牌")
    tarot_msg = explain_tarot(card_zh, upright)

    sheet.append_row([now, name, zodiac_tw, card_zh, upright, horoscope, tarot_msg, moodlog])

# ----------------- Streamlit UI -------------------
st.set_page_config(page_title="占星筆記", page_icon="🔮")
st.title("🌟 占星筆記：每日塔羅與星座運勢")

name = st.text_input("請輸入你的姓名：")
zodiac_tw = st.selectbox("請選擇你的星座：", list(zodiac_map.keys()))
moodlog = st.text_area("寫下你今天的心情或瑣事：")

if st.button("🔮 開始占卜"):
    if not name or not zodiac_tw:
        st.warning("請完整填寫姓名與星座！")
    else:
        card_en, card_zh, upright = draw_tarot()
        zodiac_en = zodiac_map[zodiac_tw]
        horoscope = get_fake_horoscope(zodiac_en)
        tarot_msg = explain_tarot(card_zh, upright)

        st.markdown(f"### 👤 {name} 的今日筆記")
        st.markdown(f"- 🌠 星座：{zodiac_tw}")
        st.markdown(f"- 🔮 塔羅：{card_zh}（{upright}）")
        st.markdown(f"- 🧿 塔羅解析：{tarot_msg}")
        st.markdown(f"- 💫 今日運勢：{horoscope}")

        try:
            image = Image.open(f"tarot_images/{card_en}.png")
            st.image(image, caption=f"{card_zh}（{upright}）", width=180)
        except Exception as e:
            st.error("找不到對應的塔羅牌圖片！")

        save_to_google_sheet(name, zodiac_tw, card_en, upright, horoscope, moodlog)
        st.success("已記錄到 Google 試算表 ✅")
