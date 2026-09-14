using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string s = text.ToLower();
        for (int i = 0; i < s.Length; i++) {
            if (s[i] == 'x') {
                return "no";
            }
        }
        return text.ToUpper();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("dEXE")).Equals(("no")));
    }

}
