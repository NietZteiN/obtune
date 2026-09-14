using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string str, string c) {
        return str.EndsWith(c);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("wrsch)xjmb8"), ("c")) == (false));
    }

}
