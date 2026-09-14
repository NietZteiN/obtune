using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s, string x) {
        int count = 0;
        while (s.Substring(0, x.Length) == x && count < s.Length - x.Length)
        {
            s = s.Substring(x.Length);
            count += x.Length;
        }
        return s;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("If you want to live a happy life! Daniel"), ("Daniel")).Equals(("If you want to live a happy life! Daniel")));
    }

}
