using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string s) {
        return s.Length == s.Count(c => c == '0') + s.Count(c => c == '1');
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("102")) == (false));
    }

}
