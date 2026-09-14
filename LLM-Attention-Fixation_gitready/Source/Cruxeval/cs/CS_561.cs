using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text, string digit) {
        int count = text.Count(c => c.ToString() == digit);
        return int.Parse(digit) * count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("7Ljnw4Lj"), ("7")) == (7L));
    }

}
