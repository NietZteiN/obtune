using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string symbols) {
        int count = 0;
        if (!string.IsNullOrEmpty(symbols)) {
            foreach (char symbol in symbols) {
                count++;
            }
            text = string.Concat(Enumerable.Repeat(text, count));
        }
        return text.PadLeft(text.Length + count * 2).Substring(0, text.Length + count * 2 - 2);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((""), ("BC1ty")).Equals(("        ")));
    }

}
