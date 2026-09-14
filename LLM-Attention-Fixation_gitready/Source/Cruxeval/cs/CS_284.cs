using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string prefix) {
        int idx = 0;
        foreach (char letter in prefix) {
            if (text[idx] != letter) {
                return null;
            }
            idx++;
        }
        return text.Substring(idx);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("bestest"), ("bestest")).Equals(("")));
    }

}
