// Benchmark "b1" written by ABC on Mon Sep 24 10:35:27 2018

module b1 ( 
    a, b, c,
    d, e, f, g  );
  input  a, b, c;
  output d, e, f, g;
  wire n8, n9, n10, n11, n14, n15, n16;
  inv1 g00(.a(a), .O(n8));
  inv1 g01(.a(b), .O(n9));
  nor2 g02(.a(n9), .b(n8), .O(n10));
  nor2 g03(.a(b), .b(a), .O(n11));
  nor2 g04(.a(n11), .b(n10), .O(e));
  inv1 g05(.a(c), .O(g));
  nor3 g06(.a(g), .b(b), .c(a), .O(n14));
  nor3 g07(.a(c), .b(n9), .c(n8), .O(n15));
  nor2 g08(.a(n15), .b(n14), .O(n16));
  inv1 g09(.a(n16), .O(f));
  buf  g10(.a(c), .O(d));
endmodule


