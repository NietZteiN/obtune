using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long n) {
        if (text.Length <= 2)
        {
            return text;
        }
        string leadingChars = new string(text[0], (int)(n - text.Length + 1));
        return leadingChars + text.Substring(1, text.Length - 2) + text[^1];
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("g"), (15L)).Equals(("g")));
    }

}
