using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string str) {
        return System.Threading.Thread.CurrentThread.CurrentCulture.TextInfo.ToTitleCase(str).Replace(" ", "");
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("1oE-err bzz-bmm")).Equals(("1Oe-ErrBzz-Bmm")));
    }

}
