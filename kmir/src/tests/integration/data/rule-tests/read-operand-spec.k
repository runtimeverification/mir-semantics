module READ-OPERAND-SPEC
  imports KMIR

//   claim [read-operand-with-as]:
//         <k> #readOperand(operandCopy(place(local(1), .ProjectionElems))) => LOCAL ... </k>
//         <locals>
//           ListItem(_)
//           ListItem(typedLocal(_, _TY:Ty, _MUT) #as LOCAL) // crashes
//           ListItem(_)
//         </locals>

  claim [read-operand]:
        <k> #readOperand(operandCopy(place(local(1), .ProjectionElems)))
          =>
            typedLocal(VAL, TY, MUT)
//        ~> _CONT // TODO why is booster "stuck" here?
        </k>
        <locals>
          ListItem(_)
          ListItem(typedLocal(VAL, TY, MUT))
          ListItem(_)
        </locals>

endmodule