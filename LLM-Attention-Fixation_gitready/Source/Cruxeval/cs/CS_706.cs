using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(string r, string w) {
        List<string> a = new List<string>();
        if (r[0] == w[0] && w[w.Length - 1] == r[r.Length - 1])
        {
            a.Add(r);
            a.Add(w);
        }
        else
        {
            a.Add(w);
            a.Add(r);
        }
        return a;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ab"), ("xy")).SequenceEqual((new List<string>(new string[]{(string)"xy", (string)"ab"}))));
    }

}
