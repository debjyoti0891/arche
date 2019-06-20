// Benchmark "CM138" written by ABC on Mon Sep 24 10:35:51 2018

module CM138 ( 
    a, b, c, d, e, f,
    g, h, i, j, k, l, m, n  );
  input  a, b, c, d, e, f;
  output g, h, i, j, k, l, m, n;
  wire n15, n16, n17, n18, n19, n20, n22, n23, n24, n25, n27, n28, n29, n30,
    n32, n33, n34, n36, n37, n38, n39, n41, n43, n45;
  inv1 g00(.a(d), .O(n15));
  nor4 g01(.a(f), .b(e), .c(n15), .d(c), .O(n16));
  inv1 g02(.a(n16), .O(n17));
  nor2 g03(.a(b), .b(a), .O(n18));
  inv1 g04(.a(n18), .O(n19));
  nor2 g05(.a(n19), .b(n17), .O(n20));
  inv1 g06(.a(n20), .O(g));
  inv1 g07(.a(a), .O(n22));
  nor2 g08(.a(b), .b(n22), .O(n23));
  inv1 g09(.a(n23), .O(n24));
  nor2 g10(.a(n24), .b(n17), .O(n25));
  inv1 g11(.a(n25), .O(h));
  inv1 g12(.a(b), .O(n27));
  nor2 g13(.a(n27), .b(a), .O(n28));
  inv1 g14(.a(n28), .O(n29));
  nor2 g15(.a(n29), .b(n17), .O(n30));
  inv1 g16(.a(n30), .O(i));
  nor2 g17(.a(n27), .b(n22), .O(n32));
  inv1 g18(.a(n32), .O(n33));
  nor2 g19(.a(n33), .b(n17), .O(n34));
  inv1 g20(.a(n34), .O(j));
  inv1 g21(.a(c), .O(n36));
  nor4 g22(.a(f), .b(e), .c(n15), .d(n36), .O(n37));
  inv1 g23(.a(n37), .O(n38));
  nor2 g24(.a(n38), .b(n19), .O(n39));
  inv1 g25(.a(n39), .O(k));
  nor2 g26(.a(n38), .b(n24), .O(n41));
  inv1 g27(.a(n41), .O(l));
  nor2 g28(.a(n38), .b(n29), .O(n43));
  inv1 g29(.a(n43), .O(m));
  nor2 g30(.a(n38), .b(n33), .O(n45));
  inv1 g31(.a(n45), .O(n));
endmodule


