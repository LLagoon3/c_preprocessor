#include "myHeader.h"

void swap(var int, var int);

void main() {
  int a, b;
  a = 2; b = 3;
  swap(a, b);
  printf(“a=%d, b=%d\n”);
}

void swap(var int x, var int y){
  int tmp;
  tmp = x;
  x = y;
  y = tmp;
}

int subpro(var int a, float b){
  return a + b;
}
