using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long m, long n) {
        text = text + text.Substring(0, (int)m) + text.Substring((int)n);
        string result = "";
        for (int i = (int)n; i < text.Length - (int)m; i++)
        {
            result = text[i] + result;
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("abcdefgabc"), (1L), (2L)).Equals(("bagfedcacbagfedc")));
    }

}
