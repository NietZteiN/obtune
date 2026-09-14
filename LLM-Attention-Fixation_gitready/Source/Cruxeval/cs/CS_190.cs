using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string shortStr = "";
        foreach (char c in text)
        {
            if (char.IsLower(c))
            {
                shortStr += c;
            }
        }
        return shortStr;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("980jio80jic kld094398IIl ")).Equals(("jiojickldl")));
    }

}
