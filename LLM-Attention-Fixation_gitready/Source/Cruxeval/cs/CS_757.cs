using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Problem {
    public static string F(string text, string character, string replace) {
        return text.Replace(character, replace);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("a1a8"), ("1"), ("n2")).Equals(("an2a8")));
    }

}
