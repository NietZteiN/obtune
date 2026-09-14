using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s) {
        if (s.All(char.IsLetter))
        {
            return "yes";
        }
        if (s == "")
        {
            return "str is empty";
        }
        return "no";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Boolean")).Equals(("yes")));
    }

}
