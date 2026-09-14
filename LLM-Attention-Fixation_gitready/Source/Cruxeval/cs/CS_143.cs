using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string s, string n) {
        return string.Equals(s, n, StringComparison.OrdinalIgnoreCase);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("daaX"), ("daaX")) == (true));
    }

}
