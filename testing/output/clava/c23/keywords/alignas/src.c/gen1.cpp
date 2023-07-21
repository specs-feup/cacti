#include <stdalign.h>

struct sse_t {
   float sse_data[4];
};


struct data {
   char x;
   char cacheline[128];
};

int main() {
}
