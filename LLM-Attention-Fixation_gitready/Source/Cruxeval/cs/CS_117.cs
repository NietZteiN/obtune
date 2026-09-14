using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string numbers) {
        for (int i = 0; i < numbers.Length; i++)
        {
            if (numbers.Count(c => c == '3') > 1)
            {
                return i;
            }
        }
        return -1;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("23157")) == (-1L));
    }

}
