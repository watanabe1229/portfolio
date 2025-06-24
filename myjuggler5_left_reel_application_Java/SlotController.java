import javafx.animation.AnimationTimer;
import javafx.fxml.FXML;
import javafx.scene.control.TextField;
import javafx.scene.control.ChoiceBox;

//import javafx.scene.image.Image;
//import javafx.scene.image.ImageView;
import javafx.scene.image.*;
import javafx.collections.FXCollections;
import java.security.SecureRandom;


public class SlotController {
    @FXML
    private ImageView slotImage1, slotImage2, slotImage3, GoGoLamp;
    @FXML
    private TextField start_field, BB_field,RB_field,sokaitensu_field,samaisu_field;
	
	@FXML
	private TextField t1_field,t2_field,t3_field,yaku_flag_field,flag_suberi1_field,t1_at_stop_field,t1_43_field,gedan_number_at_stop_field; //デバッグ用
	
	@FXML
	private ChoiceBox<Integer> settei;

    private final Image[] images = new Image[5]; // スロット画像
    private final int[] currentIcons = {0, 1, 2, 3};
    private final boolean[] stopped = {true, true, true};
	private final AnimationTimer timer = new AnimationTimer() {
	    @Override
	    public void handle(long now) {
	        // アニメーションの処理
	        if (now - lastUpdateTime >= interval) {
	            updateImages();
	        	t1_field.setText(String.valueOf(t1));//デバッグ用
		    	t2_field.setText(String.valueOf(t2));//デバッグ用
		    	t3_field.setText(String.valueOf(t3));//デバッグ用
	            lastUpdateTime = now;
	        	if(t1%43<=suberi_margin && t2%43<=suberi_margin && t3%43<=suberi_margin && allStopped()){
	        		evaluateResult();
	        		//timer.stop();
	        	}
	        }
	    }
	};
    private long lastUpdateTime = 0;
    private final long interval = 1000_000L; // ※調整用変数・・・各スロットの回転間隔（ナノ秒）(1000_100Lくらいがちょうどいい？その場合はtrimming_move_speedは20が標準速度。)
	public static int t1=0,t2=0,t3=0;
	public int trimming_move_speed=2; // ※調整用変数・・・20が標準速度（1分間に約80回転） 数値を大きくすると本来の停止位置をオーバーして停止してしまう←標準速度の20であれば問題なく動作する。(処理順序やアルゴリズムの問題か？)
	public final int start_position=900; //リール開始位置
	private int suberi1=0,suberi2=0,suberi3=0; //すべり必要距離残変数の宣言及び初期化
	private int suberi_margin=3; //※調整用変数・・・すべり停止位置の許容誤差（この値が小さいとリール停止位置の誤差は少なくなるが、止まりきれず本来の停止位置をオーバーしてしまうことがある。また、この値を大きくするとリール停止位置の誤差は大きくなるが、停止位置をオーバーしてしまうことが少なくなる。)
	private int flag_suberi1=0,flag_suberi2=0,flag_suberi3=0; //フラグ抽選結果に応じたすべり距離
	//public int w1=(int)slotImage1.getFitWidth();
    //public int h1=(int)slotImage1.getFitHeight();
	private SecureRandom secureRand = new SecureRandom(); // 1～65536までの乱数生成方法：(secureRand.nextInt(65536)+1)
	private int big=0,reg=0,sokaitensu=0,startsu=0,samaisu=0; //ビッグ回数、レギュラー回数、総回転数、スタート回数、差枚数
	private final int shokizure=43*3;//スタート初期位置のずれ分の修正用。①番のブドウがスタート位置から3コマ後に来るため。（①番のブドウについてはインターネットでリール配置図を調べて下さい。）
	private int yaku_flag=111; //役フラグ
							  //0単独ビッグ,1チェリー重複ビッグ,2単独レギュラー,3チェリー重複レギュラー
							  //4非重複チェリー,5ブドウ,6リプレイ,7ベル,8ピエロ,9レアチェリーA,10レアチェリーB
							  //11レア役P,12レア役AP,13レア役BP,14レア役ABP,15ハズレ
	
	private int[] yakukakuritsu={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};   //役確率
								     								 //0単独ビッグ,1チェリー重複ビッグ,2単独レギュラー,3チェリー重複レギュラー
									 								 //4非重複チェリー,5ブドウ,6リプレイ,7ベル,8ピエロ,9レアチェリーA,10レアチェリーB
																	 //11レア役P,12レア役AP,13レア役BP,14レア役ABP,15ハズレ
	
	private int[] seiritsukaisu={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};	 //成立した総回数
					  		 										 //0単独ビッグ,1チェリー重複ビッグ,2単独レギュラー,3チェリー重複レギュラー
															  		 //4非重複チェリー,5ブドウ,6リプレイ,7ベル,8ピエロ,9レアチェリーA,10レアチェリーB
																	 //11レア役P,12レア役AP,13レア役BP,14レア役ABP,15ハズレ
	
    @FXML
    public void initialize() {
    	
		//ChoiceBox<String> settei = new ChoiceBox<>();
		//settei.getItems().addAll("item1", "item2", "item3");
    	settei.setItems(FXCollections.observableArrayList( 1,2,3,4,5,6 ));
    	settei.setValue(1);//設定に1を代入
    	//setteihenko(); //役確率を設定1の数値に初期化

        // スロット画像の読み込み
        for (int i = 0; i < images.length; i++) {
            images[i] = new Image("file:./im" + i + ".jpg");
        }
        updateImages();
    }

    @FXML
    private void start() {
    	//if(allStopped()){ //本番環境用
    	
    	setteihenko();
    	
    	chusen();
    	
    	//役フラグ
	  //0単独ビッグ,1チェリー重複ビッグ,2単独レギュラー,3チェリー重複レギュラー
	  //4非重複チェリー,5ブドウ,6リプレイ,7ベル,8ピエロ,9レアチェリーA,10レアチェリーB
	  //11レア役P,12レア役AP,13レア役BP,14レア役ABP,15ハズレ
	  //レアチェリーAが2粒チェリーのこと。
    	
    	yaku_flag=14; //デバッグ用
    	
    	updatePoints(); System.out.println("差枚数"+samaisu+" 役フラグ"+yaku_flag);//デバッグ用
    	yaku_flag_field.setText(String.valueOf(yaku_flag));//デバッグ用

        for (int i = 0; i < stopped.length; i++) {
            stopped[i] = false;
        }
    	timer.start();
    }

    @FXML
    private void stop1() {
    	//currentIcons[0]=1;//デバッグ用
        //stopSlot(0);
    	//System.out.println("stopped[0]:"+stopped[0]+"  stopped[1]:"+stopped[1]+"  allStopped():"+allStopped());
    	if(!stopped[0]){
    		stopped[0] = true;
        	flag_suberi1_calc();
    		System.out.println("flag_suberi1:"+flag_suberi1+" t1:"+t1);//デバッグ用
    		flag_suberi1_field.setText(String.valueOf(flag_suberi1));//デバッグ用
    		t1_at_stop_field.setText(String.valueOf(t1));//デバッグ用
    		t1_43_field.setText(String.valueOf(t1/43));//デバッグ用
    		//////////↓デバッグ用↓//////////
    		int gedan_number_at_stop=1111;//デバッグ用
    		if(t1<43*2){
    			gedan_number_at_stop=(t1/43)+20;
    		}else if(t1<43*3){
    			gedan_number_at_stop=1;
    		}else{
    			gedan_number_at_stop=(t1/43)-1;
    		}
    		gedan_number_at_stop_field.setText(String.valueOf(gedan_number_at_stop));//デバッグ用
    		//////////↑デバッグ用↑//////////
    	}
    }

    @FXML
    private void stop2() {
    	if(!stopped[1] && stopped[0]){
    		//stopped[1] = true;
        	//flag_suberi2_calc();
    		
    	}
    	//currentIcons[1]=1;//デバッグ用
        //stopSlot(1);
    }

    @FXML
    private void stop3() {
    	//currentIcons[2]=1;//デバッグ用
        //stopSlot(2);
    }

    /*private void stopSlot(int index) {
        if (!stopped[index]) {
            //timers[index].stop();
            stopped[index] = true;
        	flag_suberi_calc();
            /*if (allStopped()) {
                evaluateResult();
            }*//*
        }
    }*/
	
	

    private void updateImages() {
    	int w1=(int)slotImage1.getFitWidth();
    	int h1=(int)slotImage1.getFitHeight();
    	WritableImage cutimg1=null;
    	WritableImage cutimg2=null;
    	WritableImage cutimg3=null;
    	/*WritableImage cutimg1=new WritableImage(images[currentIcons[0]].getPixelReader(), 0, start_position-t1, w1, h1); //左リール初期位置
    	WritableImage cutimg2=new WritableImage(images[currentIcons[1]].getPixelReader(), 0, start_position-t1, w1, h1); //左リール初期位置
    	WritableImage cutimg3=new WritableImage(images[currentIcons[2]].getPixelReader(), 0, 896-t1, w1, h1); //左リール初期位置*/
    	//WritableImage cutimg1=new WritableImage(images[currentIcons[0]].getPixelReader(), 0, 0, w1, h1); //左リール
    	//WritableImage cutimg2=new WritableImage(images[currentIcons[1]].getPixelReader(), 0, 0, w1, h1); //中リール
    	//WritableImage cutimg3=new WritableImage(images[currentIcons[2]].getPixelReader(), 0, 0, w1, h1); //右リール
        //WritableImage cutimg1=new WritableImage(images[currentIcons[0]].getPixelReader(), 0, 0, w1, h1); //左リール
    	//WritableImage cutimg1=new WritableImage(images[currentIcons[0]].getPixelReader(), 0, t1, w1, h1); //左リール 逆転
		if(!stopped[0] || suberi1>suberi_margin || flag_suberi1>0){
    		/*cutimg1=new WritableImage(images[currentIcons[0]].getPixelReader(), 0, start_position-t1, w1, h1); //左リール 正転
    		slotImage1.setImage(cutimg1);*/
			t1=t1+trimming_move_speed;
			if(t1>=start_position){
				t1=0; 
			}
			suberi1=t1%43;
			if(stopped[0] && flag_suberi1>=0){
				flag_suberi1-=trimming_move_speed;
			}
		}
		if(!stopped[1] || suberi2>suberi_margin){
    		/*cutimg2=new WritableImage(images[currentIcons[1]].getPixelReader(), 0, start_position-t2, w1, h1); //中リール 正転
    		slotImage2.setImage(cutimg2);*/
			t2=t2+trimming_move_speed;
			if(t2>=start_position){
				t2=0;
			}
			suberi2=t2%43;
		}
		if(!stopped[2] || suberi3>suberi_margin){
    		/*cutimg3=new WritableImage(images[currentIcons[2]].getPixelReader(), 0, start_position-t3, w1, h1); //右リール 正転
    		slotImage3.setImage(cutimg3);*/
			t3=t3+trimming_move_speed;
			if(t3>=896){
				t3=0;
			}
			suberi3=t3%43;
		}
    	cutimg1=new WritableImage(images[currentIcons[0]].getPixelReader(), 0, start_position-t1, w1, h1); //左リール 正転
    	slotImage1.setImage(cutimg1);
    	cutimg2=new WritableImage(images[currentIcons[1]].getPixelReader(), 0, start_position-t2, w1, h1); //中リール 正転
    	slotImage2.setImage(cutimg2);
    	cutimg3=new WritableImage(images[currentIcons[2]].getPixelReader(), 0, start_position-t3, w1, h1); //右リール 正転
    	slotImage3.setImage(cutimg3);
    	GoGoLamp.setImage(images[currentIcons[3]]);
    }

    private void updatePoints() {
        start_field.setText(String.valueOf(startsu));
        BB_field.setText(String.valueOf(startsu));
    	RB_field.setText(String.valueOf(startsu));
    	sokaitensu_field.setText(String.valueOf(sokaitensu));
    	samaisu_field.setText(String.valueOf(samaisu));
    	t1_field.setText(String.valueOf(t1));
    	t2_field.setText(String.valueOf(t2));
    	t3_field.setText(String.valueOf(t3));
    }

    private boolean allStopped() {
        return stopped[0] && stopped[1] && stopped[2];
    }

    private void evaluateResult() {
    	/*if (currentIcons[0] == currentIcons[1] && currentIcons[1] == currentIcons[2]) {
	        //points += bet * 10; // 当たりの得点倍率
	        currentIcons[3] = 4; // 当たりの画像
	        System.out.println("当たり！");
	    } else {
	        currentIcons[3] = 3; // ハズレの画像
	    }*/
        /*if (currentIcons[0] == currentIcons[1]) points += bet;
        if (currentIcons[1] == currentIcons[2]) points += bet;
        if (currentIcons[2] == currentIcons[0]) points += bet;*/
        updatePoints();
    	updateImages();
    	
    	
    	//timer.stop();
    }
	
/*	private void isallstopped(){
		if(allStopped() && currentIcons[0] == currentIcons[1] && currentIcons[1] == currentIcons[2]){
                    currentIcons[3]=8;
                    System.out.println("aaa");
        }else{
                    		currentIcons[3]=7;
        }
	}*/
	
	
	void chusen(){
		int ran =secureRand.nextInt(65536)+1; //1から65536までの乱数生成
		sokaitensu++;
		startsu++;
		
		if(ran<=yakukakuritsu[0]){ //単独ビッグフラグ時の処理を書く
			seiritsukaisu[0]++;
			yaku_flag=0;
			samaisu+=(240-4);
		}else if(ran<=yakukakuritsu[1]){ //チェリー重複ビッグフラグ時の処理を書く
			seiritsukaisu[1]++;
			yaku_flag=1;
			samaisu+=(240-2);
		}else if(ran<=yakukakuritsu[2]){ //単独レギュラーフラグ時の処理を書く
			seiritsukaisu[2]++;
			yaku_flag=2;
			samaisu+=(96-4);
		}else if(ran<=yakukakuritsu[3]){ //チェリー重複レギュラーフラグ時の処理を書く
			seiritsukaisu[3]++;
			yaku_flag=3;
			samaisu+=(96-2);
		}else if(ran<=yakukakuritsu[4]){ //非重複チェリーフラグ時の処理を書く
			seiritsukaisu[4]++;
			yaku_flag=4;
			samaisu-=1;
		}else if(ran<=yakukakuritsu[5]){ //ブドウフラグ時の処理を書く
			seiritsukaisu[5]++;
			yaku_flag=5;
			samaisu+=5;
		}else if(ran<=yakukakuritsu[6]){ //リプレイフラグ時の処理を書く
			seiritsukaisu[6]++;
			yaku_flag=6;
		}else if(ran<=yakukakuritsu[7]){ //ベルフラグ時の処理を書く
			seiritsukaisu[7]++;
			yaku_flag=7;
			//samaisu+=11; //フル攻略時
			samaisu-=3;
		}else if(ran<=yakukakuritsu[8]){ //ピエロフラグ時の処理を書く
			seiritsukaisu[8]++;
			yaku_flag=8;
			//samaisu+=7; //フル攻略時
			samaisu-=3;
		}else if(ran<=yakukakuritsu[9]){ //レアチェリーAフラグ時の処理を書く
			seiritsukaisu[9]++;
			yaku_flag=9;
			samaisu+=(240-3);
		}else if(ran<=yakukakuritsu[10]){ //レアチェリーBフラグ時の処理を書く
			seiritsukaisu[10]++;
			yaku_flag=10;
			samaisu+=(240-3);
		}else if(ran<=yakukakuritsu[11]){ //レア役Pフラグ時の処理を書く
			seiritsukaisu[11]++;
			yaku_flag=11;
			samaisu+=(240-4);
		}else if(ran<=yakukakuritsu[12]){ //レア役APフラグ時の処理を書く
			seiritsukaisu[12]++;
			yaku_flag=12;
			samaisu+=(240-3);
		}else if(ran<=yakukakuritsu[13]){ //レア役BPフラグ時の処理を書く
			seiritsukaisu[13]++;
			yaku_flag=13;
			samaisu+=(240-3);
		}else if(ran<=yakukakuritsu[14]){ //レア役ABPフラグ時の処理を書く
			seiritsukaisu[14]++;
			yaku_flag=14;
			samaisu+=(240-3);
		}else{							//ハズレフラグ時の処理を書く
			seiritsukaisu[15]++;
			yaku_flag=15;
			samaisu-=3;
		}
		
		System.out.println(ran); //デバッグ用
		
	}
	
	void setteihenko(){
		switch(settei.getValue()){
		case 1://設定1
			//役確率の設定
			yakukakuritsu[0]=160;						//単独ビッグ
			yakukakuritsu[1]=yakukakuritsu[0]+46;		//チェリー重複ビッグ
			yakukakuritsu[2]=yakukakuritsu[1]+100;		//単独レギュラー
			yakukakuritsu[3]=yakukakuritsu[2]+60;		//チェリー重複レギュラー
			yakukakuritsu[4]=yakukakuritsu[3]+1720;		//非重複チェリー
			yakukakuritsu[5]=yakukakuritsu[4]+11108;	//ブドウ
			yakukakuritsu[6]=yakukakuritsu[5]+8980;		//リプレイ
			yakukakuritsu[7]=yakukakuritsu[6]+64;		//ベル
			yakukakuritsu[8]=yakukakuritsu[7]+64;		//ピエロ
			yakukakuritsu[9]=yakukakuritsu[8]+9;		//レアチェリーA
			yakukakuritsu[10]=yakukakuritsu[9]+9;		//レアチェリーB
			yakukakuritsu[11]=yakukakuritsu[10]+4;		//レア役P
			yakukakuritsu[12]=yakukakuritsu[11]+4;		//レア役AP
			yakukakuritsu[13]=yakukakuritsu[12]+6;		//レア役BP
			yakukakuritsu[14]=yakukakuritsu[13]+2;		//レア役ABP
			//yakukakuritsu[15]=yakukakuritsu[14]+43200;//ハズレ
			break;
		case 2://設定2
			//役確率の設定
			yakukakuritsu[0]=161;						//単独ビッグ
			yakukakuritsu[1]=yakukakuritsu[0]+47;		//チェリー重複ビッグ
			yakukakuritsu[2]=yakukakuritsu[1]+109;		//単独レギュラー
			yakukakuritsu[3]=yakukakuritsu[2]+61;		//チェリー重複レギュラー
			yakukakuritsu[4]=yakukakuritsu[3]+1720;		//非重複チェリー
			yakukakuritsu[5]=yakukakuritsu[4]+11203;	//ブドウ
			yakukakuritsu[6]=yakukakuritsu[5]+8980;		//リプレイ
			yakukakuritsu[7]=yakukakuritsu[6]+64;		//ベル
			yakukakuritsu[8]=yakukakuritsu[7]+64;		//ピエロ
			yakukakuritsu[9]=yakukakuritsu[8]+9;		//レアチェリーA
			yakukakuritsu[10]=yakukakuritsu[9]+9;		//レアチェリーB
			yakukakuritsu[11]=yakukakuritsu[10]+4;		//レア役P
			yakukakuritsu[12]=yakukakuritsu[11]+4;		//レア役AP
			yakukakuritsu[13]=yakukakuritsu[12]+6;		//レア役BP
			yakukakuritsu[14]=yakukakuritsu[13]+2;		//レア役ABP
			//yakukakuritsu[15]=yakukakuritsu[14]+43093;//ハズレ
			break;
		case 3://設定3
			//役確率の設定
			yakukakuritsu[0]=164;						//単独ビッグ
			yakukakuritsu[1]=yakukakuritsu[0]+48;		//チェリー重複ビッグ
			yakukakuritsu[2]=yakukakuritsu[1]+133;		//単独レギュラー
			yakukakuritsu[3]=yakukakuritsu[2]+62;		//チェリー重複レギュラー
			yakukakuritsu[4]=yakukakuritsu[3]+1780;		//非重複チェリー
			yakukakuritsu[5]=yakukakuritsu[4]+11299;	//ブドウ
			yakukakuritsu[6]=yakukakuritsu[5]+8980;		//リプレイ
			yakukakuritsu[7]=yakukakuritsu[6]+64;		//ベル
			yakukakuritsu[8]=yakukakuritsu[7]+64;		//ピエロ
			yakukakuritsu[9]=yakukakuritsu[8]+9;		//レアチェリーA
			yakukakuritsu[10]=yakukakuritsu[9]+9;		//レアチェリーB
			yakukakuritsu[11]=yakukakuritsu[10]+4;		//レア役P
			yakukakuritsu[12]=yakukakuritsu[11]+4;		//レア役AP
			yakukakuritsu[13]=yakukakuritsu[12]+6;		//レア役BP
			yakukakuritsu[14]=yakukakuritsu[13]+2;		//レア役ABP
			//yakukakuritsu[15]=yakukakuritsu[14]+42908;//ハズレ
			break;
		case 4://設定4
			//役確率の設定
			yakukakuritsu[0]=173;						//単独ビッグ
			yakukakuritsu[1]=yakukakuritsu[0]+51;		//チェリー重複ビッグ
			yakukakuritsu[2]=yakukakuritsu[1]+161;		//単独レギュラー
			yakukakuritsu[3]=yakukakuritsu[2]+65;		//チェリー重複レギュラー
			yakukakuritsu[4]=yakukakuritsu[3]+1840;		//非重複チェリー
			yakukakuritsu[5]=yakukakuritsu[4]+11338;	//ブドウ
			yakukakuritsu[6]=yakukakuritsu[5]+8980;		//リプレイ
			yakukakuritsu[7]=yakukakuritsu[6]+64;		//ベル
			yakukakuritsu[8]=yakukakuritsu[7]+64;		//ピエロ
			yakukakuritsu[9]=yakukakuritsu[8]+9;		//レアチェリーA
			yakukakuritsu[10]=yakukakuritsu[9]+9;		//レアチェリーB
			yakukakuritsu[11]=yakukakuritsu[10]+4;		//レア役P
			yakukakuritsu[12]=yakukakuritsu[11]+4;		//レア役AP
			yakukakuritsu[13]=yakukakuritsu[12]+6;		//レア役BP
			yakukakuritsu[14]=yakukakuritsu[13]+2;		//レア役ABP
			//yakukakuritsu[15]=yakukakuritsu[14]+42766;//ハズレ
			break;
		case 5://設定5
			//役確率の設定
			yakukakuritsu[0]=185;						//単独ビッグ
			yakukakuritsu[1]=yakukakuritsu[0]+54;		//チェリー重複ビッグ
			yakukakuritsu[2]=yakukakuritsu[1]+168;		//単独レギュラー
			yakukakuritsu[3]=yakukakuritsu[2]+76;		//チェリー重複レギュラー
			yakukakuritsu[4]=yakukakuritsu[3]+1840;		//非重複チェリー
			yakukakuritsu[5]=yakukakuritsu[4]+11378;	//ブドウ
			yakukakuritsu[6]=yakukakuritsu[5]+8980;		//リプレイ
			yakukakuritsu[7]=yakukakuritsu[6]+64;		//ベル
			yakukakuritsu[8]=yakukakuritsu[7]+64;		//ピエロ
			yakukakuritsu[9]=yakukakuritsu[8]+9;		//レアチェリーA
			yakukakuritsu[10]=yakukakuritsu[9]+9;		//レアチェリーB
			yakukakuritsu[11]=yakukakuritsu[10]+4;		//レア役P
			yakukakuritsu[12]=yakukakuritsu[11]+4;		//レア役AP
			yakukakuritsu[13]=yakukakuritsu[12]+6;		//レア役BP
			yakukakuritsu[14]=yakukakuritsu[13]+2;		//レア役ABP
			//yakukakuritsu[15]=yakukakuritsu[14]+42693;//ハズレ
			break;
		case 6://設定6
			//役確率の設定
			yakukakuritsu[0]=194;						//単独ビッグ
			yakukakuritsu[1]=yakukakuritsu[0]+58;		//チェリー重複ビッグ
			yakukakuritsu[2]=yakukakuritsu[1]+200;		//単独レギュラー
			yakukakuritsu[3]=yakukakuritsu[2]+86;		//チェリー重複レギュラー
			yakukakuritsu[4]=yakukakuritsu[3]+1840;		//非重複チェリー
			yakukakuritsu[5]=yakukakuritsu[4]+11579;	//ブドウ
			yakukakuritsu[6]=yakukakuritsu[5]+8980;		//リプレイ
			yakukakuritsu[7]=yakukakuritsu[6]+64;		//ベル
			yakukakuritsu[8]=yakukakuritsu[7]+64;		//ピエロ
			yakukakuritsu[9]=yakukakuritsu[8]+9;		//レアチェリーA
			yakukakuritsu[10]=yakukakuritsu[9]+9;		//レアチェリーB
			yakukakuritsu[11]=yakukakuritsu[10]+4;		//レア役P
			yakukakuritsu[12]=yakukakuritsu[11]+4;		//レア役AP
			yakukakuritsu[13]=yakukakuritsu[12]+6;		//レア役BP
			yakukakuritsu[14]=yakukakuritsu[13]+2;		//レア役ABP
			//yakukakuritsu[15]=yakukakuritsu[14]+42437;//ハズレ
			break;
		default:
			System.out.println("設定変更エラーのため異常終了します。");
			System.exit(0);
		}
	}
	
	
	 //役フラグ
	  //0単独ビッグ,1チェリー重複ビッグ,2単独レギュラー,3チェリー重複レギュラー
	  //4非重複チェリー,5ブドウ,6リプレイ,7ベル,8ピエロ,9レアチェリーA,10レアチェリーB
	  //11レア役P,12レア役AP,13レア役BP,14レア役ABP,15ハズレ
	  //レアチェリーAが2粒チェリーのこと。
	
	void flag_suberi1_calc(){
		if(t1>=43*0+shokizure && t1<43*1+shokizure){ //②番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=0; //0コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=0; //0コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=0; //0コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=0; //0コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=0; //0コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=0; //0コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=0; //0コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=0; //0コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=0; //0コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*1+shokizure && t1<43*2+shokizure){ //③番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=0; //0コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*3; //3コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*2+shokizure && t1<43*3+shokizure){ //④番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*4; //4コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*3+shokizure && t1<43*4+shokizure){ //⑤番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=0; //0コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*3; //3コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*4+shokizure && t1<43*5+shokizure){ //⑥番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=0; //0コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=0; //0コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=0; //0コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*3; //3コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*5+shokizure && t1<43*6+shokizure){ //⑦番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=0; //0コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=0; //0コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*2; //2コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*6+shokizure && t1<43*7+shokizure){ //⑧番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=0; //0コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=0; //0コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*2; //2コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*7+shokizure && t1<43*8+shokizure){ //⑨番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=0; //0コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=0; //0コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=0; //0コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=0; //0コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=0; //0コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=0; //0コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=0; //0コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=0; //0コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=0; //0コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=0; //0コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*8+shokizure && t1<43*9+shokizure){ //⑩番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=0; //0コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=0; //0コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=0; //0コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=0; //0コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=0; //0コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=0; //0コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=0; //0コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=0; //0コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=0; //0コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=0; //0コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=0; //0コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*9+shokizure && t1<43*10+shokizure){ //⑪番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=0; //0コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=0; //0コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=0; //0コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=0; //0コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=0; //0コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=0; //0コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*4; //4コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*10+shokizure && t1<43*11+shokizure){ //⑫番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*3; //3コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*11+shokizure && t1<43*12+shokizure){ //⑬番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=0; //0コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=0; //0コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*2; //2コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*12+shokizure && t1<43*13+shokizure){ //⑭番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=0; //0コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*1; //1コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*13+shokizure && t1<43*14+shokizure){ //⑮番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=0; //0コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=0; //0コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=0; //0コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=0; //0コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*3; //3コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*14+shokizure && t1<43*15+shokizure){ //⑯番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*4; //4コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*15+shokizure && t1<43*16+shokizure){ //⑰番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=0; //0コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=0; //0コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=0; //0コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=0; //0コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*2; //2コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*16+shokizure && t1<43*17+shokizure){ //⑱番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=0; //0コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=0; //0コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=0; //0コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=0; //0コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*2; //2コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*17+shokizure && t1<43*18+shokizure){ //⑲番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=0; //0コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=0; //0コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=0; //0コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=0; //0コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=0; //0コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=0; //0コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=0; //0コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=0; //0コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*1; //1コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*0 && t1<43*1){ //⑳番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=0; //0コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=0; //0コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=0; //0コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=0; //0コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=0; //0コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=0; //0コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=0; //0コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=0; //0コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=0; //0コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=0; //0コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=0; //0コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*1 && t1<43*2){ //㉑番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=0; //0コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=0; //0コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*2; //2コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		if(t1>=43*2 && t1<43*3){ //①番を下段押し
			switch(yaku_flag){
			case 0: //単独ビッグ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 1: //チェリー重複ビッグ
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 2: //単独レギュラー
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 3: //チェリー重複レギュラー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 4: //非重複チェリー
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 5: //ブドウ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 6: //リプレイ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 7: //ベル
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 8: //ピエロ
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 9: //レアチェリーA
				flag_suberi1=43*1; //1コマ滑り
				break;
			case 10: //レアチェリーB
				flag_suberi1=43*2; //2コマ滑り
				break;
			case 11: //レア役P
				flag_suberi1=0; //0コマ滑り
				break;
			case 12: //レア役AP
				flag_suberi1=0; //0コマ滑り
				break;
			case 13: //レア役BP
				flag_suberi1=43*4; //4コマ滑り
				break;
			case 14: //レア役ABP
				flag_suberi1=43*3; //3コマ滑り
				break;
			case 15: //ハズレ
				flag_suberi1=43*1; //1コマ滑り
				break;
			default:
				System.out.println("flag_suberi1_calc()処理エラーのため異常終了します。");
				System.exit(0);
			}
		}
		
	}
	
	/*  //下記にはそれぞれの抽選フラグに応じてリール制御をするための処理を書く。
	//0単独ビッグ,1チェリー重複ビッグ,2単独レギュラー,3チェリー重複レギュラー
	//4非重複チェリー,5ブドウ,6リプレイ,7ベル,8ピエロ,9レアチェリーA,10レアチェリーB
 	//11レア役P,12レア役AP,13レア役BP,14レア役ABP,15ハズレ
	void tandoku_big(){
		
	}
	void cherry_big(){
		
	}
	void tandoku_reg(){
		
	}
	void cherry_reg(){
		
	}
	void budo(){	
		
	}
	void replay(){
		
	}
	void bell(){
		
	}
	void piero(){
		
	}
	void rare_cherryA(){
		
	}
	void rare_cherryB(){
		
	}
	void rare_P(){
		
	}
	void rare_AP(){
		
	}
	void rare_BP(){
		
	}
	void rare_ABP(){
		
	}
	void hazure(){
		
	}
	*/
}
