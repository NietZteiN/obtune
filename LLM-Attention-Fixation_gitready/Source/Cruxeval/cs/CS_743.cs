using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        var strings = text.Split(',');
        return -(strings[0].Length + strings[1].Length);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("dog,cat")) == (-6L));
    }

}
