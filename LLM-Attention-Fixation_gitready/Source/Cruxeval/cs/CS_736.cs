using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string insert) {
        var whitespaces = new HashSet<char> {'\t', '\r', '\v', ' ', '\f', '\n'};
        var clean = "";
        foreach (var c in text) {
            if (whitespaces.Contains(c)) {
                clean += insert;
            } else {
                clean += c;
            }
        }
        return clean;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("pi wa"), ("chi")).Equals(("pichiwa")));
    }

}
