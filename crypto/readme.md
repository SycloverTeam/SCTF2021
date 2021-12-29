> 出了几个水题，师傅们轻喷。。。

[toc]



## ciruit map

这个题用到了乱码电路的概念

该系统中利用一个简单的置换密码来实现了一个 baby Garbled circuit 

### background

乱码电路是一种启用两方安全计算的加密协议，在该协议中，两个不信任方可以在不存在可信第三方的情况下通过其私有输入共同评估函数。在乱码电路协议中，必须将该功能描述为布尔电路。

### 电路生成/分析

分析circuit map可以得到以下电路

由4个输入端 1,2,3,4和导线5,6,7,以及一个输出端9组成

![](https://gitee.com/ljahum/images/raw/master/img/20211005164429.png)

由hint可知 输入端7 为 TRUE 和输入端4为FALSE时,输出端9的语义结果对应TRUE

这符合XOR门半加的特性

此时由AND门的特性可知输入端 1 2 3 4 均为TRUE

### 乱码生成

这一步对布尔电路进行加密，得到一个乱码电路(Garbled_table)

为电路中的每条电线分配两个随机生成的字符串，称为标签：一个用于布尔语义 FALSE，一个用于 TRUE

```python
    for wireidx in wires:
        # the index of keys[wireidx] 1 and 0 means TRUE and FALSE in garbled circuit
        keys[wireidx] = (randrange(0, 2**24),randrange(0, 2**24))
    return keys
```

在每一个门中对语义标签的运算如下

```python
def garble_label(key0, key1, key2):
    """
    key0, key1 = two input labels
    key2 = output label
    """
    gl = encrypt(key2, key0, key1)
    validation = encrypt(0, key0, key1)
    return (gl, validation)
```

对每一个门，可以看做

![](https://gitee.com/ljahum/images/raw/master/img/20211005164600.png)

注意输入端的左右顺序不同对结果也是有影响的，这关系到后面算出的标签放在true位还是false位

### analysis

我们注意到的第一件事是密钥大小只有 24 位。我们可以轻松地对密钥进行暴力破解

但加密使用了两个密钥，这意味着我们实际上需要对 48 位进行暴力破解，这是我无法接受的(有超算除外)

观察 garble_label 运算
```python
def garble_label(key0, key1, key2):
    """
    key0, key1 = two input labels
    key2 = output label
    """
    gl = encrypt(key2, key0, key1)
    validation = encrypt(0, key0, key1)
    return (gl, validation)
def encrypt(data, key1, key2):
    encrypted = encrypt_data(data, key1)
    encrypted = encrypt_data(encrypted, key2)
    return encrypted
```
可以发现

$val=E(E(0,k2),k1)$

有

$tmp = E(0,k2)$

$tmp = D(val,k1)$

利用**中间相遇**的思想优先计算中值tmp对应的k2然后再去找满足条件的k1,经过测试,这个复杂度$(2\times 2^{24})$在CTF环境是可以被接受的

完成了possible key的寻找后，根据g_table值的性质还有AND们得性质来寻找标签keys

AND门:

当拿到一对key1 key2满足均为false时,可以通过评估电路测试的另一个key2必定为key2的语义真值(key20不等于recover_key2)

| 对应key1 | key20 | recover_key2 | ret  |
| -------- | ----- | ------------ | ---- |
| 0        | 0     |              | 0    |
| 0        |       | 1            | 0    |
| 或者key1 | key20 | recover_key2 | ret  |
| 0        | 1     |              | 0    |
| 0        |       | 0            | 0    |

由此可以找到每一个AND门输入端的语义真值和语义假值

在获得输入端key后根据XOR门和AND门的特性恢复出剩下的key

```python
keys = {1: (8343801, 13675268),
        2: (10251687, 12870274),
        3: (6827786, 12490757),
        4: (2096572, 3391233),
        5: (0, 0),
        6: (0, 0),
        7: (0, 0),
        9: (0, 0)}
# 5,6,7-> use AND gate
for gate in circuit["gates"]:
    gate_ID = gate["id"]
    # Right/Left_value_index
    rv = gate["in"][0]
    lv = gate["in"][1]
    
    if(gate["type"]=="AND"):
        """
        AND gate
        1 1 1
        1 0 0
        0 1 0
        0 0 0 
        """ 
        msg1 = validate_the_circuit(G_Table[gate_ID],keys[rv][1],keys[lv][1])
        msg0 = validate_the_circuit(G_Table[gate_ID],keys[rv][0],keys[lv][0])
    else:
        """
        XOR gate
        1 1 0
        1 0 1
        0 1 1
        0 0 0 
        """ 
        msg1 = validate_the_circuit(G_Table[gate_ID],keys[rv][1],keys[lv][0])
        msg0 = validate_the_circuit(G_Table[gate_ID],keys[rv][0],keys[lv][0])
    keys[gate_ID] = (msg0,msg1)
```

整个程序使用pypy运行可以将耗时控制在20min以内

### refer

https://en.wikipedia.org/wiki/Yao%27s_Millionaires%27_problem

`SCTF{#@DE-is-not-EZ@#}`








## cubic

共模 小d有350位,构造一个格子可以求出来$\phi(n)$，然后分解n，

用到的群：https://eprint.iacr.org/2021/1160.pdf，构造出对应$\phi(n)$,后面的流程就和rsa一样了



```python
#! /usr/bin/sage
from icecream import *
from pwn import *
from sage.all import *
from Crypto.Util.number import long_to_bytes
from libnum import invmod
from rich.traceback import install
import random

install()

import re
# -----------------------------------


def b2s(s):
    if(type(s)==str):
        return s
    else:
        return s.decode()
def CatNum(txt):
    txt = b2s(txt)
    matchObj = re.findall(r'[0-9]+', txt)
    return matchObj

def add(P, Q, mod):
    m, n = P
    p, q = Q

    if p is None:
        return P
    if m is None:
        return Q

    if n is None and q is None:
        x = m * p % mod
        y = (m + p) % mod
        return (x, y)

    if n is None and q is not None:
        m, n, p, q = p, q, m, n

    if q is None:
        if (n + p) % mod != 0:
            x = (m * p + 2) *invmod(n + p, mod) % mod
            y = (m + n * p) *invmod(n + p, mod) % mod
            return (x, y)
        elif (m - n ** 2) % mod != 0:
            x = (m * p + 2) *invmod(m - n ** 2, mod) % mod
            return (x, None)
        else:
            return (None, None)
    else:
        if (m + p + n * q) % mod != 0:
            x = (m * p + (n + q) * 2) *invmod(m + p + n * q, mod) % mod
            y = (n * p + m * q + 2) *invmod(m + p + n * q, mod) % mod
            return (x, y)
        elif (n * p + m * q + 2) % mod != 0:
            x = (m * p + (n + q) * 2) *invmod(n * p + m * q + 2, mod) % mod
            return (x, None)
        else:
            return (None, None)


def myPower(P, a, mod):
    
    res = (None, None)
    t = P
    while a > 0:
        if a % 2:
            res = add(res, t, mod)
        t = add(t, t, mod)
        a >>= 1
    return res

def divide_pq(e, d, n):
    k = e*d - 1
    while True:
        g = random.randint(2, n-1)
        t = k
        while True:
            if t % 2 != 0:
                break
            t //= 2
            x = pow(g, t, n)
            if x > 1 and gcd(x-1, n) > 1:
                p = int(gcd(x-1, n))
                return p, n//p
def getflag(e1,e2,N,r,c):
    # e1= 767157345110333120765215917405799114481606786819730013331218482715693974580372479745803010105698034967228434209402621442585032068414326539790465219869935194801454980119076341375989907619124605041375288948405591085582984218664195601364431818138768463516070993085129666653028608837283755081729172340185469312642915276996557223874809437727394681549138588054635447315527162846673931683806612043204285238604064083208135568479006384238162461398859978485658905575658831632236322811134146516290930931924072956144444414970682803505199019499852265669359145966923690148991465161612623676716510163913344343944946719069070427581 
    # N= 14592718596409961052155280078101857413625131283065195654251607816041905094077468255632484169056386347858935092091107812347013936961244830953290640725032815170305906625413918037617790241183697985128975766734356522274406781601459062790457184055767518999736839976379960282044414916332297554836357500811948673060046516692141021813748388570291404653736002798982222633162683030343800670671835170182656891888936101228004757222164723403750954406986520193494119942871644936143879611485043533912819499438960901502413222351764875164179533032452606422174094195951877754416864007588726950404284857470385874399162409188086058828937
    # e2=1383020076975833630498738959564811786767168598420273921181652495656917886382946230043901356778803463487075518231315434600975679739496038331493883962090705603836755686724745206984366372318115495356519173585622684223663258403055430058437316847677868712827858534965640331512251115085155491381508714175755430419381586779274387389188876088972710170881717308941847239043191080611939905502649936775182468174727833571229730111088210734276928177076621830269980689344049231490733624322824446383901933303177227405107368466864098986599511735080119755402332162930692875304464788123864480990498801490900759080550564567419340803847
    # r = 112538997432941694803570881299924418871425461567782222794081548467891263029029636765888009332091919378678909971880752971143963673917592185145417537839685778387963039213525590766501430247356670406639347348032920735219037062331389621090171176603527761597193374819715457546560107809133412307350326026175287297297
    # c=  (1472181964181591876203688838443614661079740864502446103130786526256279553585938670167454351837157193541739285780976997691999868091070396156021333889830218485989471478889835120400040803502335578222157578786573082409117936457555169379474524606851140735730243037839218940650756043986997772648354214144209505540717564826936314005234823736582082330782485485334505994950229176973180834996068962772713829425022929579254450972466037809221576080853686898662404535441467675440001393538499848469848475117679410626933769035489560105002584055724566023992145792265830396016889746795435828826428994258649610950666971718032126286563993144759670231570039361398473935827830789864015069331583574667347516266211752590562291654758155676565434691144240236344507787833445082346539094812631174888508899268228744379861615704557500820159804865558093677746182737998681273785148194147662787655348418402963644559632419820372176870751059330165502138374013, 656239427697165387417379504093771191074785031831545811708160679050939343266036885865767336072010345067887724618678256326379894175952176366166500959467203643526092339184606804378198845486497998802491954404524302319130427388490144782057132374686933725313820018260855935077123732989595715005826998659312929179523830043133765745838228912881597188198880995704016552161354128308084461602783087886943380268652205393826194015442216272486562544062642784820291712974386975685980898459058993314004423280050103133614864097852821547984068663052695430135364061877780963866019898650578458168421497370772396424781520174385202059822501482691905551226852570459430245379630202041266092843743772453075880197582970986135566799488319937601900898568520920162513214898144001948580574803662011568000582391257714187023765854850115586247107650884066945492746656028197247733875495310004792757050921945569521519957222214540892180360885566069579419907367)

    B = Matrix([
        [1, -N,   0,   N^2],
        [0, e1, -e1, -e1*N],
        [0,  0,  e2, -e2*N],
        [0,  0,   0, e1*e2]
    ])

    x = 0.355

    D = Matrix([
        [N,            0,            0,  0],
        [0, int(N^(1/2)),            0,  0],
        [0,            0, int(N^(1+x)),  0],
        [0,            0,            0,  1]

    ])

    res = B*D
    lll = res.LLL()
    y =  lll[0]
    inv = res.inverse()
    x = y*inv
    phi = (e1*(x[1]))//x[0]
    phi = int(phi)

    bezout = xgcd(e1, phi)
    d1 = Integer(mod(bezout[1], phi))
    # print(d1)
    e1= int(e1 )
    e2= int(e2)
    N= int(N)
    d1 = int(d1)
    p ,q = divide_pq(e1,d1,N)
    N = p*q*r
    phi = (p**2+p+1)*(q**2+q+1)*(r**2+r+1)
    if(gcd(e2,phi)==1):
        d = invmod(e2,phi)
        print('start pow')
        m = myPower(c,d,N)
        m = [long_to_bytes(i) for i in m]
        print(b''.join(m))
        return true
    else:
        return false

for i in range(10):
    io = remote('123.60.153.41',7002)

    io.sendafter('>','1\n')
    io.recvline()
    io.recvuntil('e:')

    e1 =  int(io.recvuntil('N:')[:-2])
    N =  int(io.recvuntil('\n'))
    io.sendafter('>','2\n')
    io.recvline()
    io.recvuntil('e:')

    e2 =  int(io.recvuntil('N:')[:-2])
    io.recvline()
    # =================================
    io.sendafter('>','3\n')
    io.recvline()
    buf = io.recvuntil('c you next time')
    data = CatNum(buf)
    x,y,pad = data

    c = (int(x),int(y))
    pad = int(pad)

    # print(e1,e2,N,pad,c)
    if(getflag(e1,e2,N,pad,c)==true):
        break
    else:
        print('failed')        
    io.close()
```

## ChristmasZone

二元copper可以解出p+q，从而分解 n,得到pq后用Complex number循环群的阶$(p^2-1)\cdot(q^2-1)$解一个rsa变体

用给出的4个方程把a，b，x三个变量，与vs代入方程，利用Groebner Basis求解出a，b

之后直接模p上求解单元方程

```python
#! /usr/bin/sage

from sage.all import *
from sage.groups.generic import bsgs
from Crypto.Util.number import *
from Crypto.Util.number import long_to_bytes
from sage.all import *
from Crypto.Util.number import *
import itertools
from Crypto.Util.number import long_to_bytes
from icecream import *
import gmpy2
from tqdm import tqdm
from rich.progress import track
from rich.traceback import install
install()

val=(34204655731647168488867648023743233202853353385423821020123013922337946150517068728088345046828240759125584860323544414123058890094862166685911736755763698037018050872262863775535941006755265629614836703072634806693353324024207015844011678057140494045663151442658095266545364513542209941243110790433376281462, 16858509746188498645994612793813325903235946006745635188906012649640394139914132762595904725617366752162117244323613906070400188097779007353580997131209081559117885929394968926206974945208635485132618506119436577421644512976425908069931192985654360429737648075567577953013239739379805891137295589381122428805, 142314290874103472342157791957387494910425619448741462534558029316959743033784878091885625427304968819761626275428497199675623519674102956411545725046448881362142100460681446306917887384147493522993703912450996684140594958479900541435636945305290188063337518337447204173177112776360023075679738966411203835703)
gift=13146292900969145912011070625936819556218067595021694542068631184072749092028768693068952505415238429120636049123342361462754478473122907110846212099001064372504307406418078350469186353000578205666049588496984550131531012299432748760443937176775790106450689313268294822420619293511621766335595109158980995115616382051960359082115678701088054347812139158169666661183575876009077616481631690804500104980112126368457619408425822555194440810454669146569909618489762437072323068652326761926857145138872528481413079646502713125626941804859406071829421319628500168706551072692956250315369557055229020553940819220767648492419
re,im,n= val



def small_roots(f, bounds, m=1, d=None):
	if not d:
		d = f.degree()

	R = f.base_ring()
	N = R.cardinality()
	
	f /= f.coefficients().pop(0)
	f = f.change_ring(ZZ)

	G = Sequence([], f.parent())
	for i in range(m+1):
		base = N^(m-i) * f^i
		for shifts in itertools.product(range(d), repeat=f.nvariables()):
			g = base * prod(map(power, f.variables(), shifts))
			G.append(g)

	B, monomials = G.coefficient_matrix()
	monomials = vector(monomials)

	factors = [monomial(*bounds) for monomial in monomials]
	for i, factor in enumerate(factors):
		B.rescale_col(i, factor)

	B = B.dense_matrix().LLL()

	B = B.change_ring(QQ)
	for i, factor in enumerate(factors):
		B.rescale_col(i, 1/factor)

	H = Sequence([], f.parent().change_ring(QQ))
	for h in filter(None, B*monomials):
		H.append(h)
		I = H.ideal()
		if I.dimension() == -1:
			H.pop()
		elif I.dimension() == 0:
			roots = []
			for root in I.variety(ring=ZZ):
				root = tuple(R(root[var]) for var in f.variables())
				roots.append(root)
			return roots
	return []

def add(P1,P2):
    x1,y1=P1
    x2,y2=P2
    x3=(x1*x2-y1*y2)%n
    y3=(x1*y2+x2*y1)%n
    return (x3,y3)

def mul(P,k):
    assert k>=0
    Q=(1,0)
    while k>0:
        if k%2:
            k-=1
            Q=add(P,Q)
        else:
            k//=2
            P=add(P,P)
    return Q


N= int(n)
e= int(gift)


R = Integers(e)
PR.<p_q, k> = PolynomialRing(R)
f = k * (N**2 + N*p_q + p_q**2 - N + p_q + 1) + 1
bounds = (2**513, 2**400)
print("strating LLL")
p_q, k = small_roots(f, bounds, m=3, d=4)[0]

print(p_q,k)
PR.<x> = PolynomialRing(ZZ)
f = x**2 - int(p_q) * x + N
(p, _), (q, _) = f.roots()
print(f'p={p}')
print(f'q={q}')
n = p*q
e = 0x10001
C=(re, im)
phi = (p**2-1)*(q**2-1)
d = gmpy2.invert(e, phi) 
M = mul(C,d) 
m1 = M[0]
m2 = M[1]
ans = long_to_bytes(m1)+long_to_bytes(m2)
print(ans)

'''
strating LLL
23860514682185861814605135299851729132039414052288696783041684557772943137476012454755412276081907673557129139549567334025046148754321219133652582236882696 952745963812659210109023124542441923017026026653857653050764529216637961231327302263329674556906022732697138469390293996
p=12059676623266404644103423515202796736992767179853466558422471837438521983828323525477329865339777607331528073491807861929135889773752694489737384356307049
q=11800838058919457170501711784648932395046646872435230224619212720334421153647688929278082410742130066225601066057759472095910258980568524643915197880575647
b'SCTF{winerwienerCKdinner}'
'''
```

