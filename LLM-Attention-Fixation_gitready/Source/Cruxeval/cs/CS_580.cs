using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(string text, string charString) {
        List<long> a = new List<long>();
        while (text.Contains(charString))
        {
            a.Add(text.IndexOf(charString));
            text = text.Remove(text.IndexOf(charString), 1);
        }
        return a;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("rvr"), ("r")).SequenceEqual((new List<long>(new long[]{(long)0L, (long)1L}))));
    }

}
