int main() {
   
   return 0;
}

// OR
/*

#define ENABLE_WARNING
#ifdef ENABLE_WARNING
#define WARNING_MSG "Warning: Something might go wrong!"
#else
#define WARNING_MSG ""
#endif

int main() {
_Pragma("message \"Hello, world!\"")
_Pragma("message \"This is a C99 program.\"")
_Pragma(WARNING_MSG)

return 0;
}

*/