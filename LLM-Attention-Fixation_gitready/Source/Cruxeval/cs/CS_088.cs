using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s1, string s2) {
        if (s2.EndsWith(s1)) {
            s2 = s2.Substring(0, s2.Length - s1.Length);
        }
        return s2;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("he"), ("hello")).Equals(("hello")));
    }

}
