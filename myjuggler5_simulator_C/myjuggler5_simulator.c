#include<stdio.h>
#include<stdlib.h>
#include<time.h>

int sokaitensu=0; //総回転数
int samaisu=0; //差枚数
int settei=0; //設定
int ran=0; //乱数を入れる変数
int shikokaisu=0; //試行回数を入れる変数
int seiritsukaisu[16]={0};	 //成立した総回数
					  		 //0単独ビッグ,1チェリー重複ビッグ,2単独レギュラー,3チェリー重複レギュラー
					  		 //4非重複チェリー,5ブドウ,6リプレイ,7ベル,8ピエロ,9レアチェリーA,10レアチェリーB
							 //11レア役P,12レア役AP,13レア役BP,14レア役ABP,15ハズレ
							 
int yakukakuritsu[16]={0};   //役確率
						     //0単独ビッグ,1チェリー重複ビッグ,2単独レギュラー,3チェリー重複レギュラー
							 //4非重複チェリー,5ブドウ,6リプレイ,7ベル,8ピエロ,9レアチェリーA,10レアチェリーB
							 //11レア役P,12レア役AP,13レア役BP,14レア役ABP,15ハズレ

int myrand(); //乱数を生成する関数
void chusen(int ran); // 抽選をする関数
void display(); //画面表示をする関数
void shiko();	//試行回数に応じた抽選をし、結果を画面表示する関数
void reset(); //初期化する関数


int main(void){
	
	srand((unsigned int)time(NULL)); // 現在時刻の情報で初期化
	
	while(1){
		printf("\n");
		printf("設定を入力してください(1～6)\n→");
		scanf("%d",&settei);
		while (getchar() != '\n'); // 入力バッファをクリア
		printf("\n");
		
		switch(settei){
			case 1: //設定1
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
				
				shiko();
				break;
				
			case 2: //設定2
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
				
				shiko();
				break;
			
			case 3: //設定3
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
				
				shiko();
				break;
			
			case 4: //設定4
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
				
				shiko();
				break;
			
			case 5: //設定5
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
				
				shiko();
				break;
			
			case 6: //設定6
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
				
				shiko();
				break;
			
			default:
				printf("正しい設定を入力してください!!\n\n");
		}//switch(settei)の終わり
	}//while(1)の終わり
	
	return 0;
}



int myrand(){
	
	int RAN1=0,RAN2=0,RAN=0;
	
	RAN1=rand() % 2; // 0か1の乱数を発生
	//printf("RAN1:%d\n",RAN1); //デバッグ用
	RAN2=rand() % 32768 + 1; // 1から32768までの乱数を発生
	//printf("RAN2:%d\n",RAN2); //デバッグ用
	
	// 1から65536までの乱数生成
	if(RAN1==0){
		RAN=RAN2;
	}else{
		RAN=RAN2+32768;
	}
	
	 return RAN;
	
}

void chusen(int ran){
	
	sokaitensu++;
	
	if(ran<=yakukakuritsu[0]){ //単独ビッグ成立時の処理を書く
		seiritsukaisu[0]++;
		samaisu+=(240-4);
	}else if(ran<=yakukakuritsu[1]){ //チェリー重複ビッグの処理を書く
		seiritsukaisu[1]++;
		samaisu+=(240-2);
	}else if(ran<=yakukakuritsu[2]){ //単独レギュラーの処理を書く
		seiritsukaisu[2]++;
		samaisu+=(96-4);
	}else if(ran<=yakukakuritsu[3]){ //チェリー重複レギュラーの処理を書く
		seiritsukaisu[3]++;
		samaisu+=(96-2);
	}else if(ran<=yakukakuritsu[4]){ //非重複チェリーの処理を書く
		seiritsukaisu[4]++;
		samaisu-=1;
	}else if(ran<=yakukakuritsu[5]){ //ブドウの処理を書く
		seiritsukaisu[5]++;
		samaisu+=5;
	}else if(ran<=yakukakuritsu[6]){ //リプレイの処理を書く
		seiritsukaisu[6]++;
	}else if(ran<=yakukakuritsu[7]){ //ベルの処理を書く
		seiritsukaisu[7]++;
		//samaisu+=11; //フル攻略時
		samaisu-=3;
	}else if(ran<=yakukakuritsu[8]){ //ピエロの処理を書く
		seiritsukaisu[8]++;
		//samaisu+=7; //フル攻略時
		samaisu-=3;
	}else if(ran<=yakukakuritsu[9]){ //レアチェリーAの処理を書く
		seiritsukaisu[9]++;
		samaisu+=(240-3);
	}else if(ran<=yakukakuritsu[10]){ //レアチェリーBの処理を書く
		seiritsukaisu[10]++;
		samaisu+=(240-3);
	}else if(ran<=yakukakuritsu[11]){ //レア役Pの処理を書く
		seiritsukaisu[11]++;
		samaisu+=(240-4);
	}else if(ran<=yakukakuritsu[12]){ //レア役APの処理を書く
		seiritsukaisu[12]++;
		samaisu+=(240-3);
	}else if(ran<=yakukakuritsu[13]){ //レア役BPの処理を書く
		seiritsukaisu[13]++;
		samaisu+=(240-3);
	}else if(ran<=yakukakuritsu[14]){ //レア役ABPの処理を書く
		seiritsukaisu[14]++;
		samaisu+=(240-3);
	}else{							//ハズレ時の処理を書く
		seiritsukaisu[15]++;
		samaisu-=3;
	}
}

void display(){
	int big=seiritsukaisu[0]+seiritsukaisu[1]+seiritsukaisu[9]+seiritsukaisu[10]+seiritsukaisu[11]+seiritsukaisu[12]+seiritsukaisu[13]+seiritsukaisu[14]; //ビッグ合算回数
	int reg=seiritsukaisu[2]+seiritsukaisu[3]; //レギュラー合算回数
	printf("設定:%24d\n",settei);
	printf("総回転数:%18d回\n",sokaitensu);
	printf("差枚数:%20d枚\n",samaisu);
	printf("機械割:%20.2f％\n",((((double)20.0*samaisu/sokaitensu)+60)/0.6)); //機械割n%、総回転数m回なら、60円×(n×0.01-1)×m=差枚数×20円。※60の数値は1回転あたり60円必要なことから。
	printf("単独ビッグ:%16d回   1/%.4f\n",seiritsukaisu[0],(float)1.0*sokaitensu/seiritsukaisu[0]);
	printf("チェリー重複ビッグ:%8d回   1/%.4f\n",seiritsukaisu[1],(float)1.0*sokaitensu/seiritsukaisu[1]);
	printf("レアチェリーA重複ビッグ:%3d回   1/%.4f\n",seiritsukaisu[9],(float)1.0*sokaitensu/seiritsukaisu[9]);
	printf("レアチェリーB重複ビッグ:%3d回   1/%.4f\n",seiritsukaisu[10],(float)1.0*sokaitensu/seiritsukaisu[10]);
	printf("レア役P重複ビッグ:%9d回   1/%.4f\n",seiritsukaisu[11],(float)1.0*sokaitensu/seiritsukaisu[11]);
	printf("レア役AP重複ビッグ:%8d回   1/%.4f\n",seiritsukaisu[12],(float)1.0*sokaitensu/seiritsukaisu[12]);
	printf("レア役BP重複ビッグ:%8d回   1/%.4f\n",seiritsukaisu[13],(float)1.0*sokaitensu/seiritsukaisu[13]);
	printf("レア役ABP重複ビッグ:%7d回   1/%.4f\n",seiritsukaisu[14],(float)1.0*sokaitensu/seiritsukaisu[14]);
	printf("ビッグ合算:%16d回   1/%.4f\n",big,(float)1.0*sokaitensu/big);
	printf("単独レギュラー:%12d回   1/%.4f\n",seiritsukaisu[2],(float)1.0*sokaitensu/seiritsukaisu[2]);
	printf("チェリー重複レギュラー:%4d回   1/%.4f\n",seiritsukaisu[3],(float)1.0*sokaitensu/seiritsukaisu[3]);
	printf("レギュラー合算:%12d回   1/%.4f\n",reg,(float)1.0*sokaitensu/reg);
	printf("ボーナス合算:%14d回   1/%.4f\n",big+reg,(float)1.0*sokaitensu/(big+reg));
	printf("非重複チェリー:%12d回   1/%.4f\n",seiritsukaisu[4],(float)1.0*sokaitensu/seiritsukaisu[4]);
	printf("ブドウ:%20d回   1/%.4f\n",seiritsukaisu[5],(float)1.0*sokaitensu/seiritsukaisu[5]);
	printf("リプレイ:%18d回   1/%.4f\n",seiritsukaisu[6],(float)1.0*sokaitensu/seiritsukaisu[6]);
	printf("ベル:%22d回   1/%.4f\n",seiritsukaisu[7],(float)1.0*sokaitensu/seiritsukaisu[7]);
	printf("ピエロ:%20d回   1/%.4f\n",seiritsukaisu[8],(float)1.0*sokaitensu/seiritsukaisu[8]);
	printf("ハズレ:%20d回   1/%.4f\n\n",seiritsukaisu[15],(float)1.0*sokaitensu/seiritsukaisu[15]);
}

void shiko(){
	while(1){
		printf("試行回数を選択してください。\n");
		printf("1:1回\n");
		printf("2:10回\n");
		printf("3:100回\n");
		printf("4:1000回\n");
		printf("5:1万回\n");
		printf("6:10万回\n");
		printf("7:100万回\n");
		printf("→");
		scanf("%d",&shikokaisu);
		while (getchar() != '\n'); // 入力バッファをクリア
		
		switch(shikokaisu){
			case 1: //試行回数1回
				ran=myrand();
				//printf("ran:%d\n",ran); //デバッグ用
				chusen(ran);
				display();
				break;
			
			case 2: //思考回数10回
				for(int i=0;i<10;i++){
					ran=myrand();
					//printf("ran:%d\n",ran); //デバッグ用
					chusen(ran);
					display();
				}
				break;
			
			case 3: //思考回数100回
				for(int i=0;i<100;i++){
					ran=myrand();
					//printf("ran:%d\n",ran); //デバッグ用
					chusen(ran);
				}
				display();
				break;
			
			case 4: //思考回数1000回
				for(int i=0;i<1000;i++){
					ran=myrand();
					//printf("ran:%d\n",ran); //デバッグ用
					chusen(ran);
				}
				display();
				break;
			
			case 5: //思考回数1万回
				for(int i=0;i<10000;i++){
					ran=myrand();
					//printf("ran:%d\n",ran); //デバッグ用
					chusen(ran);
				}
				display();
				break;
			
			case 6: //思考回数10万回
				for(int i=0;i<100000;i++){
					ran=myrand();
					//printf("ran:%d\n",ran); //デバッグ用
					chusen(ran);
				}
				display();
				break;
			
			case 7: //思考回数100万回
				for(int i=0;i<1000000;i++){
					ran=myrand();
					//printf("ran:%d\n",ran); //デバッグ用
					chusen(ran);
				}
				display();
				break;
			
			default:
				printf("\n正しい数値を入力してください!!\n\n\n");
		}//switch(shikokaisu)の終わり
	}//while(1)の終わり
}

void reset(){
	sokaitensu=0; //総回転数
	samaisu=0; //差枚数
	settei=0; //設定
	ran=0; //乱数を入れる変数
	shikokaisu=0; //試行回数を入れる変数
	for(int i=0;i<16;i++){
		seiritsukaisu[i]=0;
	}
}

