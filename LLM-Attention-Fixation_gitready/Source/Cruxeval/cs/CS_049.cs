using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        if (text.All(char.IsLetterOrDigit))
        {
            var digits = text.Where(char.IsDigit);
            return string.Concat(digits);
        }
        else
        {
            return string.Concat(text);
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("816")).Equals(("816")));
    }

}
