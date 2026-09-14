using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        var l = text.Split("0", 2);
        if (l[1] == "")
        {
            return "-1:-1";
        }
        return $"{l[0].Length}:{l[1].IndexOf('0') + 1}";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("qq0tt")).Equals(("2:0")));
    }

}
