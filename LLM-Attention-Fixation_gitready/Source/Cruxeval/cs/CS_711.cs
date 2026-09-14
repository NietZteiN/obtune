using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        return text.Replace("\n", "\t");
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("apples\n	\npears\n	\nbananas")).Equals(("apples			pears			bananas")));
    }

}
