using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string str) {
        if (string.IsNullOrEmpty(str) || !char.IsNumber(str[0])) {
            return "INVALID";
        }
        int cur = 0;
        foreach (char c in str) {
            cur = cur * 10 + (int)Char.GetNumericValue(c);
        }
        return cur.ToString();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("3")).Equals(("3")));
    }

}
