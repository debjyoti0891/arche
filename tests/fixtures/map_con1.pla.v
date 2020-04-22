// Benchmark "pla//con1" written by ABC on Mon Sep 24 10:33:50 2018

module \pla//con1  ( 
    f, b, c, d, a, h, g,
    f0, f1  );
  input  f, b, c, d, a, h, g;
  output f0, f1;
  wire n10, n11, n12, n13, n14, n15, n16, n17, n18, n19, n20, n22, n23, n24,
    n25, n26, n27, n28, n29, n30, n31, n32;
  inv1 g00(.a(b), .O(n10));
  inv1 g01(.a(h), .O(n11));
  nor2 g02(.a(n11), .b(f), .O(n12));
  nor2 g03(.a(n12), .b(a), .O(n13));
  nor2 g04(.a(n13), .b(n10), .O(n14));
  inv1 g05(.a(d), .O(n15));
  nor2 g06(.a(c), .b(n10), .O(n16));
  inv1 g07(.a(c), .O(n17));
  nor2 g08(.a(n17), .b(f), .O(n18));
  nor3 g09(.a(n18), .b(n16), .c(n15), .O(n19));
  nor2 g10(.a(n19), .b(n14), .O(n20));
  inv1 g11(.a(n20), .O(f0));
  inv1 g12(.a(f), .O(n22));
  inv1 g13(.a(a), .O(n23));
  nor2 g14(.a(d), .b(b), .O(n24));
  nor2 g15(.a(n24), .b(n23), .O(n25));
  nor2 g16(.a(n25), .b(n22), .O(n26));
  nor2 g17(.a(a), .b(b), .O(n27));
  inv1 g18(.a(g), .O(n28));
  nor2 g19(.a(n23), .b(n10), .O(n29));
  nor2 g20(.a(n29), .b(n28), .O(n30));
  nor2 g21(.a(n30), .b(f), .O(n31));
  nor3 g22(.a(n31), .b(n27), .c(n26), .O(n32));
  inv1 g23(.a(n32), .O(f1));
endmodule


