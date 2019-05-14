module simple(in1,in2,in3,in4,in5,out);
input in1, in2, in3, in4, in5;
output out; 
wire n1, n2, n3, n4;



nor2 g00(.a(in1), .b(in2), .O(n1));
nor3 g01(.a(in3), .b(in4), c(in5), .O(n2));
nor2 g02(.a(in1), .b(n1), .O(n3));
nor2 g03(.a(n2), .b(n3), O(n4));
inv1 g04(.a(n4), .O(out));

endmodule

