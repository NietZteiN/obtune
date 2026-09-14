using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string test_str) {
        string s = test_str.Replace('a', 'A');
        return s.Replace('e', 'A');
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("papera")).Equals(("pApArA")));
    }

}
