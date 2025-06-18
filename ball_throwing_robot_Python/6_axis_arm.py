import pygame
from pygame.locals import *
import pigpio
import time

# Pygameを初期化
pygame.init()

# pigpioの初期化
pi = pigpio.pi()
if not pi.connected:
    print("pigpioデーモンが実行されていません。pigpiodを開始してください。")
    exit()

# ジョイスティックが接続されているか確認
if pygame.joystick.get_count() == 0:
    print("ジョイスティックが接続されていません")
    exit()

# 最初のジョイスティックを取得
joystick = pygame.joystick.Joystick(0)
joystick.init()

# サーボの制御に使うGPIOピン
servo_pin_yubi = 2     # MG996R 指
servo_pin_hineri = 3   # MG996R ひねり
servo_pin_tekubi = 4   # MG996R 手首
servo_pin_hijiFront = 10   # MG996R 肘フロント

servo_pin_hijiRear = 17    # 8125MG 肘リア
servo_pin_kata = 27    # 8125MG 肩
servo_pin_karada = 22  # 8125MG 体

# PWMの設定 (各ピンでPWMを設定)
pi.set_mode(servo_pin_yubi, pigpio.OUTPUT)
pi.set_mode(servo_pin_hineri, pigpio.OUTPUT)
pi.set_mode(servo_pin_tekubi, pigpio.OUTPUT)
pi.set_mode(servo_pin_hijiFront, pigpio.OUTPUT)

pi.set_mode(servo_pin_hijiRear, pigpio.OUTPUT)
pi.set_mode(servo_pin_kata, pigpio.OUTPUT)
pi.set_mode(servo_pin_karada, pigpio.OUTPUT)

# PWM開始（すべて0度からスタート）
pi.set_servo_pulsewidth(servo_pin_yubi, 0)
pi.set_servo_pulsewidth(servo_pin_hineri, 0)
pi.set_servo_pulsewidth(servo_pin_tekubi, 0)
pi.set_servo_pulsewidth(servo_pin_hijiFront, 0)

pi.set_servo_pulsewidth(servo_pin_hijiRear, 0)
pi.set_servo_pulsewidth(servo_pin_kata, 0)
pi.set_servo_pulsewidth(servo_pin_karada, 0)

# MG996R用の角度設定関数
def set_mg996r_angle(angle, servo_pin):
    # 0° → 500μs, 180° → 2500μs に変換
    pulsewidth = (angle / 180) * 2000 + 500  # 0° → 500μs, 180° → 2500μs
    
    # 500μs〜2500μsの範囲で制限
    pulsewidth = max(500, min(pulsewidth, 2500))
    pi.set_servo_pulsewidth(servo_pin, pulsewidth)

# 8125MG用の角度設定関数
def set_8125mg_angle(angle, servo_pin):
    # 0° → 1000μs, 180° → 2000μs に変換
    pulsewidth = (angle / 180) * 1000 + 1000  # 0° → 1000μs, 180° → 2000μs
    
    # 1000μs〜2000μsの範囲で制限
    pulsewidth = max(1000, min(pulsewidth, 2000))
    pi.set_servo_pulsewidth(servo_pin, pulsewidth)

# メインループ
try:
    yubi_deg = 0
    hineri_deg = 0
    tekubi_deg = 0
    hijiFront_deg = 0
    hijiRear_deg = 0
    kata_deg = 0
    karada_deg = 0
    waitTime = 0.05
    
    kata_up_held_flg = False  # ボタンが押されているかどうかを確認するフラグ
    kata_down_held_flg = False  # ボタンが押されているかどうかを確認するフラグ
    kata_deg_cnt = 0
    
    
    hidari_held_flg = False  # ボタンが押されているかどうかを確認するフラグ
    migi_held_flg = False  # ボタンが押されているかどうかを確認するフラグ
    karada_deg_cnt = 0
    
    
    front_move_flg = False  # ボタンが押されているかどうかを確認するフラグ
    front_move_deg_cnt = 0
    rear_move_flg = False  # ボタンが押されているかどうかを確認するフラグ
    rear_move_deg_cnt = 0
    
    counter_clock_hineri_flg = False# ボタンが押されているかどうかを確認するフラグ
    counter_clock_hineri_deg_cnt = 0
    clock_hineri_flg = False# ボタンが押されているかどうかを確認するフラグ
    clock_hineri_deg_cnt = 0
    
    while True:
        for event in pygame.event.get():
            # 終了イベント
            if event.type == QUIT:
                pygame.quit()
                exit()

            # ボタンが押されたとき
            if event.type == JOYBUTTONDOWN:
                print(f"ボタン {event.button} が押されました")
                # 〇ボタン（通常はボタン0）を押したときに指の動きを制御
                if event.button == 13:  # 〇ボタンが押されたら
                    print("指を102度に設定")
                    yubi_deg = 115
                    set_mg996r_angle(yubi_deg, servo_pin_yubi)
                    
                if event.button == 14:  # ×ボタンが押されたら
                    print("指を65度に設定")
                    yubi_deg = 75
                    set_mg996r_angle(yubi_deg, servo_pin_yubi)
                    
                if event.button == 12:  # △ボタンが押されたら
                    kata_up_held_flg = True
                    print("△ボタンが押された")
                    
                if event.button == 15:  # □ボタンが押されたら
                    kata_down_held_flg = True
                    print("□ボタンが押された")
                    
                if event.button == 7:  # ←ボタンが押されたら
                    hidari_held_flg = True
                    print("←ボタンが押された")
                    
                if event.button == 5:  # →ボタンが押されたら
                    migi_held_flg = True
                    print("→ボタンが押された")
                    
                if event.button == 4:  # ↑ボタンが押されたら
                    front_move_flg = True
                    print("↑ボタンが押された")
                    
                if event.button == 6:  # ↓ボタンが押されたら
                    rear_move_flg = True
                    print("↓ボタンが押された")
                    
                if event.button == 8:  # L2ボタンが押されたら
                    clock_hineri_flg = True
                    print("L2ボタンが押された")
                    
                if event.button == 9:  # R2ボタンが押されたら
                    counter_clock_hineri_flg = True
                    print("R2ボタンが押された")
                    
                
                """if event.button == 3:  # STARTボタンが押されたら、初期位置(アーム直立姿勢 & 体0°)へ
                    print("STARTボタンが押された(初期位置へアーム移動)")
                    karada_deg = 0
                    print("体を", karada_deg, "度に設定")
                    kata_deg = 90
                    print("肩を", kata_deg, "度に設定")
                    hijiRear_deg = 150
                    print("肘リアを", hijiRear_deg, "度に設定")
                    hijiFront_deg = 60
                    print("肘フロントを", hijiFront_deg, "度に設定")
                    tekubi_deg = 30
                    print("手首を", tekubi_deg, "度に設定")
                    
                    set_8125mg_angle(karada_deg, servo_pin_karada)
                    set_8125mg_angle(kata_deg, servo_pin_kata)
                    set_8125mg_angle(hijiRear_deg, servo_pin_hijiRear)
                    set_mg996r_angle(hijiFront_deg, servo_pin_hijiFront)
                    set_mg996r_angle(tekubi_deg, servo_pin_tekubi)"""
                    
                if event.button == 3:  # STARTボタンが押されたら、旋回姿勢へ
                    print("STARTボタンが押された旋回姿勢へ)")
                    """if (karada_deg<90):
                        while karada_deg<90:
                            if(karada_deg<85):
                                karada_deg = karada_deg+5
                                set_8125mg_angle(kata_deg, servo_pin_karada)
                            elif(karada_deg>=85):
                                karada_deg = 90
                                set_8125mg_angle(kata_deg, servo_pin_karada)
                    elif(karada_deg>90):
                        while karada_deg>90:
                            if(karada_deg>95):
                                time.sleep(waitTime)
                                karada_deg = karada_deg-5
                                set_8125mg_angle(kata_deg, servo_pin_karada)
                            elif(karada_deg<=95):
                                time.sleep(waitTime)
                                karada_deg = 90
                                set_8125mg_angle(kata_deg, servo_pin_karada)
                                
                    print("体を", karada_deg, "度に設定")
                    """
                    if (tekubi_deg<120):
                        while tekubi_deg<120:
                            if(tekubi_deg<115):
                                tekubi_deg = tekubi_deg+5
                                set_mg996r_angle(tekubi_deg, servo_pin_tekubi)
                            elif(tekubi_deg>=115):
                                tekubi_deg = 120
                                set_mg996r_angle(tekubi_deg, servo_pin_tekubi)
                    elif(tekubi_deg>120):
                        while tekubi_deg>120:
                            if(tekubi_deg>125):
                                time.sleep(waitTime)
                                tekubi_deg = tekubi_deg-5
                                set_mg996r_angle(tekubi_deg, servo_pin_tekubi)
                            elif(tekubi_deg<=125):
                                time.sleep(waitTime)
                                tekubi_deg = 120
                                set_mg996r_angle(tekubi_deg, servo_pin_tekubi)
                    
                    print("手首を", tekubi_deg, "度に設定")
                    
                    if (hijiFront_deg<120):
                        while hijiFront_deg<120:
                            if(hijiFront_deg<115):
                                time.sleep(waitTime)
                                hijiFront_deg = hijiFront_deg+5
                                set_mg996r_angle(hijiFront_deg, servo_pin_hijiFront)
                            elif(hijiFront_deg>=115):
                                time.sleep(waitTime)
                                hijiFront_deg = 120
                                set_mg996r_angle(hijiFront_deg, servo_pin_hijiFront)
                    elif(hijiFront_deg>120):
                        while hijiFront_deg>120:
                            if(hijiFront_deg>125):
                                time.sleep(waitTime)
                                hijiFront_deg = hijiFront_deg-5
                                set_mg996r_angle(hijiFront_deg, servo_pin_hijiFront)
                            elif(hijiFront_deg<=125):
                                time.sleep(waitTime)
                                hijiFront_deg = 120
                                set_mg996r_angle(hijiFront_deg, servo_pin_hijiFront)
                    
                    print("肘フロントを", hijiFront_deg, "度に設定")
                    
                    if (hijiRear_deg<180):
                        while hijiRear_deg<180:
                            if(hijiRear_deg<175):
                                hijiRear_deg = hijiRear_deg+5
                                set_8125mg_angle(hijiRear_deg, servo_pin_hijiRear)
                            elif(hijiRear_deg>=175):
                                hijiRear_deg = 180
                                set_8125mg_angle(hijiRear_deg, servo_pin_hijiRear)
                    elif(hijiRear_deg>180):
                        while hijiRear_deg>180:
                            if(hijiRear_deg>185):
                                time.sleep(waitTime)
                                hijiRear_deg = hijiRear_deg-5
                                set_8125mg_angle(hijiRear_deg, servo_pin_hijiRear)
                            elif(hijiRear_deg<=185):
                                time.sleep(waitTime)
                                hijiRear_deg = 180
                                set_8125mg_angle(hijiRear_deg, servo_pin_hijiRear)
                                
                    print("肘リアを", hijiRear_deg, "度に設定")
                    
                    if (kata_deg<60):
                        while kata_deg<60:
                            if(kata_deg<55):
                                kata_deg = kata_deg+5
                                set_8125mg_angle(kata_deg, servo_pin_kata)
                            elif(kata_deg>=55):
                                kata_deg = 60
                                set_8125mg_angle(kata_deg, servo_pin_kata)
                    elif(kata_deg>60):
                        while kata_deg>60:
                            if(kata_deg>65):
                                time.sleep(waitTime)
                                kata_deg = kata_deg-5
                                set_8125mg_angle(kata_deg, servo_pin_kata)
                            elif(kata_deg<=65):
                                time.sleep(waitTime)
                                kata_deg = 60
                                set_8125mg_angle(kata_deg, servo_pin_kata)
                                
                    print("肩を", kata_deg, "度に設定")
                    
                
                if event.button == 0:  # SELECTボタンが押されたら、走行姿勢へ
                    print("SELECTボタンが押された走行姿勢へ)")
                    print("SELECTボタンが押された")
                    kata_deg = 100
                    print("肩を", kata_deg, "度に設定")
                    hijiRear_deg = 180
                    print("肘リアを", hijiRear_deg, "度に設定")
                    if (hijiFront_deg<180):
                        while hijiFront_deg<180:
                            if(hijiFront_deg<175):
                                time.sleep(waitTime)
                                hijiFront_deg = hijiFront_deg+5
                                set_mg996r_angle(hijiFront_deg, servo_pin_hijiFront)
                            elif(hijiFront_deg>=175):
                                time.sleep(waitTime)
                                hijiFront_deg = 180
                                set_mg996r_angle(hijiFront_deg, servo_pin_hijiFront)
                    elif(hijiFront_deg>180):
                        while hijiFront_deg>180:
                            if(hijiFront_deg>185):
                                time.sleep(waitTime)
                                hijiFront_deg = hijiFront_deg-5
                                set_mg996r_angle(hijiFront_deg, servo_pin_hijiFront)
                            elif(hijiFront_deg<=185):
                                time.sleep(waitTime)
                                hijiFront_deg = 180
                                set_mg996r_angle(hijiFront_deg, servo_pin_hijiFront)
                                
                    print("肘フロントを", hijiFront_deg, "度に設定")
                    tekubi_deg = 135
                    print("手首を", tekubi_deg, "度に設定")
                    set_8125mg_angle(kata_deg, servo_pin_kata)
                    set_8125mg_angle(hijiRear_deg, servo_pin_hijiRear)
                    set_mg996r_angle(tekubi_deg, servo_pin_tekubi)
                    
                    if (karada_deg<135):
                        while karada_deg<135:
                            if(karada_deg<130):
                                karada_deg = karada_deg+5
                                set_8125mg_angle(kata_deg, servo_pin_karada)
                            elif(karada_deg>=130):
                                karada_deg = 135
                                set_8125mg_angle(kata_deg, servo_pin_karada)
                    elif(karada_deg>135):
                        while karada_deg>135:
                            if(karada_deg>140):
                                time.sleep(waitTime)
                                karada_deg = karada_deg-5
                                set_8125mg_angle(kata_deg, servo_pin_karada)
                            elif(karada_deg<=140):
                                time.sleep(waitTime)
                                karada_deg = 135
                                set_8125mg_angle(kata_deg, servo_pin_karada)
                                
                    print("体を", karada_deg, "度に設定")
                    
                    
                """if event.button == 11:  # R1ボタンが押されたら、アーム直立姿勢へ
                    print("R1ボタンが押された")
                    kata_deg = 90
                    print("肩を", kata_deg, "度に設定")
                    hijiRear_deg = 150
                    print("肘リアを", hijiRear_deg, "度に設定")
                    hijiFront_deg = 60
                    print("肘フロントを", hijiFront_deg, "度に設定")
                    tekubi_deg = 80
                    print("手首を", tekubi_deg, "度に設定")
                    set_8125mg_angle(kata_deg, servo_pin_kata)
                    set_8125mg_angle(hijiRear_deg, servo_pin_hijiRear)
                    set_mg996r_angle(hijiFront_deg, servo_pin_hijiFront)
                    set_mg996r_angle(tekubi_deg, servo_pin_tekubi)"""
                    
                    
                    
            if event.type == JOYBUTTONUP:
                if event.button == 12:  # △ボタンが離された
                    kata_up_held_flg = False
                    print("△ボタンが離された")
                    
                if event.button == 15:  # □ボタンが離された
                    kata_down_held_flg = False
                    print("□ボタンが離された")
                    
                if event.button == 7:  # ←ボタンが離された
                    hidari_held_flg = False
                    print("←ボタンが離された")
                    
                if event.button == 5:  # →ボタンが離された
                    migi_held_flg = False
                    print("→ボタンが離された")
                    
                if event.button == 4:  # ↑ボタンが離された
                    front_move_flg = False
                    print("↑ボタンが離された")
                    
                if event.button == 6:  # ↓ボタンが離された
                    rear_move_flg = False
                    print("↓ボタンが離された")
                    
                if event.button == 8:  # L2ボタンが離された
                    clock_hineri_flg = False
                    print("L2ボタンが離された")
                    
                if event.button == 9:  # R2ボタンが離された
                    counter_clock_hineri_flg = False
                    print("R2ボタンが離された")

            if kata_up_held_flg:
                    # 肩を動かす処理（肩を上げる方向に角度を変更）
                    kata_deg_cnt = kata_deg_cnt + 1
                    if(kata_deg_cnt >= 3):
                        print("肩を", kata_deg, "度に設定")
                        set_8125mg_angle(kata_deg, servo_pin_kata)
                        kata_deg_cnt = 0
                        kata_deg = kata_deg + 3
                    if(kata_deg >= 90):
                        kata_deg = 90
                    
            if kata_down_held_flg:
                    # 肩を動かす処理（肩を下げる方向に角度を変更）
                    kata_deg_cnt = kata_deg_cnt + 1
                    if(kata_deg_cnt >= 1):
                        print("肩を", kata_deg, "度に設定")
                        set_8125mg_angle(kata_deg, servo_pin_kata)
                        time.sleep(0.01)
                        kata_deg_cnt = 0
                        kata_deg = kata_deg - 1
                    if(kata_deg <= 0):
                        kata_deg = 0
                        
            if hidari_held_flg:
                    # 体を動かす処理（体を左方向に角度を変更）
                    karada_deg_cnt = karada_deg_cnt + 1
                    if(karada_deg_cnt >= 2):
                        print("体を", karada_deg, "度に設定")
                        set_8125mg_angle(karada_deg, servo_pin_karada)
                        karada_deg_cnt = 0
                        karada_deg = karada_deg + 3
                    if(karada_deg >= 180):
                        karada_deg = 180
                        
            if migi_held_flg:
                    # 体を動かす処理（体を右方向に角度を変更）
                    karada_deg_cnt = karada_deg_cnt + 1
                    if(karada_deg_cnt >= 2):
                        print("体を", karada_deg, "度に設定")
                        set_8125mg_angle(karada_deg, servo_pin_karada)
                        karada_deg_cnt = 0
                        karada_deg = karada_deg - 3
                    if(karada_deg <= 0):
                        karada_deg = 0
                        
            if counter_clock_hineri_flg:
                    # ひねりを反時計回りに動かす処理
                    counter_clock_hineri_deg_cnt = counter_clock_hineri_deg_cnt + 1
                    if(counter_clock_hineri_deg_cnt >= 2):
                        print("ひねりを", hineri_deg, "度に設定")
                        set_mg996r_angle(hineri_deg, servo_pin_hineri)
                        counter_clock_hineri_deg_cnt = 0
                        hineri_deg = hineri_deg + 3
                    if(hineri_deg >= 180):
                        hineri_deg = 180
                        
            if clock_hineri_flg:
                    # ひねりを時計回りに動かす処理
                    clock_hineri_deg_cnt = clock_hineri_deg_cnt + 1
                    if(clock_hineri_deg_cnt >= 2):
                        print("ひねりを", hineri_deg, "度に設定")
                        set_mg996r_angle(hineri_deg, servo_pin_hineri)
                        clock_hineri_deg_cnt = 0
                        hineri_deg = hineri_deg - 3
                    if(hineri_deg <= 0):
                        hineri_deg = 0
                        
            if front_move_flg:
                    # アームを前方へ動かす処理（肘リアを上げる方向、肩を下げる方向に、角度を変更）
                    front_move_deg_cnt = front_move_deg_cnt + 1
                    if(front_move_deg_cnt >= 3):
                        front_move_deg_cnt = 0
                        if(hijiFront_deg!=90):
                            if(hijiFront_deg<90):
                                hijiFront_deg=hijiFront_deg+5
                            elif(hijiFront_deg>90):
                                hijiFront_deg=hijiFront_deg-5
                            set_8125mg_angle(hijiFront_deg, servo_pin_hijiFront)
                        if(hijiRear_deg!=150):
                            if(hijiRear_deg<150):
                                hijiRear_deg=hijiRear_deg+5
                            elif(hijiRear_deg>150):
                                hijiRear_deg=hijiRear_deg-5
                            set_8125mg_angle(hijiRear_deg, servo_pin_hijiRear)
                        if(kata_deg!=10):
                            if(kata_deg<10):
                                kata_deg=kata_deg+3
                            elif(kata_deg>10):
                                kata_deg=kata_deg-3
                            set_8125mg_angle(kata_deg, servo_pin_kata)
                            
            if rear_move_flg:
                    # アームを後方へ動かす処理（肘リアを下げる方向、肩を上る方向に、角度を変更）
                    rear_move_deg_cnt = rear_move_deg_cnt + 1
                    if(rear_move_deg_cnt >= 3):
                        rear_move_deg_cnt = 0
                        if(hijiFront_deg!=60):
                            if(hijiFront_deg<60):
                                hijiFront_deg=hijiFront_deg+5
                            elif(hijiFront_deg>60):
                                hijiFront_deg=hijiFront_deg-5
                            set_8125mg_angle(hijiFront_deg, servo_pin_hijiFront)
                        if(hijiRear_deg!=30):
                            if(hijiRear_deg<30):
                                hijiRear_deg=hijiRear_deg+5
                            elif(hijiRear_deg>30):
                                hijiRear_deg=hijiRear_deg-5
                            set_8125mg_angle(hijiRear_deg, servo_pin_hijiRear)
                        if(kata_deg!=90):
                            if(kata_deg<90):
                                kata_deg=kata_deg+3
                            elif(kata_deg>90):
                                kata_deg=kata_deg-3
                            set_8125mg_angle(kata_deg, servo_pin_kata)

except KeyboardInterrupt:
    print("プログラムを終了します。")
    pygame.quit()

finally:
    # PWM停止
    pi.set_servo_pulsewidth(servo_pin_yubi, 0)
    pi.set_servo_pulsewidth(servo_pin_hineri, 0)
    pi.set_servo_pulsewidth(servo_pin_tekubi, 0)
    pi.set_servo_pulsewidth(servo_pin_hijiFront, 0)

    pi.set_servo_pulsewidth(servo_pin_hijiRear, 0)
    pi.set_servo_pulsewidth(servo_pin_kata, 0)
    pi.set_servo_pulsewidth(servo_pin_karada, 0)

    pi.stop()  # pigpioのクリーンアップ
