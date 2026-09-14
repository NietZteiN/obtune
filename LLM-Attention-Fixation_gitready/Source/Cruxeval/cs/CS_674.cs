using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        var ls = text.ToCharArray().ToList();
        for (int x = ls.Count - 1; x >= 0; x--)
        {
            if (ls.Count <= 1) break;
            if (!"zyxwvutsrqponmlkjihgfedcba".Contains(ls[x])) ls.RemoveAt(x);
        }
        return string.Join("", ls);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("qq")).Equals(("qq")));
    }

}
