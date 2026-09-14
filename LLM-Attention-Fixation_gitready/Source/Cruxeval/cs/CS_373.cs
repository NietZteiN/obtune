using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> orig) {
        List<long> copy = orig;
        copy.Add(100);
        orig.RemoveAt(orig.Count - 1);
        return copy;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)3L}))).SequenceEqual((new List<long>(new long[]{(long)1L, (long)2L, (long)3L}))));
    }

}
