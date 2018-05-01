// Benchmark "test_18" written by ABC on Mon Feb  5 19:26:36 2018

module test_18 ( 
    \w1[0] , \w1[1] , \w1[2] , \w2[0] , \w2[1] , \w2[2] , \w3[0] , \w3[1] ,
    \w3[2] , \c1[0] , \c2[0] ,
    output_0, output_1, output_2  );
  input  \w1[0] , \w1[1] , \w1[2] , \w2[0] , \w2[1] , \w2[2] , \w3[0] ,
    \w3[1] , \w3[2] , \c1[0] , \c2[0] ;
  output output_0, output_1, output_2;
  wire n15, n16, n17, n18, n19, n20, n21, n22, n24, n25, n26, n27, n28, n29,
    n31, n32, n33, n34, n35, n36;
  inv1 g00(.a(\c2[0] ), .O(n15));
  nor2 g01(.a(n15), .b(\w1[0] ), .O(n16));
  inv1 g02(.a(\w2[0] ), .O(n17));
  nor2 g03(.a(\c1[0] ), .b(n17), .O(n18));
  inv1 g04(.a(\w3[0] ), .O(n19));
  inv1 g05(.a(\c1[0] ), .O(n20));
  nor2 g06(.a(n20), .b(n19), .O(n21));
  nor3 g07(.a(n21), .b(n18), .c(\c2[0] ), .O(n22));
  nor2 g08(.a(n22), .b(n16), .O(output_0));
  nor2 g09(.a(n15), .b(\w1[1] ), .O(n24));
  inv1 g10(.a(\w2[1] ), .O(n25));
  nor2 g11(.a(\c1[0] ), .b(n25), .O(n26));
  inv1 g12(.a(\w3[1] ), .O(n27));
  nor2 g13(.a(n20), .b(n27), .O(n28));
  nor3 g14(.a(n28), .b(n26), .c(\c2[0] ), .O(n29));
  nor2 g15(.a(n29), .b(n24), .O(output_1));
  nor2 g16(.a(n15), .b(\w1[2] ), .O(n31));
  inv1 g17(.a(\w2[2] ), .O(n32));
  nor2 g18(.a(\c1[0] ), .b(n32), .O(n33));
  inv1 g19(.a(\w3[2] ), .O(n34));
  nor2 g20(.a(n20), .b(n34), .O(n35));
  nor3 g21(.a(n35), .b(n33), .c(\c2[0] ), .O(n36));
  nor2 g22(.a(n36), .b(n31), .O(output_2));
endmodule


