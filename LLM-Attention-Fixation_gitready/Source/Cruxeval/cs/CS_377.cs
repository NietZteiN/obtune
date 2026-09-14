using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        return string.Join(", ", text.Split(new[] { Environment.NewLine }, StringSplitOptions.None));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("BYE\nNO\nWAY")).Equals(("BYE, NO, WAY")));
    }

}
