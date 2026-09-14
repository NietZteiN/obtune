using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Problem {
    public static string F(string text, string old, string newStr) {
        string text2 = text.Replace(old, newStr);
        string old2 = new string(old.Reverse().ToArray());
        while (text2.Contains(old2)) {
            text2 = text2.Replace(old2, newStr);
        }
        return text2;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("some test string"), ("some"), ("any")).Equals(("any test string")));
    }

}
