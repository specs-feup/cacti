; ModuleID = '/home/fprada/internship/cacti_tests/C/c89/nodes/ImplicitValueInitExpr/src.c'
source_filename = "/home/fprada/internship/cacti_tests/C/c89/nodes/ImplicitValueInitExpr/src.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

%struct.point = type { double, double }

@ptarray = dso_local global [10 x %struct.point] [%struct.point { double 1.000000e+00, double 0.000000e+00 }, %struct.point zeroinitializer, %struct.point { double 2.000000e+00, double 1.000000e+00 }, %struct.point zeroinitializer, %struct.point zeroinitializer, %struct.point zeroinitializer, %struct.point zeroinitializer, %struct.point zeroinitializer, %struct.point zeroinitializer, %struct.point zeroinitializer], align 16

!llvm.module.flags = !{!0, !1, !2, !3, !4}
!llvm.ident = !{!5}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"PIC Level", i32 2}
!2 = !{i32 7, !"PIE Level", i32 2}
!3 = !{i32 7, !"uwtable", i32 1}
!4 = !{i32 7, !"frame-pointer", i32 2}
!5 = !{!"Ubuntu clang version 14.0.0-1ubuntu1"}
