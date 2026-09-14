using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        return text.PadRight(text.Length + 1, '#');
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("the cow goes moo")).Equals(("the cow goes moo#")));
    }

}
