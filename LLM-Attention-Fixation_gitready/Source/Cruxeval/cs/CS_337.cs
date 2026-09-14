using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string txt) {
        List<char> d = new List<char>();
        foreach (char c in txt)
        {
            if (char.IsDigit(c))
            {
                continue;
            }
            if (char.IsLower(c))
            {
                d.Add(char.ToUpper(c));
            }
            else if (char.IsUpper(c))
            {
                d.Add(char.ToLower(c));
            }
        }
        return new string(d.ToArray());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("5ll6")).Equals(("LL")));
    }

}
