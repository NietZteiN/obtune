using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s, string suffix) {
        if (string.IsNullOrEmpty(suffix)) {
            return s;
        }
        while (s.EndsWith(suffix)) {
            s = s.Substring(0, s.Length - suffix.Length);
        }
        return s;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ababa"), ("ab")).Equals(("ababa")));
    }

}
