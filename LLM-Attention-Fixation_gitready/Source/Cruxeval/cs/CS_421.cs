using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s, long n) {
        if (s.Length < n)
        {
            return s;
        }
        else
        {
            return s.Substring((int)n);
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("try."), (5L)).Equals(("try.")));
    }

}
