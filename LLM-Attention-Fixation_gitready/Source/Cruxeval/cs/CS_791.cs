using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(long integer, long n) {
        long i = 1;
        string text = integer.ToString();
        while (i + text.Length < n) {
            i += text.Length;
        }
        return text.PadLeft((int)(i + text.Length), '0');
    }
    public static void Main(string[] args) {
    Debug.Assert(F((8999L), (2L)).Equals(("08999")));
    }

}
