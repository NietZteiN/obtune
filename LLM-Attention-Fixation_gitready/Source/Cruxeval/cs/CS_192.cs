using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string suffix) {
        string output = text;
        while (text.EndsWith(suffix)) {
            output = text.Substring(0, text.Length - suffix.Length);
            text = output;
        }
        return output;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("!klcd!ma:ri"), ("!")).Equals(("!klcd!ma:ri")));
    }

}
