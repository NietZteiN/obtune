using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        if (text.All(char.IsDigit))
        {
            return "yes";
        }
        else
        {
            return "no";
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("abc")).Equals(("no")));
    }

}
