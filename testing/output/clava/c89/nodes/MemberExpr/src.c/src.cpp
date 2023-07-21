
struct Foo {
   int x;
   int y;
};

int main() {
   struct Foo foo;
   foo.x = 10; // MemberExpr: X.F
   struct Foo *ptr = &foo;
   ptr->y = 20; // MemberExpr: X->F
   
   return 0;
}
