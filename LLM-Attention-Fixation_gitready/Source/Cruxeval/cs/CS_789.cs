using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long n) {
        if (n < 0 || text.Length <= n) {
            return text;
        }

        string result = text.Substring(0, (int)n);
        int i = result.Length - 1;
        while (i >= 0) {
            if (result[i] != text[i]) {
                break;
            }
            i--;
        }
        return text.Substring(0, i + 1);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("bR"), (-1L)).Equals(("bR")));
    }

}
