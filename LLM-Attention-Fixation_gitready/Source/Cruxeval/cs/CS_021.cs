using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array) {
        long n = array.Last();
        array.RemoveAt(array.Count - 1);
        array.Add(n);
        array.Add(n);
        return array;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)1L, (long)2L, (long)2L}))).SequenceEqual((new List<long>(new long[]{(long)1L, (long)1L, (long)2L, (long)2L, (long)2L}))));
    }

}
