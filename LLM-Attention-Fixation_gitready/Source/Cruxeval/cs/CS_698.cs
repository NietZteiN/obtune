using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        var result = new StringBuilder();
        
        foreach (var c in text) {
            if (c != ')') {
                result.Append(c);
            }
        }
        
        return result.ToString();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("(((((((((((d))))))))).))))(((((")).Equals(("(((((((((((d.(((((")));
    }

}
