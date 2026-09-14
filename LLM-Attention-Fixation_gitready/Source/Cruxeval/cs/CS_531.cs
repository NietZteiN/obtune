using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string x) {
        if (text.Substring(0, x.Length) != x)
        {
            return F(text.Substring(1), x);
        }
        else
        {
            return text;
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Ibaskdjgblw asdl "), ("djgblw")).Equals(("djgblw asdl ")));
    }

}
