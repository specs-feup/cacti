#include <stdio.h>
int main() { // selected in C23 mode, may be selected in pre-C23 mode
   printf("1: yes\n");
   printf("2: yes\n");
   printf("3: yes\n");
   // C23 directives #elifdef/#elifndef
   printf("4: no3\n"); // may be selected in pre-C23 mode
}
