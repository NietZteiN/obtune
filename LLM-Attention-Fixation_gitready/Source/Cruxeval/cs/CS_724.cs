using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(string text, string function) {
        List<long> cites = new List<long>() { text.Substring(text.IndexOf(function) + function.Length).Length };
        foreach (var charr in text)
        {
            if (charr.ToString() == function)
            {
                cites.Add(text.Substring(text.IndexOf(function) + function.Length).Length);
            }
        }
        return cites;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("010100"), ("010")).SequenceEqual((new List<long>(new long[]{(long)3L}))));
    }

}
