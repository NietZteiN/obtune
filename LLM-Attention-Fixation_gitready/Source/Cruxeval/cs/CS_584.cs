using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string txt) {
        return string.Format(txt, Enumerable.Repeat("0", 20).ToArray());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("5123807309875480094949830")).Equals(("5123807309875480094949830")));
    }

}
