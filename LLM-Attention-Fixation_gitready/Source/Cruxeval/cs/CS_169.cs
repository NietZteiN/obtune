using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        List<char> ls = text.ToCharArray().ToList();
        int total = (text.Length - 1) * 2;
        for (int i = 1; i <= total; i++) {
            if (i % 2 == 1) {
                ls.Add('+');
            }
            else {
                ls.Insert(0, '+');
            }
        }
        return new string(ls.ToArray()).PadLeft(total);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("taole")).Equals(("++++taole++++")));
    }

}
