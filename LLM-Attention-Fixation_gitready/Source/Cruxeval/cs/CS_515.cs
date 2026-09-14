using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array) {
        List<long> result = new List<long>(array);
        result.Reverse();
        for (int i = 0; i < result.Count; i++)
        {
            result[i] = result[i] * 2;
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)3L, (long)4L, (long)5L}))).SequenceEqual((new List<long>(new long[]{(long)10L, (long)8L, (long)6L, (long)4L, (long)2L}))));
    }

}
