using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(long single_digit) {
        List<long> result = new List<long>();
        for (long c = 1; c <= 10; c++)
        {
            if (c != single_digit)
            {
                result.Add(c);
            }
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((5L)).SequenceEqual((new List<long>(new long[]{(long)1L, (long)2L, (long)3L, (long)4L, (long)6L, (long)7L, (long)8L, (long)9L, (long)10L}))));
    }

}
