using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string value) {
        int length = text.Length;
        List<char> letters = text.ToCharArray().ToList();
        if (!letters.Contains(Convert.ToChar(value))) {
            value = letters[0].ToString();
        }
        return new string(value[0], length);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ldebgp o"), ("o")).Equals(("oooooooo")));
    }

}
