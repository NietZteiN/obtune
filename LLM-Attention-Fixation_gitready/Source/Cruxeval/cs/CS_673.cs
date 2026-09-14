using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string str) {
        if (str.All(char.IsUpper))
        {
            return str.ToLower();
        }
        else if (str.All(char.IsLower))
        {
            return str.ToUpper();
        }
        return str;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("cA")).Equals(("cA")));
    }

}
