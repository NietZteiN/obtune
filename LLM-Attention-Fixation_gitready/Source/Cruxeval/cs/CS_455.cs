using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        int uppers = 0;
        foreach (char c in text)
        {
            if (char.IsUpper(c))
            {
                uppers++;
            }
        }
        return uppers >= 10 ? text.ToUpper() : text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("?XyZ")).Equals(("?XyZ")));
    }

}
