using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s, long amount) {
        return new string('z', (int)(amount - s.Length)) + s;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("abc"), (8L)).Equals(("zzzzzabc")));
    }

}
