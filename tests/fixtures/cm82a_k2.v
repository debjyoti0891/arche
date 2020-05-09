// Benchmark "CM82" written by ABC on Sat May  9 16:30:25 2020

module CM82 ( 
    a, b, c, d, e,
    f, g, h  );
  input  a, b, c, d, e;
  output f, g, h;
  wire old_n11_, old_n13_, old_n14_, old_n15_, old_n16_, old_n17_, old_n19_,
    old_n20_, old_n21_;
  assign f = old_n11_ ^ ~a;
  assign old_n11_ = ~b ^ c;
  assign g = old_n13_ ^ ~old_n17_;
  assign old_n13_ = ~old_n14_ & ~old_n16_;
  assign old_n14_ = ~old_n15_ & ~a;
  assign old_n15_ = b & c;
  assign old_n16_ = ~b & ~c;
  assign old_n17_ = ~d ^ e;
  assign h = old_n19_ | old_n21_;
  assign old_n19_ = old_n13_ & ~old_n20_;
  assign old_n20_ = ~d & ~e;
  assign old_n21_ = d & e;
endmodule


