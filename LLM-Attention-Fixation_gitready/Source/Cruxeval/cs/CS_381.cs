using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long num_digits) {
        int width = Math.Max(1, (int)num_digits);
        return text.PadLeft(width, '0');
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("19"), (5L)).Equals(("00019")));
    }

}
