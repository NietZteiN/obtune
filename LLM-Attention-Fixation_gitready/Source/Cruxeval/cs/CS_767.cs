using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string[] a = text.Trim().Split(' ');
        for (int i = 0; i < a.Length; i++) {
            if (!int.TryParse(a[i], out _)) {
                return "-";
            }
        }
        return string.Join(" ", a);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("d khqw whi fwi bbn 41")).Equals(("-")));
    }

}
