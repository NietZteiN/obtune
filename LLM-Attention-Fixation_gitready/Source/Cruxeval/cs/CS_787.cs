using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        if (text.Length == 0)
        {
            return "";
        }
        text = text.ToLower();
        return char.ToUpper(text[0]) + text.Substring(1);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("xzd")).Equals(("Xzd")));
    }

}
