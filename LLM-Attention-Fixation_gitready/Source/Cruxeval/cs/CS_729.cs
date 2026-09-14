using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(string s1, string s2) {
        List<long> res = new List<long>();
        int i = s1.LastIndexOf(s2);
        while (i != -1)
        {
            res.Add(i+s2.Length-1);
            i = s1.LastIndexOf(s2, i);
        }
        return res;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("abcdefghabc"), ("abc")).SequenceEqual((new List<long>(new long[]{(long)10L, (long)2L}))));
    }

}
