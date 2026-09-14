using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> s) {
        while (s.Count > 1)
        {
            s.Clear();
            s.Add(s.Count);
        }
        return s.Last();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)6L, (long)1L, (long)2L, (long)3L}))) == (0L));
    }

}
