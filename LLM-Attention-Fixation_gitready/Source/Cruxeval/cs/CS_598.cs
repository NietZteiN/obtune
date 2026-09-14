using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long n) {
        int length = text.Length;
        return text.Substring(length * ((int)n % 4), length - length * ((int)n % 4));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("abc"), (1L)).Equals(("")));
    }

}
