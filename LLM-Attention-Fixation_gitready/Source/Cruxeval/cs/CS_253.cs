using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string pref) {
        int length = pref.Length;
        if (pref == text.Substring(0, length)) {
            return text.Substring(length);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("kumwwfv"), ("k")).Equals(("umwwfv")));
    }

}
