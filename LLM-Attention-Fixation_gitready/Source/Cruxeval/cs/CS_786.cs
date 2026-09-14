using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string letter) {
        if (text.Contains(letter)) {
            int start = text.IndexOf(letter);
            return text.Substring(start + 1) + text.Substring(0, start + 1);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("19kefp7"), ("9")).Equals(("kefp719")));
    }

}
