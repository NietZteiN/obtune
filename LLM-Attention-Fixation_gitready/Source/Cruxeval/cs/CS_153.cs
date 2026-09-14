using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static bool F(string text, string suffix, long num) {
        string strNum = num.ToString();
        return text.EndsWith(suffix + strNum);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("friends and love"), ("and"), (3L)) == (false));
    }

}
