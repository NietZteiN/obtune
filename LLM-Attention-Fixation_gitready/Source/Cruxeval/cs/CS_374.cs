using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> seq, string v) {
        List<string> a = new List<string>();
        foreach(var i in seq)
        {
            if (i.EndsWith(v))
            {
                a.Add(i + i);
            }
        }
        return a;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"oH", (string)"ee", (string)"mb", (string)"deft", (string)"n", (string)"zz", (string)"f", (string)"abA"})), ("zz")).SequenceEqual((new List<string>(new string[]{(string)"zzzz"}))));
    }

}
