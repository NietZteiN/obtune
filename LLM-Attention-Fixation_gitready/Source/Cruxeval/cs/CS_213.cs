using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s) {
        return s.Replace("(", "[").Replace(")", "]");
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("(ac)")).Equals(("[ac]")));
    }

}
