using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;

class Problem
{
    public static List<long> F(List<long> arr)
    {
        arr.Reverse();
        return arr;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)2L, (long)0L, (long)1L, (long)9999L, (long)3L, (long)-5L}))).SequenceEqual((new List<long>(new long[]{(long)-5L, (long)3L, (long)9999L, (long)1L, (long)0L, (long)2L}))));
    }

}
