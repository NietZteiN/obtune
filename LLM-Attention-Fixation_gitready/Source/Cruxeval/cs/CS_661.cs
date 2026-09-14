using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string letters, long maxsplit) {
        return string.Join("", letters.Split().Skip(Math.Max(0, letters.Split().Count() - (int)maxsplit)));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("elrts,SS ee"), (6L)).Equals(("elrts,SSee")));
    }

}
