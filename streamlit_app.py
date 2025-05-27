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

# 轉成字典方便查牌名
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

# ----------------- 取得運勢 -------------------
def get_fake_horoscope(zodiac_en):
    mood = random.choice(["愉快", "焦慮", "輕鬆", "自信", "混亂"])
    advice = random.choice([
        "嘗試與朋友聊聊心事",
        "今天適合休息充電",
        "做些能讓你快樂的小事吧",
        "勇敢嘗試新挑戰",
        "保持冷靜，別衝動"
    ])
    return f"今天的心情可能會有些{mood}，建議你：{advice}。"

# ----------------- 塔羅解析 -------------------
def explain_tarot(card_zh, upright):
    direction = "正向" if upright == "正位" else "反思"
    return f"抽到「{card_zh}」這張牌，代表目前處於{direction}的能量狀態，值得多留意內心的感受與直覺。"

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

# ----------------- Streamlit 介面 -------------------
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
