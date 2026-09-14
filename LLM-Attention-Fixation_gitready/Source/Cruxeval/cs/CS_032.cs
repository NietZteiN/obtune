using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s, string sep) {
        var reverse = s.Split(sep).Select(e => '*' + e).ToArray();
        Array.Reverse(reverse);
        return string.Join(";", reverse);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("volume"), ("l")).Equals(("*ume;*vo")));
    }

}
