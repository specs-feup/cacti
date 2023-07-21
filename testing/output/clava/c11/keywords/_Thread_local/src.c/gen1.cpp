#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
int counter = 0;
void increment_counter() {
   counter++;
}

int main() {
   increment_counter();
   int num_forks = 4;
   int j;
   for(j = 0; j < num_forks; j++) {
      pid_t pid = fork();
      if(pid == 0) {
         increment_counter();
         
         return 0;
      }
      else if(pid > 0) {
         }
         else {
            
            return 1;
         }
   }
   int i = 0;
   for(i = 0; i < num_forks; i++) {
      wait(0);
   }
   
   return 0;
}
