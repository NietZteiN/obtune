using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s) {
        if (s.All(char.IsLetterOrDigit))
        {
            return "True";
        }
        return "False";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("777")).Equals(("True")));
    }

}
