using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        List<char> chars = new List<char>();
        foreach (char c in text)
        {
            if (char.IsDigit(c))
            {
                chars.Add(c);
            }
        }
        chars.Reverse();
        return string.Join("", chars);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("--4yrw 251-//4 6p")).Equals(("641524")));
    }

}
