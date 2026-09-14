using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array, long n) {
        List<long> sublist = new List<long>();
        for (int i = (int)n; i < array.Count; i++)
        {
            sublist.Add(array[i]);
        }
        return sublist;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)0L, (long)0L, (long)1L, (long)2L, (long)2L, (long)2L, (long)2L})), (4L)).SequenceEqual((new List<long>(new long[]{(long)2L, (long)2L, (long)2L}))));
    }

}
