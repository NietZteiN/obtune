using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s, string ch) {
        string sl = s;
        if (s.Contains(ch)) {
            sl = sl.TrimStart(ch[0]);
            if (sl.Length == 0) {
                sl += "!?";
            }
        } else {
            return "no";
        }
        return sl;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("@@@ff"), ("@")).Equals(("ff")));
    }

}
