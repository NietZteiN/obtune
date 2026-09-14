using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> arr) {
        int count = arr.Count;
        List<long> sub = new List<long>(arr);
        for (int i = 0; i < count; i += 2)
        {
            sub[i] *= 5;
        }
        return sub;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)-3L, (long)-6L, (long)2L, (long)7L}))).SequenceEqual((new List<long>(new long[]{(long)-15L, (long)-6L, (long)10L, (long)7L}))));
    }

}
