using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string t) {
        string[] parts = t.Split('-');
        string a = string.Join("-", parts.Take(parts.Length - 1));
        string sep = "-";
        string b = parts.Last();

        if (b.Length == a.Length)
        {
            return "imbalanced";
        }

        return a + b.Replace(sep, "");
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("fubarbaz")).Equals(("fubarbaz")));
    }

}
