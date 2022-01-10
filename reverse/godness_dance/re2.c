#include<stdio.h>
#include<stdlib.h>
#include<string.h>
int n=28,wa[2005],wb[2005],wv[2005],wsu[2005],sa[2005],rk[2005],sm[2005];
int re[2005]={1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1};
int ta[2005]={0,2,26,17,28,24,11,21,10,16,20,19,18,3,8,6,12,9,14,13,22,4,27,15,23,1,25,7,5};
void error1()
{
    printf("Count wrong!");
    exit(0);
}
void error2()
{
    printf("Wrong!");
    exit(0);
}
int cmp(int r[],int a,int b,int l)
{
	return r[a]==r[b]&&r[a+l]==r[b+l];
}
void saa(char r[],int n,int m)
{
	int *x=wa,*y=wb;
	for(int i=0;i<=m;i++)
		wsu[i]=0;
	for(int i=1;i<=n;i++)
		wsu[x[i]=r[i]]++;
	for(int i=1;i<=m;i++)
		wsu[i]+=wsu[i-1];
	for(int i=n;i>=1;i--)
		sa[wsu[x[i]]--]=i;
	for(int j=1,p=1;j<n&&p<n;j<<=1,m=p)
	{
		p=0;
		for(int i=n-j+1;i<=n;i++)
			y[++p]=i;
		for(int i=1;i<=n;i++)
			if(sa[i]>j)
				y[++p]=sa[i]-j;
		for(int i=1;i<=n;i++)
			wv[i]=x[y[i]];
		for(int i=0;i<=m;i++)
			wsu[i]=0;
		for(int i=1;i<=n;i++)
			wsu[wv[i]]++;
		for(int i=1;i<=m;i++)
			wsu[i]+=wsu[i-1];
		for(int i=n;i>=1;i--)
			sa[wsu[wv[i]]--]=y[i];
        int *tmp=x;
        x=y;
        y=tmp;
		// swap(x,y);
		p=1;
		x[sa[1]]=1;
		for(int i=2;i<=n;i++)
			x[sa[i]]=cmp(y,sa[i-1],sa[i],j)?p:++p;
	}
	for(int i=1;i<=n;i++)
		rk[sa[i]]=i;
}
int main()
{
    char s[2005];
    printf("Input:");
    for(int i=1;i<=28;i++)
        scanf("%c",&s[i]);
    for(int i=1;i<=n;i++)
        sm[s[i]-'a']++;
    for(int i=0;i<26;i++)
        if(sm[i]!=re[i])
            error1();
    saa(s,28,200);
    for(int i=1;i<=28;i++)
	{
        if(sa[i]!=ta[i])
		{
			 error2();
		}
	}
    printf("Good for you!\nflag:SCTF{");
    for(int i=1;i<=28;i++)
        printf("%c",s[i]);
    printf("}");
    return 0;
}
// waltznymphforquickjigsvexbud
// waltznymphforquickjigsvexbu1
