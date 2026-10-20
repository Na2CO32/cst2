"""產生 apps-script/TestData.gs：網站的虛構測試資料（含程式繪製的圖片）。

所有人名、Email、地址、事件皆為虛構；Email 一律使用保留網域 example.com。
圖片是抽象幾何圖案與字母頭像，不含任何真實照片。

用法：python3 tools/gen_test_data.py
"""
import base64
import io
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'apps-script' / 'TestData.gs'
rng = random.Random(20261020)


def L(zh, en):
    return {'zh': zh, 'en': en}


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def to_data_url(img, quality=78):
    buf = io.BytesIO()
    img.convert('RGB').save(buf, 'JPEG', quality=quality, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def gradient(w, h, c1, c2):
    a, b = hex_rgb(c1), hex_rgb(c2)
    img = Image.new('RGB', (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            t = (x / w + y / h) / 2
            px[x, y] = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return img


def photo(w, h, c1, c2, kind):
    img = gradient(w, h, c1, c2).convert('RGBA')
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if kind == 0:   # 山與太陽
        r = h * 0.2
        d.ellipse([w * 0.72 - r, h * 0.3 - r, w * 0.72 + r, h * 0.3 + r], fill=(255, 255, 255, 90))
        d.polygon([(0, h), (w * 0.35, h * 0.45), (w * 0.62, h * 0.8), (w * 0.8, h * 0.55), (w, h * 0.75), (w, h)], fill=(0, 0, 0, 55))
    elif kind == 1:  # 螢幕
        d.rounded_rectangle([w * 0.15, h * 0.2, w * 0.85, h * 0.75], 14, fill=(255, 255, 255, 60))
        d.rounded_rectangle([w * 0.22, h * 0.28, w * 0.78, h * 0.67], 8, fill=(0, 0, 0, 45))
        d.rectangle([w * 0.45, h * 0.75, w * 0.55, h * 0.85], fill=(255, 255, 255, 60))
    elif kind == 2:  # 泡泡
        for _ in range(9):
            r = rng.uniform(h * 0.05, h * 0.22)
            x, y = rng.uniform(0, w), rng.uniform(0, h)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, rng.randint(35, 80)))
    else:            # 網路節點
        pts = [(rng.uniform(w * 0.1, w * 0.9), rng.uniform(h * 0.1, h * 0.9)) for _ in range(14)]
        for i, p in enumerate(pts):
            for q in pts[i + 1:]:
                if abs(p[0] - q[0]) + abs(p[1] - q[1]) < w * 0.35:
                    d.line([p, q], fill=(255, 255, 255, 70), width=2)
        for x, y in pts:
            d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(255, 255, 255, 170))
    return to_data_url(Image.alpha_composite(img, layer))


def find_font(size):
    for f in ['DejaVuSans-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'arial.ttf']:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default(size)


def avatar(color, letter):
    img = gradient(300, 300, color, '#0b1a33')
    d = ImageDraw.Draw(img)
    d.text((150, 150), letter, font=find_font(140), fill='white', anchor='mm')
    return to_data_url(img, 82)


members = [
    ('林語晨', 'Yuchen Lin', '隊長', 'Team Lead', '統籌團隊工作分配與學期計畫，對接各處室需求。\n主持每週例會並追蹤任務進度。', 'Coordinates assignments and the semester plan, and liaises with school offices.\nRuns the weekly meeting and tracks progress.', 'Y', '#2563eb'),
    ('張浩宇', 'Haoyu Zhang', '副隊長', 'Deputy Lead', '協助隊長管理專案，負責新成員培訓課程。', 'Supports the lead on projects and runs onboarding for new members.', 'H', '#7c3aed'),
    ('許芷涵', 'Zhihan Hsu', '前端工程師', 'Front-end Developer', '負責校園系統的網頁介面開發與無障礙檢查。', 'Builds web interfaces for campus systems and checks accessibility.', 'Z', '#0891b2'),
    ('周柏翰', 'Bohan Chou', '後端工程師', 'Back-end Developer', '維護表單與資料庫服務，撰寫自動化排程。', 'Maintains form and database services and writes automation jobs.', 'B', '#059669'),
    ('黃予安', 'Yuan Huang', '硬體維修', 'Hardware Technician', '負責教室電腦、投影設備的定期檢查與故障排除。', 'Handles routine checks and repairs for classroom computers and projectors.', 'A', '#d97706'),
    ('吳品睿', 'Pinrui Wu', '網路管理', 'Network Admin', '管理校內無線網路設定，記錄並追蹤網路問題回報。', 'Manages campus Wi-Fi settings and tracks network issue reports.', 'P', '#dc2626'),
    ('蔡沐恩', 'Muen Tsai', '視覺設計', 'Visual Designer', '設計活動海報、團隊識別與系統介面視覺。', 'Designs event posters, team branding and interface visuals.', 'M', '#db2777'),
    ('鄭以樂', 'Yile Cheng', '資訊安全', 'Security Analyst', '進行系統弱點檢查，推廣校園資安觀念。', 'Runs vulnerability checks on systems and promotes security awareness.', 'E', '#4f46e5'),
]

projects = [
    (L('社團報名系統', 'Club Sign-up System'), L('網站', 'Web'), L('讓學生線上選填社團志願並自動分發，取代紙本作業。', 'Lets students rank clubs online with automatic placement, replacing paper forms.')),
    (L('設備借用平台', 'Equipment Loan Platform'), L('網站', 'Web'), L('記錄平板、相機等設備的借還狀況，逾期自動提醒。', 'Tracks loans of tablets and cameras with automatic overdue reminders.')),
    (L('教室電腦健檢', 'Classroom PC Check-up'), L('維修', 'Repair'), L('每學期巡檢 120 台教室電腦，更新系統並清理硬體。', 'Inspects 120 classroom PCs each semester, updating systems and cleaning hardware.')),
    (L('校園 Wi-Fi 熱點圖', 'Campus Wi-Fi Map'), L('網路', 'Network'), L('實地量測訊號強度，產出熱點圖協助調整基地台位置。', 'Measured signal strength on site to map coverage and reposition access points.')),
    (L('公告推播機器人', 'Announcement Bot'), L('應用程式', 'App'), L('把學校公告自動整理後推播到班級群組。', 'Summarizes school announcements and pushes them to class groups.')),
    (L('資安宣導週', 'Security Awareness Week'), L('活動', 'Event'), L('舉辦釣魚郵件辨識挑戰與密碼安全講座。', 'Ran a phishing-spotting challenge and a password safety talk.')),
    (L('團隊識別設計', 'Team Brand Design'), L('設計', 'Design'), L('重新設計隊徽、配色與文宣模板。', 'Redesigned the team emblem, colors and print templates.')),
    (L('成績查詢小工具', 'Grade Lookup Tool'), L('應用程式', 'App'), L('練習用專題：以虛構資料示範查詢介面與權限控管。', 'A practice project demonstrating a lookup UI and access control with mock data.')),
]

photo_specs = [
    (L('活動', 'Events'), L('期末成果發表', 'End-of-term showcase'), 800, 560, '#0b2a55', '#3b82f6', 3),
    (L('維修', 'Repair'), L('電腦教室巡檢', 'Computer lab inspection'), 640, 800, '#14396e', '#60a5fa', 1),
    (L('活動', 'Events'), L('資安宣導週闖關', 'Security week challenge'), 800, 520, '#312e81', '#818cf8', 2),
    (L('日常', 'Daily'), L('社課教學', 'Club lesson'), 700, 700, '#0f3a72', '#38bdf8', 1),
    (L('日常', 'Daily'), L('午休討論', 'Lunch-break meeting'), 800, 600, '#172554', '#6366f1', 2),
    (L('維修', 'Repair'), L('投影機更換燈泡', 'Projector lamp replacement'), 600, 780, '#1e40af', '#93c5fd', 0),
    (L('活動', 'Events'), L('校慶攤位', 'School fair booth'), 820, 540, '#0e7490', '#67e8f9', 0),
    (L('日常', 'Daily'), L('新成員培訓', 'New member training'), 760, 560, '#1d4e9e', '#a5b4fc', 3),
    (L('活動', 'Events'), L('寒假工作營', 'Winter camp'), 680, 680, '#155e75', '#7dd3fc', 2),
]

news = [
    ('2026-10-12', L('期中電腦巡檢完成', 'Mid-term PC inspection completed'), L('本學期共巡檢 118 台教室電腦，修復 9 台故障設備。', 'We inspected 118 classroom PCs this term and repaired 9 faulty units.')),
    ('2026-09-28', L('社團報名系統上線', 'Club sign-up system launched'), L('新系統首週即有超過 900 位同學完成線上選填。', 'Over 900 students submitted their choices online in the first week.')),
    ('2026-09-10', L('招募新成員', 'Recruiting new members'), L('歡迎對程式、維修、設計有興趣的同學加入，詳情請洽社辦。', 'Students interested in coding, repair or design are welcome to join. Visit our club room for details.')),
    ('2026-07-15', L('暑期網路設備更新', 'Summer network upgrade'), L('協助更新三棟教學大樓的無線基地台設定。', 'Helped reconfigure Wi-Fi access points in three teaching buildings.')),
    ('2026-05-20', L('資安宣導週圓滿落幕', 'Security week wrapped up'), L('共 320 人次參與釣魚郵件辨識挑戰。', '320 participants took part in the phishing-spotting challenge.')),
    ('2026-03-02', L('團隊網站改版', 'Team website redesign'), L('新版網站支援深色模式與中英雙語。', 'The new site supports dark mode and both Chinese and English.')),
]

timeline = [
    ('2021', L('團隊成立', 'Team founded'), L('五位同學發起，協助處理教室設備問題。', 'Started by five students helping with classroom equipment.')),
    ('2022', L('第一個校用系統', 'First school system'), L('完成設備借用平台，開始承接處室需求。', 'Built the equipment loan platform and began taking requests from school offices.')),
    ('2023', L('成立網路組', 'Network unit formed'), L('開始協助管理校園無線網路。', 'Began helping manage the campus wireless network.')),
    ('2024', L('資安推廣', 'Security outreach'), L('舉辦第一屆資安宣導週。', 'Held the first Security Awareness Week.')),
    ('2026', L('網站改版', 'Website redesign'), L('推出雙語團隊網站與線上報名系統。', 'Launched the bilingual team site and the online sign-up system.')),
]

contact = [
    ('mail', L('電子郵件', 'Email'), L('team@example.com', 'team@example.com')),
    ('pin', L('社辦位置', 'Club room'), L('範例高中 資訊大樓 3 樓（虛構地址）', '3F, IT Building, Example High School (fictional)')),
    ('social', L('社群', 'Social'), L('@example_team', '@example_team')),
]

values = [
    ('target', L('解決真實問題', 'Solve real problems'), L('從校園需求出發，做出真正有人用的工具。', 'We start from real campus needs and build tools people actually use.')),
    ('users', L('互相學習', 'Learn together'), L('學長姐帶學弟妹，每個人都能教也能學。', 'Seniors mentor juniors; everyone teaches and learns.')),
    ('growth', L('持續進步', 'Keep improving'), L('每個專案結束都檢討，下一次做得更好。', 'We review every project so the next one is better.')),
]

data = {
    'team': {
        'title': L('山城資訊工作隊', 'Cyber Service Team'),
        'description': L(
            '（測試資料）這是一個虛構的學生資訊服務團隊介紹。我們協助校園處理電腦維修、網路管理與系統開發，並舉辦資安推廣活動。\n\n以下所有成員、作品與消息皆為虛構的示範內容。',
            '(Test data) This is a fictional introduction of a student IT service team. We help the campus with PC repair, network management and system development, and run security outreach events.\n\nAll members, projects and news below are fictional sample content.'),
        'image': photo(1200, 420, '#0b2a55', '#3b82f6', 3),
    },
    'home': {'tagline': L('用資訊技術，讓校園更有效率。（測試資料）', 'Using technology to make campus work better. (test data)')},
    'members': [{
        'name': L(zh, en), 'role': L(rz, re), 'responsibilities': L(dz, de),
        'email': en.lower().replace(' ', '.') + '@example.com', 'image': avatar(color, letter)
    } for zh, en, rz, re, dz, de, letter, color in members],
    'projects': [{'title': t, 'tag': g, 'text': x} for t, g, x in projects],
    'photos': [{'album': a, 'caption': c, 'image': photo(w, h, c1, c2, k)} for a, c, w, h, c1, c2, k in photo_specs],
    'news': [{'date': d, 'title': t, 'text': x} for d, t, x in news],
    'timeline': [{'year': y, 'title': t, 'text': x} for y, t, x in timeline],
    'contact': [{'icon': i, 'title': t, 'text': x} for i, t, x in contact],
    'values': [{'icon': i, 'title': t, 'text': x} for i, t, x in values],
}

OUT.write_text(
    '// 此檔由 tools/gen_test_data.py 產生，請勿手動修改。\n'
    '// 網站的虛構測試資料：人名、Email、地址、事件皆為虛構；圖片為程式繪製的抽象圖案。\n'
    '// 不需要測試資料時，可以直接刪除這個檔案（以及 Apps Script 專案中的同名檔案）。\n\n'
    'var TEST_DATA_ = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n',
    encoding='utf-8')
print('已產生 %s（%.0f KB）' % (OUT.relative_to(ROOT), OUT.stat().st_size / 1024))
