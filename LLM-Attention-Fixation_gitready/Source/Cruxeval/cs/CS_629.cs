using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string dng) {
        if (!text.Contains(dng)) {
            return text;
        }
        if (text.Substring(text.Length - dng.Length) == dng) {
            return text.Substring(0, text.Length - dng.Length);
        }
        return text.Substring(0, text.Length - 1) + F(text.Substring(0, text.Length - 2), dng);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("catNG"), ("NG")).Equals(("cat")));
    }

}
