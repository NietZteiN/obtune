using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string a, string b) {
        text = text.Replace(a, b);
        return text.Replace(b, a);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((" vup a zwwo oihee amuwuuw! "), ("a"), ("u")).Equals((" vap a zwwo oihee amawaaw! ")));
    }

}
