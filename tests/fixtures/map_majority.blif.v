// Benchmark "traffic_cl" written by ABC on Mon Sep 24 10:36:09 2018

module traffic_cl ( 
    a, b, c, d, e,
    f  );
  input  a, b, c, d, e;
  output f;
  wire n7, n8, n9, n10, n11, n12, n13, n14, n15;
  inv1 g0(.a(c), .O(n7));
  inv1 g1(.a(e), .O(n8));
  nor2 g2(.a(b), .b(a), .O(n9));
  nor3 g3(.a(n9), .b(n8), .c(n7), .O(n10));
  inv1 g4(.a(a), .O(n11));
  inv1 g5(.a(b), .O(n12));
  nor2 g6(.a(e), .b(c), .O(n13));
  nor3 g7(.a(n13), .b(n12), .c(n11), .O(n14));
  nor3 g8(.a(n14), .b(n10), .c(d), .O(n15));
  inv1 g9(.a(n15), .O(f));
endmodule


