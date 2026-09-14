using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        int n = text.IndexOf('8');
        return string.Join("", Enumerable.Repeat("x0", n));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("sa832d83r xd 8g 26a81xdf")).Equals(("x0x0")));
    }

}
