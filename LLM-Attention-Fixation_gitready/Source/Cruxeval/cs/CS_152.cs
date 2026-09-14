using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        long n = 0;
        foreach(var charac in text)
        {
            if (char.IsUpper(charac))
            {
                n += 1;
            }
        }
        return n;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("AAAAAAAAAAAAAAAAAAAA")) == (20L));
    }

}
