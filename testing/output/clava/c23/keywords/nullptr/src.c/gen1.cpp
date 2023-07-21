#include <stddef.h>
#include <stdio.h>
void g(int *) {
   puts("Function g called");
}

int main() {
   g(nullptr);
   void *cloned_nullptr = nullptr;
}
