#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include <time.h>
#include <ctype.h>
#include <stdio.h>
#include <unistd.h>

const int N=3005;
const int bili=20;
const int len=10000;
int dy[]={0,0,-1,1},dx[]={-1,1,0,0},ha[300];
int n,a[3005][3005],ya[3005][3005],zhi[3005],qx[3005*3005],qy[3005*3005],ll,rr,tot,v[3005],boxs,sm,smx,nx,ny,ans,sumk;
int js[3005][3005];
//a是地图，质数是墙合数是空地-1是箱子-2是人-3是目标，1算合数

void hexDump(void * data_ptr, size_t size)
{
    int i;
    size_t offset = 0;
    unsigned char * data = (unsigned char *)data_ptr;
    while (offset < size)
    {
        printf("%04x  ", (int)offset);
        for (i=0; i<16; i++)
        {
            if (i%8 == 0) putchar(' ');
            if (offset+i < size)
            {
                printf("%02x ", data[offset + i]);
            }
            else
            {
                printf("   ");
            }
        }
        printf("   ");
        for (i=0; i<16 && offset+i<size; i++)
        {
            if (isprint(data[offset+i]))
            {
                printf("%c", data[offset+i]);
            }
            else
            {
                putchar('.');
            }
        }
        putchar('\n');
        offset += 16;
    }
}


int init1() {
    dy[0] = 0;
    dy[1] = 0;
    dy[2] = -1;
    dy[3] = 1;
    dx[0] = -1;
    dx[1] = 1;
    dx[2] = 0;
    dx[3] = 0;
    memset(ha, 0, sizeof(ha));
    memset(a,  0, sizeof(a));
    memset(ya,  0, sizeof(ya));
    memset(zhi,  0, sizeof(zhi));
    memset(qx,  0, sizeof(qx));
    memset(qy,  0, sizeof(qy));
    memset(v,  0, sizeof(v));
    memset(js,  0, sizeof(js));
    ll = 0;
    rr = 0;
    tot = 0;
    boxs=0;
    sm = 0;
    smx = 0;
    nx = 0;
    ny = 0;
    ans = 0;
    sumk = 0;
}

int min(int a,int b)
{
    if(a<b)
        return a;
    else
        return b;
}

int ran(int x)
{
    return rand()%x;
}

int randzhi()
{
    return zhi[rand()%tot];
}

int randhe()
{
    int x=rand()%3001;
    while(!v[x])
        x=rand()%3001;
    return x;
}

void oula()
{
    v[1]=1;
    for(int i=2;i<=3000;i++)
    {
        if(!v[i])
            zhi[tot++]=i;
        for(int j=0;i*zhi[j]<=3000&&j<tot;j++)
        {
            v[i*zhi[j]]=1;
            if(i%zhi[j]==0)
                break;
        }
    }
}

void init()
{
    ha['w']=0,ha['s']=1,ha['a']=2,ha['d']=3;
    for(int i=0;i<n;i++)
        for(int j=0;j<n;j++)
            a[i][j]=randzhi();
    for(int i=1;i<n-1;i++)
        for(int j=1;j<n-1;j++)
            js[i][j]=4;
    for(int i=0;i<n;i++)
        js[0][i]=3,js[i][0]=3,js[n-1][i]=3,js[i][n-1]=3;
    js[0][0]=2;
    js[0][n-1]=2;
    js[n-1][0]=2;
    js[n-1][n-1]=2;
    
    //挖空地
    a[n/2][n/2]=randhe();
    ll=1,rr=0;
    qx[++rr]=n/2,qy[rr]=n/2;
    while(ll<=rr&&rr<min(N*N,n*n*2)&&sumk<n*n/2)
    {
        int ux=qx[ll],uy=qy[ll];
        // printf("%d     %d  %d\n",ux,uy,js[ux][uy]);
        if(--js[ux][uy]==0)
            ll++;
        int w=ran(4);
        if(ux+dx[w]>0&&ux+dx[w]<n&&uy+dy[w]>0&&uy+dy[w]<n&&!v[a[ux+dx[w]][uy+dy[w]]])
        {
            a[ux+dx[w]][uy+dy[w]]=randhe();
            qx[++rr]=ux+dx[w],qy[rr]=uy+dy[w];
            sumk++;
            // printf("%d %d\n",ux+dx[w],uy+dy[w]);
        }
    }
    
    //放人
    a[n/2][n/2]=-2;
    
    //放箱子
    while(sm<boxs)
    {
        for(int i=1;i<n-1&&sm<boxs;i++)
            for(int j=1;j<n-1&&sm<boxs;j++)
                if(v[a[i][j]]&&v[a[i-1][j]]&&v[a[i+1][j]]&&v[a[i][j-1]]&&v[a[i][j+1]]&&a[i][j]!=-2)
                {
                    if(ran(100)<bili)
                    {
                        a[i][j]=-1;
                        sm++;
                        //printf("%d %d %d\n",i,j,a[i][j]);
                    }
                }
    }
    
    //放目标
    while(smx<boxs)
    {
        for(int i=1;i<n-1&&smx<boxs;i++)
            for(int j=1;j<n-1&&smx<boxs;j++)
                if(v[a[i][j]]&&v[a[i-1][j]]&&v[a[i+1][j]]&&v[a[i][j-1]]&&v[a[i][j+1]]&&a[i][j]!=-1&&a[i][j]!=-2)
                {
                    if(ran(100)<bili)
                    {
                        a[i][j]=-3;
                        smx++;
                    }
                }
    }
    
    nx=n/2,ny=n/2;
    for(int i=0;i<n;i++)
        for(int j=0;j<n;j++)
            ya[i][j]=a[i][j];
}

void prin()//可视化地图
{
    // for(int i=0;i<n;i++)
    // {
    //     for(int j=0;j<n;j++)
    //     {
    //         if(a[i][j]==-3)
    //             printf("x");
    //         else if(a[i][j]==-2)
    //             printf("p");
    //         else if(a[i][j]==-1)
    //             printf("b");
    //         else if(!v[a[i][j]])
    //             printf("#");
    //         else
    //             printf(".");
    //     }
    //     printf("\n");
    // }
    // printf("\n");
}

void prin2() {
    printf("gift:\n");
    for(int i=0;i<n;i++)
    {
        for(int j=0;j<n;j++)
        {
            printf("%d ", a[i][j]);
        }
    }
//   //  hexDump(a, sizeof(a));
    printf("\n");
}

void error1()
{
    printf("fail!\n");
    exit(0);
}

void error2()
{
    printf("fail\n");
    exit(0);
}

void error3()
{
    printf("fail\n");
    exit(0);
}

void error4()
{
    printf("fail\n");
    exit(0);
}

void succ()
{
    printf("fail\n");
    exit(0);
}

int challenge()
{
    static int cccc = 0;
    srand(0);
    srand((unsigned int)time(0) + cccc);
    cccc += rand();
    init1();
    oula();
    n = 20;
    boxs = 4;
    // n = 8;
    // boxs = 1;
    init();
    prin2();
    prin();
    printf("Tell me sol:");
    for(int i=1;i<=len;i++)
    {
        char c = getchar();
        //printf("ch: %d", c);
        if (c == '\n')
            continue;
        if(c!='w'&&c!='s'&&c!='a'&&c!='d'&&c!='0')
            error1();
        if(c=='0')
            error4();
        if(a[nx+dx[ha[c]]][ny+dy[ha[c]]]==-1)
        {
            if(a[nx+dx[ha[c]]+dx[ha[c]]][ny+dy[ha[c]]+dy[ha[c]]]==-3)
            {
                ans++;
                a[nx+dx[ha[c]]+dx[ha[c]]][ny+dy[ha[c]]+dy[ha[c]]]=-1;
                a[nx+dx[ha[c]]][ny+dy[ha[c]]]=-2;
                a[nx][ny]=ya[nx][ny];
                nx+=dx[ha[c]],ny+=dy[ha[c]];
            }
            else if(!v[a[nx+dx[ha[c]]+dx[ha[c]]][ny+dy[ha[c]]+dy[ha[c]]]])
            {
                printf("!");
                error2();
            }
            else if(ya[nx+dx[ha[c]]][ny+dy[ha[c]]]==-3)
            {
                ans--;
                a[nx+dx[ha[c]]+dx[ha[c]]][ny+dy[ha[c]]+dy[ha[c]]]=-1;
                a[nx+dx[ha[c]]][ny+dy[ha[c]]]=-2;
                a[nx][ny]=ya[nx][ny];
                nx+=dx[ha[c]],ny+=dy[ha[c]];
            }
            else
            {
                a[nx+dx[ha[c]]+dx[ha[c]]][ny+dy[ha[c]]+dy[ha[c]]]=-1;
                a[nx+dx[ha[c]]][ny+dy[ha[c]]]=-2;
                a[nx][ny]=ya[nx][ny];
                nx+=dx[ha[c]],ny+=dy[ha[c]];
            }
        }
        else if(v[a[nx+dx[ha[c]]][ny+dy[ha[c]]]])
        {
            a[nx+dx[ha[c]]][ny+dy[ha[c]]]=-2;
            a[nx][ny]=randhe();
            nx+=dx[ha[c]],ny+=dy[ha[c]];
        }
        else if(!v[a[nx+dx[ha[c]]][ny+dy[ha[c]]]])
            error2();
        if(ans==sm)
            return 1;
        prin();
    }
    error3();
    return 0;
}

int main() {
    setvbuf(stdin, 0LL, 2, 0LL);
    setvbuf(stdout, 0LL, 2, 0LL);
    setvbuf(stderr, 0LL, 2, 0LL);
    alarm(30);

    printf("play game! 5 times, you will get flag!\n");
    for(int i = 0; i < 5; i++) {
        printf("Ready?(Y/n):");
        char ch;
        do {
            ch = getchar();
        }while(ch == '\n');
        if( ch != 'Y') {
            printf("bye\n");
            exit(0);
        }
        if(challenge() == 0) {
            printf("bye!");
        }
        printf("Yeah Continue!\n");
    }
    system("cat flag");
}