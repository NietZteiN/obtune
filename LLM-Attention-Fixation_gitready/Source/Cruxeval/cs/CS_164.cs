using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> lst) {
        lst.Sort();
        return lst.Take(3).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)5L, (long)8L, (long)1L, (long)3L, (long)0L}))).SequenceEqual((new List<long>(new long[]{(long)0L, (long)1L, (long)3L}))));
    }

}
