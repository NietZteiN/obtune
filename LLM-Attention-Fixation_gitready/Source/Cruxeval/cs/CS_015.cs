using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string wrong, string right) {
        string new_text = text.Replace(wrong, right);
        return new_text.ToUpper();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("zn kgd jw lnt"), ("h"), ("u")).Equals(("ZN KGD JW LNT")));
    }

}
