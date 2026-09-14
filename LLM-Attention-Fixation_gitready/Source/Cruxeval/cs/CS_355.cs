using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string prefix) {
        return text.Substring(prefix.Length);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("123x John z"), ("z")).Equals(("23x John z")));
    }

}
