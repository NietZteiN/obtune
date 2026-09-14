using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static Tuple<long, long> F(string text) {
        long ws = 0;
        foreach(var s in text){
            if (Char.IsWhiteSpace(s))
            {
                ws += 1;
            }
        }
        return Tuple.Create(ws, (long)text.Length);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("jcle oq wsnibktxpiozyxmopqkfnrfjds")).Equals((Tuple.Create(2L, 34L))));
    }

}
