using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string n, string s) {
        if (s.StartsWith(n))
        {
            var parts = s.Split(new string[] { n }, 2, StringSplitOptions.None);
            return parts[0] + n + s.Substring(n.Length);
        }
        return s;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("xqc"), ("mRcwVqXsRDRb")).Equals(("mRcwVqXsRDRb")));
    }

}
