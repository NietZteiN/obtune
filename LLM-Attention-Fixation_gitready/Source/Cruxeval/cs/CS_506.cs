using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(long n) {
        string p = "";
        if (n % 2 == 1) {
            p += "sn";
        } else {
            return (n * n).ToString();
        }
        for (long x = 1; x <= n; x++) {
            if (x % 2 == 0) {
                p += "to";
            } else {
                p += "ts";
            }
        }
        return p;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((1L)).Equals(("snts")));
    }

}
