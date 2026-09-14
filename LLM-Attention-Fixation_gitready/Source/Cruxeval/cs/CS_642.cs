using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        int i = 0;
        while (i < text.Length && char.IsWhiteSpace(text[i])) {
            i++;
        }
        if (i == text.Length) {
            return "space";
        }
        return "no";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("     ")).Equals(("space")));
    }

}
