using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Problem {
    public static string F(string text, string old, string newStr) {
        if (old.Length > 3) {
            return text;
        }
        if (text.Contains(old) && !text.Contains(" ")) {
            return text.Replace(old, new string(newStr[0], newStr.Length * old.Length));
        }
        while (text.Contains(old)) {
            text = text.Replace(old, newStr);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("avacado"), ("va"), ("-")).Equals(("a--cado")));
    }

}
