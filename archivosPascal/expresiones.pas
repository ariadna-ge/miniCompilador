var x1 real;
var x2 real;
var r_cos real;
var r_sen real;
var r_tan real;

begin
x1 := 0.5;
x2 := 0.3;

r_cos := cos(x1 + x2); (*Calcula el coseno de la suma de x1 y x2*)
r_sen := sin(x1 + x2);  (*Calcula el seno de la suma de x1 y x2*)
r_tan := tan(x1 + x2); (*Calcula la tangente de la suma de x1 y x2*)
end;