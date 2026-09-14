using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s, string sep) {
        s += sep;
        return s.Substring(0, s.LastIndexOf(sep));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("234dsfssdfs333324314"), ("s")).Equals(("234dsfssdfs333324314")));
    }

}
