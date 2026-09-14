using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(string alphabet, string s) {
        List<string> a = new List<string>();
        foreach (char x in alphabet)
        {
            if (s.Contains(x.ToString().ToUpper()))
            {
                a.Add(x.ToString());
            }
        }
        if (s.ToUpper() == s)
        {
            a.Add("all_uppercased");
        }
        return a;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("abcdefghijklmnopqrstuvwxyz"), ("uppercased # % ^ @ ! vz.")).SequenceEqual((new List<string>())));
    }

}
