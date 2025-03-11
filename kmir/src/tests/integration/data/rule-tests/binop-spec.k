module BINOP-SPEC
  imports KMIR

  // // needs lemmas otherwise and kore starts branching
  // claim [add-normal]:
  //       <k> rvalueCheckedBinaryOp(
  //             binOpAdd,
  //             operandCopy(place(local(1), .ProjectionElems)),
  //             operandCopy(place(local(2), .ProjectionElems))
  //           )
  //         =>
  //           typedLocal(
  //             Aggregate(
  //               ListItem(typedLocal(Integer(ARG1 +Int ARG2, WIDTH, true), ?_, ?_))
  //               ListItem(typedLocal(BoolVal(false), ?_, ?_))
  //             ),
  //             ?_,
  //             ?_
  //             )
  //         ...
  //       </k>
  //       <locals>
  //         ListItem(noValue( _TY, mutabilityMut))
  //         ListItem(typedLocal(Integer(ARG1, WIDTH, true), TY:Ty, _MUT1)) // important for the #compute rule to fire!
  //         ListItem(typedLocal(Integer(ARG2, WIDTH, true), TY   , _MUT2))
  //       </locals>
  //   requires ARG1 +Int ARG2 <Int (1 <<Int (WIDTH -Int 1))
  //    andBool 0 -Int (1 <<Int (WIDTH -Int 1)) <=Int ARG1 +Int ARG2
  //    andBool 0 <Int WIDTH
  //    andBool WIDTH <=Int 128

  claim [add-underflow]:
        <k> rvalueCheckedBinaryOp(
              binOpAdd,
              operandCopy(place(local(1), .ProjectionElems)),
              operandCopy(place(local(2), .ProjectionElems))
            )
          =>
            typedLocal(
              Aggregate(
                ListItem(?_)
                ListItem(typedLocal(BoolVal(true), ?_, ?_))
              ),
              ?_,
              ?_
              )
          ...
        </k>
        <locals>
          ListItem(noValue( _TY, mutabilityMut))
          ListItem(typedLocal(Integer(ARG1, WIDTH, true), TY:Ty, _MUT1)) // important for the #compute rule to fire!
          ListItem(typedLocal(Integer(ARG2, WIDTH, true), TY   , _MUT2))
        </locals>
    requires ARG1 +Int ARG2 <Int 0 -Int (1 <<Int (WIDTH -Int 1))
     andBool 0 <Int WIDTH
     andBool WIDTH <=Int 128

  claim [add-overflow]:
        <k> rvalueCheckedBinaryOp(
              binOpAdd,
              operandCopy(place(local(1), .ProjectionElems)),
              operandCopy(place(local(2), .ProjectionElems))
            )
          =>
            typedLocal(
              Aggregate(
                ListItem(?_)
                ListItem(typedLocal(BoolVal(true), ?_, ?_))
              ),
              ?_,
              ?_
              )
          ...
        </k>
        <locals>
          ListItem(noValue( _TY, mutabilityMut))
          ListItem(typedLocal(Integer(ARG1, WIDTH, true), TY:Ty, _MUT1)) // important for the #compute rule to fire!
          ListItem(typedLocal(Integer(ARG2, WIDTH, true), TY   , _MUT2))
        </locals>
    requires ARG1 +Int ARG2 >=Int (1 <<Int (WIDTH -Int 1))
     andBool 0 <Int WIDTH
     andBool WIDTH <=Int 128

  claim [sub-overflow]:
        <k> rvalueCheckedBinaryOp(
              binOpSub,
              operandCopy(place(local(1), .ProjectionElems)),
              operandCopy(place(local(2), .ProjectionElems))
            )
          =>
            typedLocal(
              Aggregate(
                ListItem(?_)
                ListItem(typedLocal(BoolVal(true), ?_, ?_))
              ),
              ?_,
              ?_
              )
          ...
        </k>
        <locals>
          ListItem(noValue( _TY, mutabilityMut))
          ListItem(typedLocal(Integer(ARG1, WIDTH, true), TY:Ty, _MUT1)) // important for the #compute rule to fire!
          ListItem(typedLocal(Integer(ARG2, WIDTH, true), TY   , _MUT2))
        </locals>
    requires ARG1 -Int ARG2 >=Int (1 <<Int (WIDTH -Int 1))
     andBool 0 <Int WIDTH
     andBool WIDTH <=Int 128

endmodule
