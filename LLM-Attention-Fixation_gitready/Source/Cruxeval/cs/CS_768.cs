using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s, string o) {
        if (s.StartsWith(o))
        {
            return s;
        }
        return o + F(s, new string(o.ToCharArray().Reverse().ToArray()).Substring(1));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("abba"), ("bab")).Equals(("bababba")));
    }

}
