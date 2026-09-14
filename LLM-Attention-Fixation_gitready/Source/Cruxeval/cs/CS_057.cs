using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        text = text.ToUpper();
        int countUpper = 0;
        foreach (char c in text)
        {
            if (char.IsUpper(c))
            {
                countUpper++;
            }
            else
            {
                return -1; // 'no' in Python is returned as -1 in C#
            }
        }
        return countUpper / 2;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ax")) == (1L));
    }

}
