using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        int length = text.Length / 2;
        string left_half = text.Substring(0, length);
        string right_half = new string(text.Substring(length).Reverse().ToArray());
        return left_half + right_half;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("n")).Equals(("n")));
    }

}
