using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(long n) {
        var b = n.ToString().ToCharArray().ToList();
        for (int i = 2; i < b.Count; i++)
        {
            b[i] += '+';
        }
        return b.Select(c => c.ToString()).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((44L)).SequenceEqual((new List<string>(new string[]{(string)"4", (string)"4"}))));
    }

}
