using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string str, string substring) {
        while (str.StartsWith(substring))
        {
            str = str.Substring(substring.Length);
        }
        return str;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((""), ("A")).Equals(("")));
    }

}
