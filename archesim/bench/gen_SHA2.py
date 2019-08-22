import json
SHA2_K = [0 for i in range(80)]

def right_rot(value, count):

    return (value >> count | value << (64-count))

def Rotate(c, fp):
    # Used for bit shifting
    # Rotate(0, fp) signifies no bit shifting
    t = (63 + c) % 64

    for i in range(64):
        if (t < 0):
            t += 64

        fp.write("1 %d " % t)
        t = t - 1

    fp.write("\n\n")


def PIR_RoundConstants(fp2, cyc, i):

    # Contains Round constants Ki

    k = [
        0x428a2f98d728ae22, 0x7137449123ef65cd, 0xb5c0fbcfec4d3b2f,
        0xe9b5dba58189dbbc, 0x3956c25bf348b538, 0x59f111f1b605d019,
        0x923f82a4af194f9b, 0xab1c5ed5da6d8118, 0xd807aa98a3030242,
        0x12835b0145706fbe, 0x243185be4ee4b28c, 0x550c7dc3d5ffb4e2,
        0x72be5d74f27b896f, 0x80deb1fe3b1696b1, 0x9bdc06a725c71235,
        0xc19bf174cf692694, 0xe49b69c19ef14ad2, 0xefbe4786384f25e3,
        0x0fc19dc68b8cd5b5, 0x240ca1cc77ac9c65, 0x2de92c6f592b0275,
        0x4a7484aa6ea6e483, 0x5cb0a9dcbd41fbd4, 0x76f988da831153b5,
        0x983e5152ee66dfab, 0xa831c66d2db43210, 0xb00327c898fb213f,
        0xbf597fc7beef0ee4, 0xc6e00bf33da88fc2, 0xd5a79147930aa725,
        0x06ca6351e003826f, 0x142929670a0e6e70, 0x27b70a8546d22ffc,
        0x2e1b21385c26c926, 0x4d2c6dfc5ac42aed, 0x53380d139d95b3df,
        0x650a73548baf63de, 0x766a0abb3c77b2a8, 0x81c2c92e47edaee6,
        0x92722c851482353b, 0xa2bfe8a14cf10364, 0xa81a664bbc423001,
        0xc24b8b70d0f89791, 0xc76c51a30654be30, 0xd192e819d6ef5218,
        0xd69906245565a910, 0xf40e35855771202a, 0x106aa07032bbd1b8,
        0x19a4c116b8d2d0c8, 0x1e376c085141ab53, 0x2748774cdf8eeb99,
        0x34b0bcb5e19b48a8, 0x391c0cb3c5c95a63, 0x4ed8aa4ae3418acb,
        0x5b9cca4f7763e373, 0x682e6ff3d6b2b8a3, 0x748f82ee5defb2fc,
        0x78a5636f43172f60, 0x84c87814a1f0ab72, 0x8cc702081a6439ec,
        0x90befffa23631e28, 0xa4506cebde82bde9, 0xbef9a3f7b2c67915,
        0xc67178f2e372532b, 0xca273eceea26619c, 0xd186b8c721c0c207,
        0xeada7dd6cde0eb1e, 0xf57d4f7fee6ed178, 0x06f067aa72176fba,
        0x0a637dc5a2c898a6, 0x113f9804bef90dae, 0x1b710b35131c471b,
        0x28db77f523047d84, 0x32caab7b40c72493, 0x3c9ebe0a15c9bebc,
        0x431d67c49c100d4c, 0x4cc5d4becb3e42b6, 0x597f299cfc657e2a,
        0x5fcb6fab3ad6faec, 0x6c44198c4a475817
    ]

    fp2.write("%d " % cyc)
    for c in range(63, -1, -1):
        h = (k[i]) >> c
        if (h & 1):
            fp2.write("1")
        else:
            fp2.write("0")
    fp2.write("\n\n")


def PIR_Words(fp2, cyc, i):

    global SHA2_K

    fp2.write("%d " % cyc)
    for c in range(63, -1, -1):
        h = (SHA2_K[i]) >> c
        if (h & 1):
            fp2.write("1")
        else:
            fp2.write("0")

    fp2.write("\n\n")


def Calculate_carrybits(fp, fp2, cyc, m2, m1):

    initial = cyc

    fp.write("Read %d\n\n"% m2)
    cyc = cyc + 1

    fp.write("Apply %d 1 00 000000 "% m2)
    cyc = cyc + 1  # Calculates and stores c1 in bit 63 (leftmost bit is labelled 0)
    for i in range(64):
        if (i == 63):
            fp.write("1 32 ")
        elif (31 - i >= 0):
            fp.write("0 %d " % (31 - i))
        else:
            fp.write("0 %d " % (64 + 31 - i))

    fp.write("\n\n")

    for i in range(1, 32):

        fp.write("Read %d\n\n"% m2)
        cyc = cyc + 1
        fp.write("Apply %d 1 11 %d "% (m2, 64 - i))
        cyc = cyc + 1  # Calculates ci and stores in bit 63-i
        for j in range(64):
            if (j == 63 - i):
                fp.write("1 %d "% (32 + i))
            elif (31 - j >= 0):  # TODO : check
                fp.write("0 %d "% (31 - j))
            else:
                fp.write("0 %d "% (64 + 31 - j))
        fp.write("\n\n")

    # Reset left half of line m2
    # PIR Loads string of 1's

    fp.write("Apply %d 0 00 000000 "% m2)
    cyc = cyc + 1
    for i in range(64):
        if (63 - i >= 32):
            fp.write("1 %d "% (63 - i))
        else:
            fp.write("0 %d "% (63 - i))

    fp.write("\n\n")

    fp2.write("%d "% cyc)
    for i in range(64):
        fp2.write("1")
    fp2.write("\n\n")

    fp.write("Read %d\n\n"% m2)
    cyc = cyc + 1  # Read c32

    fp.write("Apply %d 1 01 000000 "% m2)
    cyc = cyc + 1  # Copy ~c32 to immediate left
    for i in range(64):
        if (62 - i == 31):
            fp.write("1 31 ")
        elif (62 - i >= 0):
            fp.write("0 %d "% (62 - i))
        else:
            fp.write("0 %d "% (62 - i + 63))

    fp.write("\n\n")

    fp.write("Read %d\n\n"% m2)
    cyc = cyc + 1  # Read ~c31

    fp.write("Apply %d 1 01 000000 "% m1)
    cyc = cyc + 1  # Copy c31 to the corresponding position in m1
    for i in range(64):
        if (64 + 0 - i == 32):
            fp.write("1 32 ")
        elif (0 - i >= 0):
            fp.write("0 %d "% (0 - i))
        else:
            fp.write("0 %d "% (0 - i + 64))

    fp.write("\n\n")

    # Calculate remaining carry bits

    fp.write("Read %d\n\n"% m1)
    cyc = cyc + 1

    fp.write("Apply %d 1 11 32 "% m1)
    cyc = cyc + 1  # Calculates and stores c1 in bit 63 (leftmost bit is labelled 0)
    for i in range(64):
        if (i == 63):
            fp.write("1 32 ")
        elif (31 - i >= 0):
            fp.write("0 %d "% (31 - i))
        else:
            fp.write("0 %d "% (64 + 31 - i))

    fp.write("\n\n")

    for i in range(1, 31):  # Does not compute c64

        fp.write("Read %d\n\n"% m1)
        cyc = cyc + 1
        fp.write("Apply %d 1 11 %d "% (m1, 64 - i))
        cyc = cyc + 1  # Calculates ci and stores in bit 63-i
        for j in range(64):
            if (j == 63 - i):
                fp.write("1 %d "% (32 + i))
            elif (31 - j >= 0):
                fp.write("0 %d "% (31 - j))
            else:
                fp.write("0 %d "% (64 + 31 - j))

        fp.write("\n\n")

    # Reset ~c32 in m2
    # PIR Loads string of 1's
    fp.write("Apply %d 0 00 000000 "% m2)
    cyc = cyc + 1
    for i in range(64):
        if (63 - i >= 32):
            fp.write("1 %d "% (63 - i))
        else:
            fp.write("0 %d "% (63 - i))

    fp.write("\n\n")

    fp2.write("%d "% cyc)
    for i in range(64):
        fp2.write("1")
    fp2.write("\n\n")

    # Reset left half of m1
    # PIR Loads string of 1's
    fp.write("Apply %d 0 00 000000 "% m1)
    cyc = cyc + 1
    for i in range(64):
        if (63 - i >= 32):
            fp.write("1 %d "% (63 - i))
        else:
            fp.write("0 %d "% (63 - i))

    fp.write("\n\n")

    fp2.write("%d "% cyc)
    for i in range(64):
        fp2.write("1")
    fp2.write("\n\n")

    # Copy c33 c34 ... c63 to m1 in inverted form

    #print(cyc - initial)
    #stopbar = input()

    fp.write("Read %d\n\n"% m1)
    cyc = cyc + 1

    fp.write("Apply %d 1 01 000000 "% m1)
    cyc = cyc + 1
    for i in range(64):
        if (31 - i >= 0):
            if (31 - i == 31):
                fp.write("0 %d "% (31 - i))
            else:
                fp.write("1 %d "% (31 - i))

        else:
            fp.write("0 %d "% (31 - i + 64))

    fp.write("\n\n")

    fp.write("Read %d\n\n"% m1)
    cyc = cyc + 1  # Read ~c63 ~c62 ... ~c33

    fp.write("Apply %d 1 01 000000 "% m2)
    cyc = cyc + 1  # Copy c63 c62 ... c33 to m2
    for i in range(64):
        if (63 - i == 63):
            fp.write("0 %d "% (63 - i))
        elif (63 - i >= 32):
            fp.write("1 %d "% (63 - i))
        else:
            fp.write("0 %d "% (63 - i))

    fp.write("\n\n")

    # Reset m1
    # PIR Loads string of 1's
    fp.write("Apply %d 0 00 000000 "% m1)
    cyc = cyc + 1
    Rotate(0, fp)

    fp2.write("%d "% cyc)
    for i in range(64):
        fp2.write("1")
    fp2.write("\n\n")


    return cyc

def Load(fp, fp2, cyc):

    h = [
        0x6a09e667f3bcc908, 0xbb67ae8584caa73b, 0x3c6ef372fe94f82b,
        0xa54ff53a5f1d36f1, 0x510e527fade682d1, 0x9b05688c2b3e6c1f,
        0x1f83d9abfb41bd6b, 0x5be0cd19137e2179
    ]

    m = 0xffffffffffffffff

    fp.write(
        "//The following code loads the initial states to the SHA-2 State partition in inverted form\n\n"
    )

    for i in range(8):

        fp.write("Apply %d 0 01 000000 "% i)
        cyc = cyc + 1
        Rotate(0, fp)

        fp2.write("%d "% cyc)
        for c in range(63, -1, -1):
            k = (h[i]) >> c
            if (k & 1):
                fp2.write("1")
            else:
                fp2.write("0")

        fp2.write("\n\n")

    return cyc

def Ch_EFG(fp, fp2, cyc, tar, mem2,
           mem1):  # Computation memory has NOT BEEN PREVIOUSLY CLEARED
    # Leaves WordLine tar occupied

    fp.write(
        "//The following code computes Ch(E,F,G) and stores it in wl %d\n\n"%
        tar)

    fp.write("Read 4\n\n")
    cyc = cyc + 1  # Read ~e

    fp.write("Apply %d 1 01 000000 "% tar)
    cyc = cyc + 1  # Store e in wl 9, 10
    Rotate(0, fp)
    fp.write("Apply %d 1 01 000000 "% mem2)
    cyc = cyc + 1
    Rotate(0, fp)

    fp.write("Read %d\n\n"% mem2)
    cyc = cyc + 1  # Read e

    fp.write("Apply %d 1 01 000000 "% mem1)
    cyc = cyc + 1  # Store ~e in wl 8
    Rotate(0, fp)

    fp.write("Read 5\n\n")
    cyc = cyc + 1  # Read ~f

    fp.write("Apply %d 1 00 000000 "% tar)
    cyc = cyc + 1  # e.f
    Rotate(0, fp)
    fp.write("Apply %d 1 00 000000 "% mem2)
    cyc = cyc + 1  # e.f
    Rotate(0, fp)

    fp.write("Read 6\n\n")
    cyc = cyc + 1  # Read ~g

    fp.write("Apply %d 1 00 000000 "% mem1)
    cyc = cyc + 1  # ~e.g
    Rotate(0, fp)

    fp.write("Read %d\n\n"% mem1)
    cyc = cyc + 1  # Read ~e.g

    fp.write("Apply %d 1 00 000000 "% tar)
    cyc = cyc + 1  # e.f.~(~e.g)
    Rotate(0, fp)
    fp.write("Apply %d 1 01 000000 "% mem2)
    cyc = cyc + 1  # e.f + ~(~e.g)
    Rotate(0, fp)

    fp.write("Read %d\n\n"% mem2)
    cyc = cyc + 1  # Read ~e.f + ~(~e.g)

    fp.write("Apply %d 1 01 000000 "% tar)
    cyc = cyc + 1  # e.f XOR ~e.g
    Rotate(0, fp)

    # PIR Loads string of 1's
    fp.write("Apply %d 0 00 000000 "% mem2)
    cyc = cyc + 1  # RESET wl 8, 9
    Rotate(0, fp)

    fp2.write("%d "% cyc)
    for i in range(64):
        fp2.write("1")
    fp2.write("\n\n")

    fp.write("Apply %d 0 00 000000 "% mem1)
    cyc = cyc + 1
    Rotate(0, fp)

    fp2.write("%d "% cyc)
    for i in range(64):
        fp2.write("1")
    fp2.write("\n\n")

    return cyc



def Sigma1(fp, fp2, cyc, tar, mem2, mem1): # Computation memory NOT PREVIOUSLY CLEARED
    # Leaves wordline tar occupied

    fp.write( "//The following code computes Sigma1 and stores it in wl %d\n\n"% tar);

    fp.write( "Read 4\n\n"); 
    cyc = cyc+1 # Read ~e

    fp.write( "Apply %d 1 01 000000 "% tar); 
    cyc = cyc+1 # Write e14
    Rotate(14, fp);
    fp.write( "Apply %d 1 01 000000 "% mem2); 
    cyc = cyc+1 # Write e14
    Rotate(14, fp);
    fp.write( "Apply %d 1 01 000000 "% mem1); 
    cyc = cyc+1 # Write e14
    Rotate(14, fp);

    fp.write( "Read %d\n\n"% tar); 
    cyc = cyc+1 # Read e14

    fp.write( "Apply %d 1 00 000000 "% tar); 
    cyc = cyc+1  # e14.~e18
    Rotate(4, fp);
    fp.write( "Apply %d 1 00 000000 "% mem2); 
    cyc = cyc+1 # e14.~e18
    Rotate(4, fp);
    fp.write( "Apply %d 1 01 000000 "% mem1); 
    cyc = cyc+1 # e14 + ~e18
    Rotate(4, fp);

    fp.write( "Read %d\n\n"% mem1); 
    cyc = cyc+1  # Read e14 + ~e18

    fp.write( "Apply %d 1 01 000000 "% tar); 
    cyc = cyc+1  # e14 XOR e18
    Rotate(0, fp);
    fp.write( "Apply %d 1 01 000000 "% mem2); 
    cyc = cyc+1 # e14 XOR e18
    Rotate(0, fp);

    fp.write( "Apply %d 0 00 000000 "% mem1); 
    cyc = cyc+1 # Reset wl mem1
    Rotate(0, fp);

    fp.write( "Read 4\n\n"); 
    cyc = cyc+1                  # Read ~e

    fp.write( "Apply %d 1 01 000000 "% mem1); 
    cyc = cyc+1 # Store e41
    Rotate(41, fp);

    fp.write( "Read %d\n\n"% mem1); 
    cyc = cyc+1            # Read e41

    fp.write( "Apply %d 1 00 000000 "% tar); 
    cyc = cyc+1  # (e14 XOR e18).~e41
    Rotate(0, fp);
    fp.write( "Apply %d 1 01 000000 "% mem2); 
    cyc = cyc+1 # (e14 XOR e18) + ~e41
    Rotate(0, fp);

    fp.write( "Read %d\n\n"% mem2); 
    cyc = cyc+1            # Read (e14 XOR e18) + ~e41

    fp.write( "Apply %d 1 01 000000 "% tar); 
    cyc = cyc+1  # (e14 XOR e18) XOR e41
    Rotate(0, fp);

    # PIR Loads string of 1's
    fp.write( "Apply %d 0 00 000000 "% mem2); 
    cyc = cyc+1 # RESET wl mem1, mem2
    Rotate(0, fp);

    fp2.write("%d "% cyc);
    for i in range(64): 
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply %d 0 00 000000 "% mem1); 
    cyc = cyc+1 
    Rotate(0, fp);

    fp2.write("%d "% cyc);
    for i in range(64): 
        fp2.write("1");
    fp2.write("\n\n");

    return cyc;



def Sigma0(fp, fp2, cyc, tar, mem2, mem1): # Computation memory NOT PREVIOUSLY CLEARED
    # Leaves wordline tar occupied

    fp.write( "//The following code computes Sigma0 and stores it in wl %d\n\n"% tar);

    fp.write( "Read 0\n\n"); 
    cyc = cyc+1                  # Read ~a
 
    fp.write( "Apply %d 1 01 000000 "% tar); 
    cyc = cyc+1  # Write a28
    Rotate(28, fp);
    fp.write( "Apply %d 1 01 000000 "% mem2); 
    cyc = cyc+1 # Write a28
    Rotate(28, fp);
    fp.write( "Apply %d 1 01 000000 "% mem1); 
    cyc = cyc+1 # Write a28
    Rotate(28, fp);

    fp.write( "Read %d\n\n"% tar); 
    cyc = cyc+1            # Read a28

    fp.write( "Apply %d 1 00 000000 "% tar); 
    cyc = cyc+1  # a28.~a34
    Rotate(6, fp);
    fp.write( "Apply %d 1 00 000000 "% mem2); 
    cyc = cyc+1 # a28.~a34
    Rotate(6, fp);
    fp.write( "Apply %d 1 01 000000 "% mem1); 
    cyc = cyc+1 # a28 + ~a34
    Rotate(6, fp);

    fp.write( "Read %d\n\n"% mem1); 
    cyc = cyc+1            # Read a28 + ~a34

    fp.write( "Apply %d 1 01 000000 "% tar); 
    cyc = cyc+1  # a28 XOR a34
    Rotate(0, fp);
    fp.write( "Apply %d 1 01 000000 "% mem2); 
    cyc = cyc+1 # a28 XOR a34
    Rotate(0, fp);

    fp.write( "Apply %d 0 00 000000 "% mem1); 
    cyc = cyc+1 # Reset wl mem1
    Rotate(0, fp);

    fp.write( "Read 0\n\n"); 
    cyc = cyc+1                  # Read ~a

    fp.write( "Apply %d 1 01 000000 "% mem1); 
    cyc = cyc+1 # Store a39
    Rotate(39, fp);

    fp.write( "Read %d\n\n"% mem1); 
    cyc = cyc+1            # Read a39

    fp.write( "Apply %d 1 00 000000 "% tar); 
    cyc = cyc+1  # (a28 XOR a34).~a39
    Rotate(0, fp);
    fp.write( "Apply %d 1 01 000000 "% mem2); 
    cyc = cyc+1 # (a28 XOR a34) + ~a39
    Rotate(0, fp);

    fp.write( "Read %d\n\n"% mem2); 
    cyc = cyc+1            # Read (a28 XOR a34) + ~a39

    fp.write( "Apply %d 1 01 000000 "% tar); 
    cyc = cyc+1  # (a28 XOR a34) XOR a39
    Rotate(0, fp);

    # PIR Loads string of 1's
    fp.write( "Apply %d 0 00 000000 "% mem2); 
    cyc = cyc+1 # RESET wl mem1, mem2
    Rotate(0, fp);

    fp2.write("%d "% cyc);
    for i in range(64): 
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply %d 0 00 000000 "% mem1); 
    cyc = cyc+1 
    Rotate(0, fp);

    fp2.write("%d "% cyc);
    for i in range(64): 
        fp2.write("1");
    fp2.write("\n\n");

    return cyc;


def Maj(fp, fp2, cyc, tar, m3, m2, m1):

    fp.write( "//The following code computes Maj(A, B, C) and stores it in wl %d\n\n"% tar);    

    fp.write( "Read 0\n\n"); 
    cyc = cyc+1 # Read ~a    

    fp.write( "Apply %d 1 01 000000 "% tar); 
    cyc = cyc+1 # Write a
    Rotate(0, fp);
    fp.write( "Apply %d 1 01 000000 "% m3); 
    cyc = cyc+1  # Write a
    Rotate(0, fp);
    fp.write( "Apply %d 1 01 000000 "% m2); 
    cyc = cyc+1  # Write a
    Rotate(0, fp);
    fp.write( "Apply %d 1 01 000000 "% m1); 
    cyc = cyc+1  # Write a
    Rotate(0, fp);

    fp.write( "Read 1\n\n"); 
    cyc = cyc+1                 # Read ~b  

    fp.write( "Apply %d 1 00 000000 "% tar); 
    cyc = cyc+1 # a.b
    Rotate(0, fp);
    fp.write( "Apply %d 1 00 000000 "% m3); 
    cyc = cyc+1  # a.b
    Rotate(0, fp);
    fp.write( "Apply %d 1 00 000000 "% m2); 
    cyc = cyc+1  # a.b
    Rotate(0, fp);

    fp.write( "Read 2\n\n"); 
    cyc = cyc+1                 # Read ~c 

    fp.write( "Apply %d 1 00 000000 "% m1); 
    cyc = cyc+1  # a.c
    Rotate(0, fp);

    fp.write( "Read %d\n\n"% m1); 
    cyc = cyc+1            # Read a.c 

    fp.write( "Apply %d 1 00 000000 "% tar); 
    cyc = cyc+1 # (a.b).~(a.c)
    Rotate(0, fp);
    fp.write( "Apply %d 1 00 000000 "% m3); 
    cyc = cyc+1  # (a.b).~(a.c)
    Rotate(0, fp);
    fp.write( "Apply %d 1 01 000000 "% m2); 
    cyc = cyc+1  # (a.b) + ~(a.c)
    Rotate(0, fp);

    fp.write( "Read %d\n\n"% m2); 
    cyc = cyc+1            # Read (a.b) + ~(a.c)

    fp.write( "Apply %d 1 01 000000 "% tar); 
    cyc = cyc+1 # (a.b)XOR(a.c)
    Rotate(0, fp);
    fp.write( "Apply %d 1 01 000000 "% m3); 
    cyc = cyc+1  # (a.b)XOR(a.c)
    Rotate(0, fp);

    fp.write( "Apply %d 0 00 000000 "% m2); 
    cyc = cyc+1  # RESET wl m2, m1
    Rotate(0, fp);
    fp.write( "Apply %d 0 00 000000 "% m1); 
    cyc = cyc+1  
    Rotate(0, fp);

    fp.write( "Read 1\n\n"); 
    cyc = cyc+1                 # Read ~b

    fp.write( "Apply %d 1 01 000000 "% m2); 
    cyc = cyc+1  # Write b
    Rotate(0, fp);

    fp.write( "Read 2\n\n"); 
    cyc = cyc+1                 # Read ~c

    fp.write( "Apply %d 1 00 000000 "% m2); 
    cyc = cyc+1  # b.c
    Rotate(0, fp);

    fp.write( "Read %d\n\n"% m2); 
    cyc = cyc+1            # Read b.c

    fp.write( "Apply %d 1 00 000000 "% tar); 
    cyc = cyc+1 # (a.b XOR a.c).~(b.c)
    Rotate(0, fp);
    fp.write( "Apply %d 1 01 000000 "% m3); 
    cyc = cyc+1  # (a.b XOR a.c) + ~(b.c)
    Rotate(0, fp);

    fp.write( "Read %d\n\n"% m3); 
    cyc = cyc+1            # Read (a.b XOR a.c) + ~(b.c)

    fp.write( "Apply %d 1 01 000000 "% tar); 
    cyc = cyc+1 # (a.b XOR a.c) XOR (b.c)
    Rotate(0, fp);

    # PIR Loads string of 1's
    fp.write( "Apply %d 0 00 000000 "% m3); 
    cyc = cyc+1  # RESET wl m3, m2
    Rotate(0, fp);

    fp2.write("%d "% cyc);
    for i in range(64): 
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply %d 0 00 000000 "% m2); 
    cyc = cyc+1  
    Rotate(0, fp);

    fp2.write("%d "% cyc);
    for i in range(64): 
        fp2.write("1");
    fp2.write("\n\n");

    return cyc;


def Sum(sharound, fp, fp2, cyc, a, b, m1, m2, m3, m4, ainverted):    # Computation memory NOT PREVIOUSLY CLEARED
    # Stored A ++ B in m4, ++ is sum

    # Assuming B is initially non-inverted

    if ( ainverted == 0 ) :  # A is non-inverted (from PIR or Computation Memory)

        if (a >= 0):
            fp.write( "Read %d\n\n"% a); 
            cyc = cyc+1             # Read A

            fp.write( "Apply %d 1 01 000000 "% m1); 
            cyc = cyc+1    # Write ~A
            Rotate(0, fp);

      
        else: 
            # PIR Loads A
            fp.write( "Apply %d 0 01 000000 "% m1); 
            cyc = cyc+1  # Write ~A
            Rotate(0, fp);
            PIR_RoundConstants(fp2, cyc, sharound);

      

        fp.write( "Read %d\n\n"% m1); 
        cyc = cyc+1            # Read ~A

    

    else:   # A is inverted (from SHA-2 State partition)
        fp.write( "Read %d\n\n"% a); 
        cyc = cyc+1             # Read ~A

    

    fp.write( "Apply %d 1 01 000000 "% m4); 
    cyc = cyc+1  # Write A
    Rotate(0, fp);
    fp.write( "Apply %d 1 01 000000 "% m3); 
    cyc = cyc+1  # Write A
    Rotate(0, fp);
    fp.write( "Apply %d 1 01 000000 "% m2); 
    cyc = cyc+1  # Write A
    Rotate(0, fp);

    if (b >= 0):

        fp.write( "Read %d\n\n"% b); 
        cyc = cyc+1             # Read B

        fp.write( "Apply %d 1 00 000000 "% m4); 
        cyc = cyc+1  # A.~B
        Rotate(0, fp);
        fp.write( "Apply %d 1 00 000000 "% m3); 
        cyc = cyc+1  # A.~B
        Rotate(0, fp);
        fp.write( "Apply %d 1 01 000000 "% m2); 
        cyc = cyc+1  # A + ~B
        Rotate(0, fp); 

    
    
    else:
        # PIR Loads B
        fp.write( "Apply %d 0 00 000000 "% m4); 
        cyc = cyc+1  # A.~B
        Rotate(0, fp);
        PIR_Words(fp2, cyc, sharound);     

        fp.write( "Apply %d 0 00 000000 "% m3); 
        cyc = cyc+1  # A.~B
        Rotate(0, fp);
        PIR_Words(fp2, cyc, sharound);    

        fp.write( "Apply %d 0 01 000000 "% m2); 
        cyc = cyc+1  # A + ~B
        Rotate(0, fp); 
        PIR_Words(fp2, cyc, sharound);    
 
    

    fp.write( "Read %d\n\n"% m2); 
    cyc = cyc+1            # Read A + ~B  

    fp.write( "Apply %d 1 01 000000 "% m4); 
    cyc = cyc+1  # A XOR B
    Rotate(0, fp);
    fp.write( "Apply %d 1 01 000000 "% m3); 
    cyc = cyc+1  # A XOR B
    Rotate(0, fp);

    # PIR Loads string of 1's
    fp.write( "Apply %d 0 00 000000 "% m2); 
    cyc = cyc+1  # RESET m1, m
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64): 
        fp2.write("1");
    fp2.write("\n\n");

    if (ainverted == 0):

        fp.write( "Apply %d 0 00 000000 "% m1); 
        cyc = cyc+1
        Rotate(0, fp);
        fp2.write("%d "% cyc);
        for i in range(64): 
            fp2.write("1");
        fp2.write("\n\n");

    

    # Copy A in non_inverted form, half to m2 and half to m1

    if (ainverted == 0):

        if (a >= 0):

            fp.write( "Read %d\n\n"% a); 
            cyc = cyc+1             # Read A

            fp.write( "Apply %d 1 01 000000 "% m1); 
            cyc = cyc+1    # Write ~A
            Rotate(0, fp);    
        else: 
            # PIR Loads A
            fp.write( "Apply %d 0 01 000000 "% m1); 
            cyc = cyc+1    # Write ~A
            Rotate(0, fp);

            PIR_RoundConstants(fp2, cyc, sharound);

      

        fp.write( "Read %d\n\n"% m1); 
        cyc = cyc+1            # Read ~A
        
    else:   # A is inverted (from SHA-2 State partition)

        fp.write( "Read %d\n\n"% a); 
        cyc = cyc+1             # Read ~A


    # PIR Loads String of 1's
    fp.write( "Apply %d 0 00 000000 "% m1); 
    cyc = cyc+1  # Clear m1
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64): 
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply %d 1 01 000000 "% m2); 
    cyc = cyc+1  # Copy a31 a30 a29 ... a0 to m2
    for i in range(32):
        fp.write( "0 %d "% (63-i));
    
    for i in range(32):
        fp.write( "1 %d "% (31-i));
    
    fp.write( "\n\n");

    fp.write( "Apply %d 1 01 000000 "% m1); 
    cyc = cyc+1  # Copy 0 a62 a61 ... a32 to m1
    for i in range(32):
        fp.write( "0 %d "% (31-i));
    

    fp.write( "0 63 ");

    for i in range(1,32):
        fp.write( "1 %d "% (63-i));
    
    fp.write( "\n\n");  

    # Copy B in inverted form, half to m2 and half to m1
    
    if (b >= 0):
        fp.write( "Read %d\n\n"% b); 
        cyc = cyc+1             # Read B

        fp.write( "Apply %d 1 01 000000 "% m2); 
        cyc = cyc+1  # Copy ~b31 ~b30 ~b29 ... ~b0 to m2
        for i in range(32):
            fp.write( "1 %d "% (31-i));
      
        for i in range(32):
            fp.write( "0 %d "% (63-i));
      
        fp.write( "\n\n");

        fp.write( "Apply %d 1 01 000000 "% m1); 
        cyc = cyc+1  # Copy ~b63 ~b62 ~b61 ... ~b32 to m1
        for i in range(32):
            fp.write( "1 %d "% (63-i));
        
        for i in range(32):
            fp.write( "0 %d "% (31-i));
        
        fp.write( "\n\n");    

    else: 

        # PIR Loads B
        fp.write( "Apply %d 0 01 000000 "% m2); 
        cyc = cyc+1  # Copy ~b31 ~b30 ~b29 ... ~b0 to m2
        for i in range(32):
            fp.write( "1 %d "% (31-i));
      
        for i in range(32):
            fp.write( "0 %d "% (63-i));
      
        fp.write( "\n\n");

        PIR_Words(fp2, cyc, sharound);    

        fp.write( "Apply %d 0 01 000000 "% m1); 
        cyc = cyc+1  # Copy ~b63 ~b62 ~b61 ... ~b32 to m1
        for i in range(32):
            fp.write( "1 %d "% (63-i));
      
        for i in range(32):
            fp.write( "0 %d "% (31-i));
      
        fp.write( "\n\n");    

        PIR_Words(fp2, cyc, sharound);    

    cyc = Calculate_carrybits(fp, fp2, cyc, m2, m1);    # Line m2 contains (Carry >>> 1)


   # print(cyc)
    # Carry bits need to be left rotated by 1

    fp.write( "Read %d\n\n"% m2); 
    cyc = cyc+1         # Read (Carry >>> 1)

    fp.write( "Apply %d 1 00 000000 "% m4); 
    cyc = cyc+1 # (A XOR B).~C
    Rotate(63, fp);

    fp.write( "Apply %d 1 01 000000 "% m3); 
    cyc = cyc+1 # (A XOR B) + ~C
    Rotate(63, fp); 

    fp.write( "Read %d\n\n"% m3); 
    cyc = cyc+1         # Read (A XOR B) + ~C 

    fp.write( "Apply %d 1 01 000000 "% m4); 
    cyc = cyc+1 # (A XOR B) XOR C
    Rotate(0, fp);      

    fp.write( "Apply %d 0 00 000000 "% m3); 
    cyc = cyc+1    # RESET m3
    Rotate(0, fp);

    fp2.write("%d "% cyc);
    for i in range(64): 
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply %d 0 00 000000 "% m2); 
    cyc = cyc+1    # RESET m2
    Rotate(0, fp); 

    fp2.write("%d "% cyc);
    for i in range(64): 
        fp2.write("1");
    fp2.write("\n\n");  

    return cyc;

def stringToBinary(s):

    if len(s) == 0:
        return 0
    length = len(s)
    binary = []
    for i in range(length):
        ch = ord(s[i])
        for j in range(7, -1, -1):
            if (ch & (1 << j)):
                binary.append('1')
            else:
                binary.append('0')
    for i in range(length, 960):
        if i == length:
            binary.append('1')
        else:
            binary.append('0')
    place = 63
    for i in range(960, 1024):
        k = length >> place
        place -= 1
        if k & 1:
            binary.append('1')
        else:
            binary.append('0')
    return binary
 


def calc_sha_256(inp, length):

    global SHA2_K

    for i in range(16):
        temp = 0
        for j in range(63, -1, -1):
            if inp[64*i+63-j] == '1':
                temp += (1 << j)
        SHA2_K[i] = temp

    for i in range(16, 80):
        s0 = right_rot(SHA2_K[i - 15], 7) ^ right_rot(SHA2_K[i - 15], 18) ^ (SHA2_K[i - 15] >> 3)
        s1 = right_rot(SHA2_K[i - 2], 17) ^ right_rot(SHA2_K[i - 2], 19) ^ (SHA2_K[i - 2] >> 10)
        SHA2_K[i] = SHA2_K[i - 16] + s0 + SHA2_K[i - 7] + s1

def SHA2512(prefix='',inputStr=None, genConfig = False):
    fp = open(prefix+"SHA-2.ins", "w");
    fp2 = open(prefix+"SHA-2.inp", "w");

    #char *inp = (char *) malloc(100*sizeof(char));
    if inputStr == None:
        inp = input("Enter string: ");
    else:
        inp = inputStr 
    bininp = stringToBinary(inp);

    calc_sha_256(bininp, 1024);

    cyc = 0;
    cyc = Load(fp, fp2, cyc);

    for i in range(80):
        cyc = Round(fp, fp2, cyc, i);
    fp.close()
    fp2.close()
    
    if genConfig:
        if '/' in prefix:
            preName = prefix[prefix.rfind('/')+1:]
        else:
            preName = prefix
        
        config = dict()
        config['dim'] = {'m':42, 'n':64}
        config['filename'] = {'input':preName+"SHA-2.inp",\
                'ins_mem':preName+'SHA-2.ins',\
                'output': preName+'SHA-2'}
        config['simulation'] = {'cycles': 0,  'print_ins': 1, 'verbose': 0}
        with open(prefix+'config.json','w') as outfile:
            json.dump(config, outfile,indent=4)
    
    return cyc;



def Round(fp, fp2, cyc, i):


    #TODO: 
    #uint64_t w[80] = {0};
    w = [0 for i in range(80)]
    #printf("cyc = %d\n", cyc);

    # Ki ++ Wi
    cyc = Sum(i, fp, fp2, cyc, -1, -1, 8, 9, 10, 11, 0);  # Correctness of Sum verified
    #printf("cyc = %d\n", cyc);
    # Ki ++ Wi ++ H
    cyc = Sum(i, fp, fp2, cyc, 7, 11, 8, 9, 10, 12, 1);
    #printf("cyc = %d\n", cyc);
    # Reset wl 11
    fp.write( "Apply 11 0 00 000000 "); 
    cyc = cyc+1
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");
    #printf("cyc = %d\n", cyc);
    # Ch(E, F, G)
    cyc = Ch_EFG(fp, fp2, cyc, 10, 9, 8);         # Correctness of Ch verified against reference

    #printf("cyc = %d\n", cyc);
    # G -> H                                     # Correctness of copying verified
    fp.write( "Read 6\n\n"); 
    cyc = cyc+1            # Read ~G
    fp.write( "Apply 8 1 01 000000 "); 
    cyc = cyc+1    # Write G
    Rotate(0, fp); 
    fp.write( "Read 8\n\n"); 
    cyc = cyc+1             # Read G

    fp.write( "Apply 8 0 00 000000 "); 
    cyc = cyc+1    # Reset 8
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 7 0 00 000000 "); 
    cyc = cyc+1    # Reset H
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 7 1 01 000000 "); 
    cyc = cyc+1    # Copy ~G to H
    Rotate(0, fp);
    #printf("cyc = %d\n", cyc);
    # F -> G
    fp.write( "Read 5\n\n"); 
    cyc = cyc+1             # Read ~F
    fp.write( "Apply 8 1 01 000000 "); 
    cyc = cyc+1    # Write F
    Rotate(0, fp);
    fp.write( "Read 8\n\n"); 
    cyc = cyc+1             # Read F

    fp.write( "Apply 8 0 00 000000 "); 
    cyc = cyc+1    # Reset 8
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 6 0 00 000000 "); 
    cyc = cyc+1    # Reset G
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 6 1 01 000000 "); 
    cyc = cyc+1    # Copy ~F to G
    Rotate(0, fp);
    #printf("cyc = %d\n", cyc);
    # E -> F
    fp.write( "Read 4\n\n"); 
    cyc = cyc+1             # Read ~E
    fp.write( "Apply 8 1 01 000000 "); 
    cyc = cyc+1    # Write E
    Rotate(0, fp);
    fp.write( "Read 8\n\n"); 
    cyc = cyc+1             # Read E

    fp.write( "Apply 8 0 00 000000 "); 
    cyc = cyc+1    # Reset 8
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 5 0 00 000000 "); 
    cyc = cyc+1    # Reset F
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 5 1 01 000000 "); 
    cyc = cyc+1    # Copy ~E to F
    Rotate(0, fp);
    #printf("cyc = %d\n", cyc);
    # Computation of Sigma1(E)
    cyc = Sigma1(fp, fp2, cyc, 11, 9, 8);         # Correctness of Sigma1 verified against reference
    #printf("cyc = %d\n", cyc);
    # Ch ++ Sigma1
    cyc = Sum(i, fp, fp2, cyc, 10, 11, 8, 9, 13, 14, 0);
    #printf("cyc = %d\n", cyc);
    fp.write( "Apply 10 0 00 000000 "); 
    cyc = cyc+1  # Reset 10
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 11 0 00 000000 "); 
    cyc = cyc+1  # Reset 11
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");
    #printf("cyc = %d\n", cyc);
    # T1 = (Ch ++ Sigma1) ++ (Ki ++ Wi ++ H)
    cyc = Sum(i, fp, fp2, cyc, 12, 14, 8, 9, 10, 11, 0);    # Correctness of T1 verified against reference
    #printf("cyc = %d\n", cyc);
    fp.write( "Apply 14 0 00 000000 "); 
    cyc = cyc+1  # Reset 14
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 12 0 00 000000 "); 
    cyc = cyc+1  # Reset 12
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");
    #printf("cyc = %d\n", cyc);
    # D ++ T1
    cyc = Sum(i, fp, fp2, cyc, 3, 11, 8, 9, 10, 12, 1);
    #printf("cyc = %d\n", cyc);
    # Copy ~(D ++ T1) to ~E
    fp.write( "Read 12\n\n"); 
    cyc = cyc+1             # Read (D ++ T1)

    fp.write( "Apply 4 0 00 000000 "); 
    cyc = cyc+1    # Reset E
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");    

    fp.write( "Apply 4 1 01 000000 "); 
    cyc = cyc+1    # Write ~(D ++ T1) to E
    Rotate(0, fp);

    # Reset (D ++ T1)
    fp.write( "Apply 12 0 00 000000 "); 
    cyc = cyc+1    # Reset 12
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");    
    #printf("cyc = %d\n", cyc);
    # Maj(A, B, C)
    cyc = Maj(fp, fp2, cyc, 12, 10, 9, 8);        # Correctness of Maj(A,B,C) verified against reference
    #printf("cyc = %d\n", cyc);
    # C -> D                                     # Correctness of copying verified
    fp.write( "Read 2\n\n"); 
    cyc = cyc+1             # Read ~C
    fp.write( "Apply 8 1 01 000000 "); 
    cyc = cyc+1    # Write C
    Rotate(0, fp); 
    fp.write( "Read 8\n\n"); 
    cyc = cyc+1             # Read C

    fp.write( "Apply 8 0 00 000000 "); 
    cyc = cyc+1    # Reset 8
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 3 0 00 000000 "); 
    cyc = cyc+1    # Reset D
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 3 1 01 000000 "); 
    cyc = cyc+1    # Copy ~C to D
    Rotate(0, fp);
    #printf("cyc = %d\n", cyc);
    # B -> C
    fp.write( "Read 1\n\n"); 
    cyc = cyc+1             # Read ~B
    fp.write( "Apply 8 1 01 000000 "); 
    cyc = cyc+1    # Write B
    Rotate(0, fp);
    fp.write( "Read 8\n\n"); 
    cyc = cyc+1             # Read B

    fp.write( "Apply 8 0 00 000000 "); 
    cyc = cyc+1    # Reset 8
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 2 0 00 000000 "); 
    cyc = cyc+1    # Reset C
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 2 1 01 000000 "); 
    cyc = cyc+1    # Copy ~B to C
    Rotate(0, fp);
    #printf("cyc = %d\n", cyc);
    # A -> B
    fp.write( "Read 0\n\n"); 
    cyc = cyc+1             # Read ~A
    fp.write( "Apply 8 1 01 000000 "); 
    cyc = cyc+1    # Write A
    Rotate(0, fp);
    fp.write( "Read 8\n\n"); 
    cyc = cyc+1             # Read A

    fp.write( "Apply 8 0 00 000000 "); 
    cyc = cyc+1    # Reset 8
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 1 0 00 000000 "); 
    cyc = cyc+1    # Reset B
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 1 1 01 000000 "); 
    cyc = cyc+1    # Copy ~A to B
    Rotate(0, fp);
    #printf("cyc = %d\n", cyc);
    # Computation of Sigma0(A)
    cyc = Sigma0(fp, fp2, cyc, 10, 9, 8);         # Correctness of Sigma0 verified against reference
    #printf("cyc = %d\n", cyc);
    # Maj(A,B,C) ++ Sigma0
    cyc = Sum(i, fp, fp2, cyc, 10, 12, 8, 9, 13, 14, 0);  # Correctness of T2 verified
    #printf("cyc = %d\n", cyc);
    fp.write( "Apply 10 0 00 000000 "); 
    cyc = cyc+1  # Reset 10
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 12 0 00 000000 "); 
    cyc = cyc+1  # Reset 12
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");
    #printf("cyc = %d\n", cyc);
    # T1 ++ T2
    cyc = Sum(i, fp, fp2, cyc, 11, 14, 8, 9, 10, 12, 0);
    #printf("cyc = %d\n", cyc);
    # Copy ~(T1 ++ T2) to ~A
    fp.write( "Read 12\n\n"); 
    cyc = cyc+1             # Read (T2 ++ T1)

    fp.write( "Apply 0 0 00 000000 "); 
    cyc = cyc+1    # Reset A
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");    

    fp.write( "Apply 0 1 01 000000 "); 
    cyc = cyc+1    # Write ~(D ++ T1) to A
    Rotate(0, fp);
  # printf("cyc = %d\n", cyc);
    fp.write( "Apply 11 0 00 000000 "); 
    cyc = cyc+1  # Reset 11
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 12 0 00 000000 "); 
    cyc = cyc+1  # Reset 12
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");

    fp.write( "Apply 14 0 00 000000 "); 
    cyc = cyc+1  # Reset 14
    Rotate(0, fp);
    fp2.write("%d "% cyc);
    for i in range(64):
        fp2.write("1");
    fp2.write("\n\n");
    #printf("cyc = %d\n", cyc);
    return cyc;



def TestSum(fp, cyc):

    fp2 = open("SHA-2.inp", "w");

    fp.write( "Apply 0 0 01 000000 "); 
    cyc = cyc+1
    Rotate(0, fp);

    fp2.write("%d "% cyc);
    #for(i=0; i<50; i++)
      #fp2.write("1");
    fp2.write("0100001010001010001011111001100011010111001010001010111000100010\n\n");

    fp.write( "Apply 1 0 01 000000 "); 
    cyc = cyc+1
    Rotate(0, fp);

    fp2.write("%d "% cyc);
    for i in range(64): 
        fp2.write("1");
    fp2.write("\n\n");

    cyc = Sum(0, fp, fp2, cyc, 0, 1, 2, 3, 4, 5, 1);
    
    fp2.close()
    return cyc;



if __name__ == '__main__':
    prefix = 'SHA3/'
    newobj = SHA2512(prefix)
    #print(newobj)

