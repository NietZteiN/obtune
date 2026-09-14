using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string froms) {
        text = text.Trim(froms.ToCharArray());
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("0 t 1cos "), ("st 0	\n  ")).Equals(("1co")));
    }

}
