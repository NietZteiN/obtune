using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string letters) {
        int count = 0;
        foreach (char l in letters)
        {
            if (char.IsDigit(l))
            {
                count++;
            }
        }
        return count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("dp ef1 gh2")) == (2L));
    }

}
