import sqlite3

def init_db():
    conn = sqlite3.connect('tahoiya.db')
    cursor = conn.cursor()
    
    # 修正版：word TEXT NOT EXISTS の誤りを word TEXT に直しました
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT,
            correct_meaning TEXT,
            fake_1 TEXT,
            fake_2 TEXT,
            fake_3 TEXT
        )
    ''')
    
    # テスト用データ（実在する正しい意味）
    sample_data = [
        (
            "たほいや", 
            "猪などを追うために、追い手が発する声。また、それを行う人やその小屋。",
            "江戸時代に流行した、手ぬぐいを使った座敷遊びの一種。",
            "囲炉裏（いろり）の灰を均したり、炭を動かしたりするための鉄製の道具。",
            "九州地方の古い方言で、「お調子者」や「騒がしい人」を指す言葉。"
        ),
        (
            "ぐにゃにゃ", 
            "文楽や歌舞伎で、締まりのない、だだくさな人間をあざけって言う語。",
            "猫が怒ったときに発する特有の鳴き声を模した、江戸時代の擬音語。",
            "こんにゃくや寒天などの、弾力があって柔らかい食べ物を指す隠語。",
            "ポルトガルから伝来した、初期の織物（レースの一種）の日本での呼び名。"
        ),
        (
            "すいかずら",
            "冬を耐え忍ぶという意味の「忍冬」とも書き、甘い蜜がある実在する植物。",
            "室町時代に飲まれていた、砂糖と酢を調合した清涼飲料水のこと。",
            "すれ違いざまに他人の悪口をボソッと言う、質の悪い嫌がらせ行為。",
            "職人が使う、木材の表面を限界まで薄く削り出すための特殊な鉋（かんな）。"
        )
    ]
    
    cursor.execute("DELETE FROM questions")
    
    cursor.executemany('''
        INSERT INTO questions (word, correct_meaning, fake_1, fake_2, fake_3)
        VALUES (?, ?, ?, ?, ?)
    ''', sample_data)
    
    conn.commit()
    conn.close()
    print("データベースにお題データをストックしました！")

if __name__ == "__main__":
    init_db()