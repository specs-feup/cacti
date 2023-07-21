#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
int counter = 0;
void increment_counter() {
   counter++;
}

int main() {
   increment_counter();
   printf("Counter in main thread: %d\n", counter);
   int num_forks = 4;
   for(int i = 0; i < num_forks; i++) {
      pid_t pid = fork();
      if(pid == 0) {
         increment_counter();
         printf("Counter in child process %d: %d\n", i, counter);
         
         return 0;
      }
      else if(pid > 0) {
         }
         else {
            fprintf(stderr, "Fork failed.\n");
            
            return 1;
         }
   }
   for(int i = 0; i < num_forks; i++) {
      wait(0);
   }
   printf("Counter in main process after forks: %d\n", counter);
   
   return 0;
}
