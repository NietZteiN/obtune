using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        return text.Count(char.IsDigit);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("so456")) == (3L));
    }

}
