using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s) {
        return string.Join("", s.Select(c => c.ToString().ToLower()));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("abcDEFGhIJ")).Equals(("abcdefghij")));
    }

}
