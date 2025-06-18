import RPi.GPIO as GPIO
import time
import random

# ポート番号の定義
SW1 = 25
SW2 = 8
SW3 = 7
SW4 = 12
SPM_A = 2
SPM_B = 4
SPM_C = 3
SPM_D = 5

# GPIOの初期化
GPIO.setmode(GPIO.BCM) # BCMモードに設定（GPIOのポート番号で指定する） BOARDモードだとピン番号（GND等含む）で指定する
GPIO.setup(SW1, GPIO.IN) # 指定ポートをinに設定
GPIO.setup(SW2, GPIO.IN) # 指定ポートをinに設定
GPIO.setup(SW3, GPIO.IN) # 指定ポートをinに設定
GPIO.setup(SW4, GPIO.IN) # 指定ポートをinに設定
GPIO.setup(SPM_A, GPIO.OUT) # 指定ポートをoutに設定
GPIO.setup(SPM_B, GPIO.OUT) # 指定ポートをoutに設定
GPIO.setup(SPM_C, GPIO.OUT) # 指定ポートをoutに設定
GPIO.setup(SPM_D, GPIO.OUT) # 指定ポートをoutに設定

# ステッピングモータ定数
TPHS = 0.002 # 1相あたりの時間[s]
#TPHS = 0.05 # 1相あたりの時間[s] #テスト用
DPP = 0.9 # 1-2相励磁における１相あたりの回転角度[deg/phase]
NPHS = 8 # 1-2相励磁における相数
koma_size=19 #1コマ分の励磁回数
last_koma_size=20 #最後の1コマの励磁回数（調整用に20とする)

# 最後に通電したステッピングモータの相(1:A, 2:A+B, 3:B, 4:B+C, 5:C, 6:C+D, 7:D, 8:D+A)
phase = 1

seiten_flg=0

rotate_OnePointNineDeg_cnt=0
suberi=0
suberi_margin=3
flag_suberi1=0
SW2_flg=0
SW3_flg=0
SW4_flg=0
stop_flg=0
ran=0

#設定1に初期化
yakukakuritsu=[160,46,100,60,1720,11108,8980,64,64,9,9,4,4,6,2,43200]
yakukakuritsu[0]=160						#単独ビッグ
yakukakuritsu[1]=yakukakuritsu[0]+46		#チェリー重複ビッグ
yakukakuritsu[2]=yakukakuritsu[1]+100		#単独レギュラー
yakukakuritsu[3]=yakukakuritsu[2]+60		#チェリー重複レギュラー
yakukakuritsu[4]=yakukakuritsu[3]+1720		#非重複チェリー
yakukakuritsu[5]=yakukakuritsu[4]+11108		#ブドウ
yakukakuritsu[6]=yakukakuritsu[5]+8980		#リプレイ
yakukakuritsu[7]=yakukakuritsu[6]+64		#ベル
yakukakuritsu[8]=yakukakuritsu[7]+64		#ピエロ
yakukakuritsu[9]=yakukakuritsu[8]+9			#レアチェリーA
yakukakuritsu[10]=yakukakuritsu[9]+9		#レアチェリーB
yakukakuritsu[11]=yakukakuritsu[10]+4		#レア役P
yakukakuritsu[12]=yakukakuritsu[11]+4		#レア役AP
yakukakuritsu[13]=yakukakuritsu[12]+6		#レア役BP
yakukakuritsu[14]=yakukakuritsu[13]+2		#レア役ABP
yakukakuritsu[15]=yakukakuritsu[14]+43200	#ハズレ


yaku_flag=111 #抽選結果によるフラグ立て用変数
settei=1 #設定を入れる変数


#割り込みが発生したときに実行する関数
#def switch_callback(channel):
	#global seiten_flg
	#if(channel==SW4):
		#seiten_flg=1
	#elif(channel==SW3):
		#seiten_flg=0

#割り込みの設定（立ち下がりエッジでトリガー）
#GPIO.add_event_detect(SW3,GPIO.RISING,callback=switch_callback,bouncetime=200)
#GPIO.add_event_detect(SW4,GPIO.RISING,callback=switch_callback,bouncetime=200)


# スイッチの状態をチェックする関数
def check_switch():
	ans = 0
	global SW2_flg,SW3_flg,SW4_flg,ran,suberi,settei,rotate_OnePointNineDeg_cnt
	
	if (GPIO.input(SW1) == GPIO.HIGH):
		# チャタリング防止
		time.sleep(0.02)
		if (GPIO.input(SW1) == GPIO.HIGH):
			print("sw1")
			ans = 1
	elif (GPIO.input(SW2) == GPIO.HIGH):
		# チャタリング防止
		time.sleep(0.02)
		if (GPIO.input(SW2) == GPIO.HIGH and SW2_flg==0):
			SW2_flg=1
			print("sw2")
			settei=settei+1
			if(settei>6):
				settei=1
			setteihenko()
			print("設定を",settei,"に変更しました。")
			ans = 2
	elif (GPIO.input(SW3) == GPIO.HIGH):
		# チャタリング防止
		time.sleep(0.02)
		if (GPIO.input(SW3) == GPIO.HIGH and SW3_flg==0):
			SW3_flg=1
			print("sw3")
			print("rotate_OnePointNiceDeg_cnt at stop:",rotate_OnePointNineDeg_cnt)
			flag_suberi1_calc()
			print("flag_suberi1 at stop:",flag_suberi1) #デバッグ用
			if rotate_OnePointNineDeg_cnt>380:
				suberi=rotate_OnePointNineDeg_cnt%20
			else:
				suberi=rotate_OnePointNineDeg_cnt%19
			print("suberi at stop:",suberi)
			ans = 3
	elif (GPIO.input(SW4) == GPIO.HIGH):
		# チャタリング防止
		time.sleep(0.02)
		if (GPIO.input(SW4) == GPIO.HIGH and SW4_flg==0):
			SW4_flg=1
			print("sw4")
			chusen()
			print("yaku_flag:",yaku_flag)
			ans = 4
			
			
	if(GPIO.input(SW2)==GPIO.LOW):
		SW2_flg=0	
	if(GPIO.input(SW3)==GPIO.LOW):
		SW3_flg=0
	if(GPIO.input(SW4)==GPIO.LOW):
		SW4_flg=0
	
			
	# スイッチの状態をリターン
	return ans

# 指定相を通電する関数(1-2相励磁)
def enable_phase(phase):
	# A相の通電
	if ((phase == 1) or (phase == 2) or (phase == 8)):
		GPIO.output(SPM_A, GPIO.HIGH)
	else:
		GPIO.output(SPM_A, GPIO.LOW)

	# B相の通電
	if ((phase == 2) or (phase == 3) or (phase == 4)):
		GPIO.output(SPM_B, GPIO.HIGH)
	else:
		GPIO.output(SPM_B, GPIO.LOW)

	# C相の通電
	if ((phase == 4) or (phase == 5) or (phase == 6)):
		GPIO.output(SPM_C, GPIO.HIGH)
	else:
		GPIO.output(SPM_C, GPIO.LOW)

	# D相の通電
	if ((phase == 6) or (phase == 7) or (phase == 8)):
		GPIO.output(SPM_D, GPIO.HIGH)
	else:
		GPIO.output(SPM_D, GPIO.LOW)

	# 通電時間待機
	time.sleep(TPHS)

# 通電終了関数
def disable_phase():
	GPIO.output(SPM_A, GPIO.LOW)
	GPIO.output(SPM_B, GPIO.LOW)
	GPIO.output(SPM_C, GPIO.LOW)
	GPIO.output(SPM_D, GPIO.LOW)

	# 通電時間待機
	time.sleep(TPHS)


# 指定した角度だけステッピングモータを正回転（もしくは逆回転）させる関数(1-2相励磁)
def rotate_spm(deg):
	# グローバル変数の指定
	global phase
	
	# 相数算出
	phase_num = round(abs(deg/DPP))

	# 算出した相数分だけ現在相から進める
	for i in range(phase_num):
		# 相を１つだけ進める（もしくは戻す）
		if (deg > 0.0):
			phase += 1
		else:
			phase -= 1
			
		# 余りを計算して相のオーバーを吸収する
		phase %= NPHS

		# 現在相を通電する
		enable_phase(phase)



# ステッピングモータを連続的に正回転させる関数(1-2相励磁)
def rotate_spm_continue():
	# グローバル変数の指定
	global phase
	global rotate_OnePointNineDeg_cnt
	global suberi
	global suberi_margin
	global seiten_flg
	global stop_flg
	global flag_suberi1

	# 相を１つだけ進める
	phase += 1
	rotate_OnePointNineDeg_cnt=rotate_OnePointNineDeg_cnt+1
	if rotate_OnePointNineDeg_cnt>=400:
		rotate_OnePointNineDeg_cnt=0
	suberi=suberi-1
	#print("suberi:",suberi) #デバッグ用
	flag_suberi1=flag_suberi1-1
	#print("flag_suberi1:",flag_suberi1) #デバッグ用
	if suberi<=suberi_margin and stop_flg==1 and flag_suberi1<=0:
			seiten_flg=0
	if phase>=NPHS:
		phase=1
	
	#print("rotate_OnePointNineDeg_cnt:",rotate_OnePointNineDeg_cnt) #デバッグ用

	# 現在相を通電する
	enable_phase(phase)
	


def chusen():
		global yaku_flag
		global yakukakuritsu
		global ran
		
		#print("yakukakuritsu[0]:",yakukakuritsu[0]) #テスト用
		#print("yakukakuritsu[5]:",yakukakuritsu[5]) #テスト用
		
		ran=random.randint(1,65536) #1から65536までの乱数生成
		
		if(ran<=yakukakuritsu[0]): #単独ビッグフラグ時の処理を書く
			yaku_flag=0
		elif(ran<=yakukakuritsu[1]): #チェリー重複ビッグフラグ時の処理を書く
			yaku_flag=1
		elif(ran<=yakukakuritsu[2]): #単独レギュラーフラグ時の処理を書く
			yaku_flag=2
		elif(ran<=yakukakuritsu[3]): #チェリー重複レギュラーフラグ時の処理を書く
			yaku_flag=3
		elif(ran<=yakukakuritsu[4]): #非重複チェリーフラグ時の処理を書く
			yaku_flag=4
		elif(ran<=yakukakuritsu[5]): #ブドウフラグ時の処理を書く
			yaku_flag=5
		elif(ran<=yakukakuritsu[6]): #リプレイフラグ時の処理を書く
			yaku_flag=6
		elif(ran<=yakukakuritsu[7]): #ベルフラグ時の処理を書く
			yaku_flag=7
		elif(ran<=yakukakuritsu[8]): #ピエロフラグ時の処理を書く
			yaku_flag=8
		elif(ran<=yakukakuritsu[9]): #レアチェリーAフラグ時の処理を書く
			yaku_flag=9
		elif(ran<=yakukakuritsu[10]): #レアチェリーBフラグ時の処理を書く
			yaku_flag=10
		elif(ran<=yakukakuritsu[11]): #レア役Pフラグ時の処理を書く
			yaku_flag=11
		elif(ran<=yakukakuritsu[12]): #レア役APフラグ時の処理を書く
			yaku_flag=12
		elif(ran<=yakukakuritsu[13]): #レア役BPフラグ時の処理を書く
			yaku_flag=13
		elif(ran<=yakukakuritsu[14]): #レア役ABPフラグ時の処理を書く
			yaku_flag=14
		else:							#ハズレフラグ時の処理を書く
			yaku_flag=15
		
		
		print("乱数:",ran) #デバッグ用
		
		
	
	
def setteihenko():
	global yakukakuritsu
	global settei
	
	match settei:
		case 1:#設定1
		#役確率の設定
			yakukakuritsu[0]=160						#単独ビッグ
			yakukakuritsu[1]=yakukakuritsu[0]+46		#チェリー重複ビッグ
			yakukakuritsu[2]=yakukakuritsu[1]+100		#単独レギュラー
			yakukakuritsu[3]=yakukakuritsu[2]+60		#チェリー重複レギュラー
			yakukakuritsu[4]=yakukakuritsu[3]+1720		#非重複チェリー
			yakukakuritsu[5]=yakukakuritsu[4]+11108	#ブドウ
			yakukakuritsu[6]=yakukakuritsu[5]+8980		#リプレイ
			yakukakuritsu[7]=yakukakuritsu[6]+64		#ベル
			yakukakuritsu[8]=yakukakuritsu[7]+64		#ピエロ
			yakukakuritsu[9]=yakukakuritsu[8]+9		#レアチェリーA
			yakukakuritsu[10]=yakukakuritsu[9]+9		#レアチェリーB
			yakukakuritsu[11]=yakukakuritsu[10]+4		#レア役P
			yakukakuritsu[12]=yakukakuritsu[11]+4		#レア役AP
			yakukakuritsu[13]=yakukakuritsu[12]+6		#レア役BP
			yakukakuritsu[14]=yakukakuritsu[13]+2		#レア役ABP
			yakukakuritsu[15]=yakukakuritsu[14]+43200  #ハズレ
		
		case 2:#設定2
			#役確率の設定
			yakukakuritsu[0]=161						#単独ビッグ
			yakukakuritsu[1]=yakukakuritsu[0]+47		#チェリー重複ビッグ
			yakukakuritsu[2]=yakukakuritsu[1]+109		#単独レギュラー
			yakukakuritsu[3]=yakukakuritsu[2]+61		#チェリー重複レギュラー
			yakukakuritsu[4]=yakukakuritsu[3]+1720		#非重複チェリー
			yakukakuritsu[5]=yakukakuritsu[4]+11203	#ブドウ
			yakukakuritsu[6]=yakukakuritsu[5]+8980		#リプレイ
			yakukakuritsu[7]=yakukakuritsu[6]+64		#ベル
			yakukakuritsu[8]=yakukakuritsu[7]+64		#ピエロ
			yakukakuritsu[9]=yakukakuritsu[8]+9		#レアチェリーA
			yakukakuritsu[10]=yakukakuritsu[9]+9		#レアチェリーB
			yakukakuritsu[11]=yakukakuritsu[10]+4		#レア役P
			yakukakuritsu[12]=yakukakuritsu[11]+4		#レア役AP
			yakukakuritsu[13]=yakukakuritsu[12]+6		#レア役BP
			yakukakuritsu[14]=yakukakuritsu[13]+2		#レア役ABP
			yakukakuritsu[15]=yakukakuritsu[14]+43093  #ハズレ
		
		case 3:#設定3
			#役確率の設定
			yakukakuritsu[0]=164						#単独ビッグ
			yakukakuritsu[1]=yakukakuritsu[0]+48		#チェリー重複ビッグ
			yakukakuritsu[2]=yakukakuritsu[1]+133		#単独レギュラー
			yakukakuritsu[3]=yakukakuritsu[2]+62		#チェリー重複レギュラー
			yakukakuritsu[4]=yakukakuritsu[3]+1780		#非重複チェリー
			yakukakuritsu[5]=yakukakuritsu[4]+11299	#ブドウ
			yakukakuritsu[6]=yakukakuritsu[5]+8980		#リプレイ
			yakukakuritsu[7]=yakukakuritsu[6]+64		#ベル
			yakukakuritsu[8]=yakukakuritsu[7]+64		#ピエロ
			yakukakuritsu[9]=yakukakuritsu[8]+9		#レアチェリーA
			yakukakuritsu[10]=yakukakuritsu[9]+9		#レアチェリーB
			yakukakuritsu[11]=yakukakuritsu[10]+4		#レア役P
			yakukakuritsu[12]=yakukakuritsu[11]+4		#レア役AP
			yakukakuritsu[13]=yakukakuritsu[12]+6		#レア役BP
			yakukakuritsu[14]=yakukakuritsu[13]+2		#レア役ABP
			yakukakuritsu[15]=yakukakuritsu[14]+42908  #ハズレ
		
		case 4:#設定4
			#役確率の設定
			yakukakuritsu[0]=173						#単独ビッグ
			yakukakuritsu[1]=yakukakuritsu[0]+51		#チェリー重複ビッグ
			yakukakuritsu[2]=yakukakuritsu[1]+161		#単独レギュラー
			yakukakuritsu[3]=yakukakuritsu[2]+65		#チェリー重複レギュラー
			yakukakuritsu[4]=yakukakuritsu[3]+1840		#非重複チェリー
			yakukakuritsu[5]=yakukakuritsu[4]+11338	#ブドウ
			yakukakuritsu[6]=yakukakuritsu[5]+8980		#リプレイ
			yakukakuritsu[7]=yakukakuritsu[6]+64		#ベル
			yakukakuritsu[8]=yakukakuritsu[7]+64		#ピエロ
			yakukakuritsu[9]=yakukakuritsu[8]+9		#レアチェリーA
			yakukakuritsu[10]=yakukakuritsu[9]+9		#レアチェリーB
			yakukakuritsu[11]=yakukakuritsu[10]+4		#レア役P
			yakukakuritsu[12]=yakukakuritsu[11]+4		#レア役AP
			yakukakuritsu[13]=yakukakuritsu[12]+6		#レア役BP
			yakukakuritsu[14]=yakukakuritsu[13]+2		#レア役ABP
			yakukakuritsu[15]=yakukakuritsu[14]+42766  #ハズレ
		
		case 5:#設定5
			#役確率の設定
			yakukakuritsu[0]=185						#単独ビッグ
			yakukakuritsu[1]=yakukakuritsu[0]+54		#チェリー重複ビッグ
			yakukakuritsu[2]=yakukakuritsu[1]+168		#単独レギュラー
			yakukakuritsu[3]=yakukakuritsu[2]+76		#チェリー重複レギュラー
			yakukakuritsu[4]=yakukakuritsu[3]+1840		#非重複チェリー
			yakukakuritsu[5]=yakukakuritsu[4]+11378	#ブドウ
			yakukakuritsu[6]=yakukakuritsu[5]+8980		#リプレイ
			yakukakuritsu[7]=yakukakuritsu[6]+64		#ベル
			yakukakuritsu[8]=yakukakuritsu[7]+64		#ピエロ
			yakukakuritsu[9]=yakukakuritsu[8]+9		#レアチェリーA
			yakukakuritsu[10]=yakukakuritsu[9]+9		#レアチェリーB
			yakukakuritsu[11]=yakukakuritsu[10]+4		#レア役P
			yakukakuritsu[12]=yakukakuritsu[11]+4		#レア役AP
			yakukakuritsu[13]=yakukakuritsu[12]+6		#レア役BP
			yakukakuritsu[14]=yakukakuritsu[13]+2		#レア役ABP
			yakukakuritsu[15]=yakukakuritsu[14]+42693  #ハズレ
		
		case 6:#設定6
			#役確率の設定
			yakukakuritsu[0]=194						#単独ビッグ
			yakukakuritsu[1]=yakukakuritsu[0]+58		#チェリー重複ビッグ
			yakukakuritsu[2]=yakukakuritsu[1]+200		#単独レギュラー
			yakukakuritsu[3]=yakukakuritsu[2]+86		#チェリー重複レギュラー
			yakukakuritsu[4]=yakukakuritsu[3]+1840		#非重複チェリー
			yakukakuritsu[5]=yakukakuritsu[4]+11579	#ブドウ
			yakukakuritsu[6]=yakukakuritsu[5]+8980		#リプレイ
			yakukakuritsu[7]=yakukakuritsu[6]+64		#ベル
			yakukakuritsu[8]=yakukakuritsu[7]+64		#ピエロ
			yakukakuritsu[9]=yakukakuritsu[8]+9		#レアチェリーA
			yakukakuritsu[10]=yakukakuritsu[9]+9		#レアチェリーB
			yakukakuritsu[11]=yakukakuritsu[10]+4		#レア役P
			yakukakuritsu[12]=yakukakuritsu[11]+4		#レア役AP
			yakukakuritsu[13]=yakukakuritsu[12]+6		#レア役BP
			yakukakuritsu[14]=yakukakuritsu[13]+2		#レア役ABP
			yakukakuritsu[15]=yakukakuritsu[14]+42437  #ハズレ
		
		case _:
			print("設定変更エラー")
		


 #役フラグ
  #0単独ビッグ,1チェリー重複ビッグ,2単独レギュラー,3チェリー重複レギュラー
  #4非重複チェリー,5ブドウ,6リプレイ,7ベル,8ピエロ,9レアチェリーA,10レアチェリーB
  #11レア役P,12レア役AP,13レア役BP,14レア役ABP,15ハズレ
  #レアチェリーAが2粒チェリーのこと。

def flag_suberi1_calc():
	global rotate_OnePointNineDeg_cnt
	global koma_size
	global yaku_flag
	global flag_suberi1
	if(rotate_OnePointNineDeg_cnt<=koma_size): #②番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=0 #0コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=0 #0コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=0 #0コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=0 #0コマ滑り
			
			case 7: #ベル
				flag_suberi1=0 #0コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=0 #0コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=0 #0コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 11: #レア役P
				flag_suberi1=0 #0コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=0 #0コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*2): #③番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=0 #0コマ滑り
			
			case 11: #レア役P
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*3): #④番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 11: #レア役P
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*4): #⑤番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=0 #0コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 11: #レア役P
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*5): #⑥番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=0 #0コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=0 #0コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 7: #ベル
				flag_suberi1=0 #0コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 11: #レア役P
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*6): #⑦番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=0 #0コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=0 #0コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 11: #レア役P
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*7): #⑧番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 11: #レア役P
				flag_suberi1=0 #0コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=0 #0コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*8): #⑨番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=0 #0コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=0 #0コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=0 #0コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=0 #0コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=0 #0コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 11: #レア役P
				flag_suberi1=0 #0コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=0 #0コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=0 #0コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=0 #0コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=0 #0コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*9): #⑩番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=0 #0コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=0 #0コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=0 #0コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=0 #0コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=0 #0コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=0 #0コマ滑り
			
			case 11: #レア役P
				flag_suberi1=0 #0コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=0 #0コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=0 #0コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=0 #0コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=0 #0コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*10): #⑪番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=0 #0コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=0 #0コマ滑り
			
			case 7: #ベル
				flag_suberi1=0 #0コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=0 #0コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 11: #レア役P
				flag_suberi1=0 #0コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=0 #0コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*11): #⑫番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 11: #レア役P
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*12): #⑬番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=0 #0コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 11: #レア役P
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=0 #0コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*13): #⑭番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=0 #0コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 11: #レア役P
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*14): #⑮番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=0 #0コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=0 #0コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=0 #0コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=0 #0コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 11: #レア役P
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*15): #⑯番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 11: #レア役P
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*16): #⑰番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=0 #0コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=0 #0コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=0 #0コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=0 #0コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 11: #レア役P
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*17): #⑱番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 11: #レア役P
				flag_suberi1=0 #0コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=0 #0コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=0 #0コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=0 #0コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*18): #⑲番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=0 #0コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=0 #0コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=0 #0コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=0 #0コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=0 #0コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=0 #0コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 11: #レア役P
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=0 #0コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=0 #0コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*19): #⑳番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=0 #0コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=0 #0コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=0 #0コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=0 #0コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=0 #0コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=0 #0コマ滑り
			
			case 11: #レア役P
				flag_suberi1=0 #0コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=0 #0コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=0 #0コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=0 #0コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=0 #0コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt<=koma_size*20): #㉑番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 7: #ベル
				flag_suberi1=0 #0コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 11: #レア役P
				flag_suberi1=0 #0コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
			
		
	
	elif(rotate_OnePointNineDeg_cnt>koma_size*20): #①番を下段押し
		match yaku_flag:
			case 0: #単独ビッグ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 1: #チェリー重複ビッグ
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 2: #単独レギュラー
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 3: #チェリー重複レギュラー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 4: #非重複チェリー
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 5: #ブドウ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 6: #リプレイ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 7: #ベル
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 8: #ピエロ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 9: #レアチェリーA
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case 10: #レアチェリーB
				flag_suberi1=koma_size*2 #2コマ滑り
			
			case 11: #レア役P
				flag_suberi1=0 #0コマ滑り
			
			case 12: #レア役AP
				flag_suberi1=0 #0コマ滑り
			
			case 13: #レア役BP
				flag_suberi1=koma_size*4 #4コマ滑り
			
			case 14: #レア役ABP
				flag_suberi1=koma_size*3 #3コマ滑り
			
			case 15: #ハズレ
				flag_suberi1=koma_size*1 #1コマ滑り
			
			case _:
				print("flag_suberi1_calc処理エラー")
				




# メイン処理
try:
	# フラグの宣言
	flg = 0
	seiten_flg=0
	
	# 繰り返しスイッチの状態を確認してフラグをセットする
	while True:
		global phase_cnt

		# スイッチの状態をチェック
		flg = check_switch()

		# フラグに応じてモータを制御する
		if (flg == 1):
			pass
			
		elif (flg == 2):
			pass
			
		elif (flg == 3):
			stop_flg=1
			
			
		elif (flg == 4):
			seiten_flg=1
			stop_flg=0
			

		if(seiten_flg==1):
			rotate_spm_continue()


		# 0.1秒待機
		#time.sleep(0.1)
		
except KeyboardInterrupt:
	print("\nプログラムが中断されました")

finally:
	GPIO.cleanup()
	print("GPIOのクリーンアップが完了しました")
