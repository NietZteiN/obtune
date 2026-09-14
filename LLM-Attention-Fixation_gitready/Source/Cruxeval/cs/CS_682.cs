using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long length, long index) {
        var ls = text.Split(new char[] { ' ' }, (int)index);
        return string.Join("_", ls.Select(l => l.Substring(0, (int)length)));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("hypernimovichyp"), (2L), (2L)).Equals(("hy")));
    }

}
