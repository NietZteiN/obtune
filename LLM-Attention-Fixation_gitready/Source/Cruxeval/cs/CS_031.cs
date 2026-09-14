using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string str) {
        int upper = 0;
        foreach (char c in str)
        {
            if (char.IsUpper(c))
            {
                upper++;
            }
        }
        return upper * (upper % 2 == 0 ? 2 : 1);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("PoIOarTvpoead")) == (8L));
    }

}
