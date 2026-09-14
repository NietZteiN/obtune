using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s, string c) {
        string[] words = s.Split(' ');
        Array.Reverse(words);
        return c + "  " + string.Join("  ", words);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Hello There"), ("*")).Equals(("*  There  Hello")));
    }

}
