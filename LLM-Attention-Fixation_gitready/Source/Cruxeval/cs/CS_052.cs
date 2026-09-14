using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        List<char> a = new List<char>();
        for (int i = 0; i < text.Length; i++) {
            if (!char.IsDigit(text[i])) {
                a.Add(text[i]);
            }
        }
        return new string(a.ToArray());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("seiq7229 d27")).Equals(("seiq d")));
    }

}
