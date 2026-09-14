using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> m) {
        m.Reverse();
        return m;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)-4L, (long)6L, (long)0L, (long)4L, (long)-7L, (long)2L, (long)-1L}))).SequenceEqual((new List<long>(new long[]{(long)-1L, (long)2L, (long)-7L, (long)4L, (long)0L, (long)6L, (long)-4L}))));
    }

}
