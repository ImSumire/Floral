; ModuleID = 'target/main.ll'
source_filename = "target/main.ll"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

; Function Attrs: nofree nounwind
declare noundef i32 @printf(ptr nocapture noundef readonly, ...) local_unnamed_addr #0

; Function Attrs: nofree nosync nounwind memory(none)
define i32 @fact(i32 %.1) local_unnamed_addr #1 {
fact_entry:
  %.63 = icmp slt i32 %.1, 2
  br i1 %.63, label %common.ret, label %fact_entry.endif.preheader

fact_entry.endif.preheader:                       ; preds = %fact_entry
  %0 = tail call i32 @llvm.usub.sat.i32(i32 %.1, i32 2)
  %1 = add nuw i32 %0, 1
  %min.iters.check = icmp ult i32 %0, 7
  br i1 %min.iters.check, label %fact_entry.endif.preheader8, label %vector.ph

vector.ph:                                        ; preds = %fact_entry.endif.preheader
  %n.vec = and i32 %1, -8
  %ind.end = sub i32 %.1, %n.vec
  %.splatinsert = insertelement <4 x i32> poison, i32 %.1, i64 0
  %.splat = shufflevector <4 x i32> %.splatinsert, <4 x i32> poison, <4 x i32> zeroinitializer
  %induction = add <4 x i32> %.splat, <i32 0, i32 -1, i32 -2, i32 -3>
  br label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.ph
  %index = phi i32 [ 0, %vector.ph ], [ %index.next, %vector.body ]
  %vec.ind = phi <4 x i32> [ %induction, %vector.ph ], [ %vec.ind.next, %vector.body ]
  %vec.phi = phi <4 x i32> [ <i32 1, i32 1, i32 1, i32 1>, %vector.ph ], [ %2, %vector.body ]
  %vec.phi7 = phi <4 x i32> [ <i32 1, i32 1, i32 1, i32 1>, %vector.ph ], [ %3, %vector.body ]
  %step.add = add <4 x i32> %vec.ind, <i32 -4, i32 -4, i32 -4, i32 -4>
  %2 = mul <4 x i32> %vec.ind, %vec.phi
  %3 = mul <4 x i32> %step.add, %vec.phi7
  %index.next = add nuw i32 %index, 8
  %vec.ind.next = add <4 x i32> %vec.ind, <i32 -8, i32 -8, i32 -8, i32 -8>
  %4 = icmp eq i32 %index.next, %n.vec
  br i1 %4, label %middle.block, label %vector.body, !llvm.loop !0

middle.block:                                     ; preds = %vector.body
  %bin.rdx = mul <4 x i32> %3, %2
  %5 = tail call i32 @llvm.vector.reduce.mul.v4i32(<4 x i32> %bin.rdx)
  %cmp.n = icmp eq i32 %1, %n.vec
  br i1 %cmp.n, label %common.ret, label %fact_entry.endif.preheader8

fact_entry.endif.preheader8:                      ; preds = %fact_entry.endif.preheader, %middle.block
  %.1.tr5.ph = phi i32 [ %.1, %fact_entry.endif.preheader ], [ %ind.end, %middle.block ]
  %accumulator.tr4.ph = phi i32 [ 1, %fact_entry.endif.preheader ], [ %5, %middle.block ]
  br label %fact_entry.endif

common.ret:                                       ; preds = %fact_entry.endif, %middle.block, %fact_entry
  %accumulator.tr.lcssa = phi i32 [ 1, %fact_entry ], [ %5, %middle.block ], [ %.13, %fact_entry.endif ]
  ret i32 %accumulator.tr.lcssa

fact_entry.endif:                                 ; preds = %fact_entry.endif.preheader8, %fact_entry.endif
  %.1.tr5 = phi i32 [ %.11, %fact_entry.endif ], [ %.1.tr5.ph, %fact_entry.endif.preheader8 ]
  %accumulator.tr4 = phi i32 [ %.13, %fact_entry.endif ], [ %accumulator.tr4.ph, %fact_entry.endif.preheader8 ]
  %.11 = add nsw i32 %.1.tr5, -1
  %.13 = mul i32 %.1.tr5, %accumulator.tr4
  %.6 = icmp ult i32 %.1.tr5, 3
  br i1 %.6, label %common.ret, label %fact_entry.endif, !llvm.loop !3
}

; Function Attrs: nofree nounwind
define i32 @main() local_unnamed_addr #0 {
main_entry:
  %.9 = alloca [8 x i8], align 8
  store <8 x i8> <i8 119, i8 104, i8 105, i8 108, i8 101, i8 10, i8 0, i8 0>, ptr %.9, align 8
  %.12 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.9)
  %.9.1 = alloca [8 x i8], align 8
  store <8 x i8> <i8 119, i8 104, i8 105, i8 108, i8 101, i8 10, i8 0, i8 0>, ptr %.9.1, align 8
  %.12.1 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.9.1)
  %.9.2 = alloca [8 x i8], align 8
  store <8 x i8> <i8 119, i8 104, i8 105, i8 108, i8 101, i8 10, i8 0, i8 0>, ptr %.9.2, align 8
  %.12.2 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.9.2)
  %.9.3 = alloca [8 x i8], align 8
  store <8 x i8> <i8 119, i8 104, i8 105, i8 108, i8 101, i8 10, i8 0, i8 0>, ptr %.9.3, align 8
  %.12.3 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.9.3)
  %.9.4 = alloca [8 x i8], align 8
  store <8 x i8> <i8 119, i8 104, i8 105, i8 108, i8 101, i8 10, i8 0, i8 0>, ptr %.9.4, align 8
  %.12.4 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.9.4)
  %.9.5 = alloca [8 x i8], align 8
  store <8 x i8> <i8 119, i8 104, i8 105, i8 108, i8 101, i8 10, i8 0, i8 0>, ptr %.9.5, align 8
  %.12.5 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.9.5)
  %.9.6 = alloca [8 x i8], align 8
  store <8 x i8> <i8 119, i8 104, i8 105, i8 108, i8 101, i8 10, i8 0, i8 0>, ptr %.9.6, align 8
  %.12.6 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.9.6)
  %.9.7 = alloca [8 x i8], align 8
  store <8 x i8> <i8 119, i8 104, i8 105, i8 108, i8 101, i8 10, i8 0, i8 0>, ptr %.9.7, align 8
  %.12.7 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.9.7)
  %.9.8 = alloca [8 x i8], align 8
  store <8 x i8> <i8 119, i8 104, i8 105, i8 108, i8 101, i8 10, i8 0, i8 0>, ptr %.9.8, align 8
  %.12.8 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.9.8)
  %.9.9 = alloca [8 x i8], align 8
  store <8 x i8> <i8 119, i8 104, i8 105, i8 108, i8 101, i8 10, i8 0, i8 0>, ptr %.9.9, align 8
  %.12.9 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.9.9)
  %.25 = alloca [8 x i8], align 8
  store <8 x i8> <i8 117, i8 110, i8 116, i8 105, i8 108, i8 10, i8 0, i8 0>, ptr %.25, align 8
  %.28 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.25)
  %.25.1 = alloca [8 x i8], align 8
  store <8 x i8> <i8 117, i8 110, i8 116, i8 105, i8 108, i8 10, i8 0, i8 0>, ptr %.25.1, align 8
  %.28.1 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.25.1)
  %.25.2 = alloca [8 x i8], align 8
  store <8 x i8> <i8 117, i8 110, i8 116, i8 105, i8 108, i8 10, i8 0, i8 0>, ptr %.25.2, align 8
  %.28.2 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.25.2)
  %.25.3 = alloca [8 x i8], align 8
  store <8 x i8> <i8 117, i8 110, i8 116, i8 105, i8 108, i8 10, i8 0, i8 0>, ptr %.25.3, align 8
  %.28.3 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.25.3)
  %.25.4 = alloca [8 x i8], align 8
  store <8 x i8> <i8 117, i8 110, i8 116, i8 105, i8 108, i8 10, i8 0, i8 0>, ptr %.25.4, align 8
  %.28.4 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.25.4)
  %.25.5 = alloca [8 x i8], align 8
  store <8 x i8> <i8 117, i8 110, i8 116, i8 105, i8 108, i8 10, i8 0, i8 0>, ptr %.25.5, align 8
  %.28.5 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.25.5)
  %.25.6 = alloca [8 x i8], align 8
  store <8 x i8> <i8 117, i8 110, i8 116, i8 105, i8 108, i8 10, i8 0, i8 0>, ptr %.25.6, align 8
  %.28.6 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.25.6)
  %.25.7 = alloca [8 x i8], align 8
  store <8 x i8> <i8 117, i8 110, i8 116, i8 105, i8 108, i8 10, i8 0, i8 0>, ptr %.25.7, align 8
  %.28.7 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.25.7)
  %.25.8 = alloca [8 x i8], align 8
  store <8 x i8> <i8 117, i8 110, i8 116, i8 105, i8 108, i8 10, i8 0, i8 0>, ptr %.25.8, align 8
  %.28.8 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.25.8)
  %.25.9 = alloca [8 x i8], align 8
  store <8 x i8> <i8 117, i8 110, i8 116, i8 105, i8 108, i8 10, i8 0, i8 0>, ptr %.25.9, align 8
  %.28.9 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.25.9)
  %.38 = alloca [7 x i8], align 4
  store <4 x i8> <i8 104, i8 105, i8 32, i8 33>, ptr %.38, align 4
  %.38.repack20 = getelementptr inbounds [7 x i8], ptr %.38, i64 0, i64 4
  store i8 10, ptr %.38.repack20, align 4
  %.38.repack21 = getelementptr inbounds [7 x i8], ptr %.38, i64 0, i64 5
  store i8 0, ptr %.38.repack21, align 1
  %.38.repack22 = getelementptr inbounds [7 x i8], ptr %.38, i64 0, i64 6
  store i8 0, ptr %.38.repack22, align 2
  %.41 = call i32 (ptr, ...) @printf(ptr nonnull dereferenceable(1) %.38)
  ret i32 3628800
}

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(none)
declare i32 @llvm.vector.reduce.mul.v4i32(<4 x i32>) #2

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.usub.sat.i32(i32, i32) #3

attributes #0 = { nofree nounwind }
attributes #1 = { nofree nosync nounwind memory(none) }
attributes #2 = { nocallback nofree nosync nounwind willreturn memory(none) }
attributes #3 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }

!0 = distinct !{!0, !1, !2}
!1 = !{!"llvm.loop.isvectorized", i32 1}
!2 = !{!"llvm.loop.unroll.runtime.disable"}
!3 = distinct !{!3, !2, !1}
