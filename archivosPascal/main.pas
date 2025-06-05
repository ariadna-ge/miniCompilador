var x1 real;
var x2 real; (* coordenadas del 1er punto *)
var y1 real;
var y1 integer;
var y2 real; (* coordenadas del 2do punto *)
var m real; (* pendiente de la recta *)
writeln("Escriba el valor de x1: ");
read(x1);
write("Escriba el valor de x2: ");
read(x2);
writeln("Escriba el valor de y1: ");
read(y1);
write("Escriba el valor de y2: ");
read(y2);
m := (y2 - y1) / (x2 - x1);
writeln("La pendiente es: ", m);
end;